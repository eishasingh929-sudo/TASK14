function stripVerificationPrefix(answer) {
  if (!answer) {
    return "";
  }
  const patterns = [
    /^Based on verified source:[^\n]*\n\n/i,
    /^This information is partially verified from:[^\n]*\n\n/i,
    /^Verification status:[^\n]*\n\n/i,
  ];
  let text = String(answer);
  for (const pattern of patterns) {
    text = text.replace(pattern, "");
  }
  return text;
}

function normalizeText(text) {
  return String(text || "").replace(/\r/g, "").trim();
}

function truncateText(text, maxLength = 900) {
  const value = normalizeText(text);
  if (!value || value.length <= maxLength) {
    return value;
  }
  return `${value.slice(0, maxLength - 3).trim()}...`;
}

function parseSections(answer) {
  let body = normalizeText(answer);
  if (body.startsWith("Answer:")) {
    body = body.slice("Answer:".length).trim();
  }

  let details = "";
  let source = "";
  const detailsMarker = "\nDetails:\n";
  const sourceMarker = "\nSource:\n";
  const detailsIndex = body.indexOf(detailsMarker);
  const sourceIndex = body.indexOf(sourceMarker);

  if (detailsIndex >= 0 && (sourceIndex < 0 || detailsIndex < sourceIndex)) {
    details = body.slice(detailsIndex + detailsMarker.length, sourceIndex >= 0 ? sourceIndex : undefined).trim();
    body = body.slice(0, detailsIndex).trim();
  }

  if (sourceIndex >= 0) {
    source = normalizeText(answer).slice(normalizeText(answer).indexOf(sourceMarker) + sourceMarker.length).trim();
    if (!details && detailsIndex >= 0 && sourceIndex > detailsIndex) {
      details = body.slice(detailsIndex + detailsMarker.length).trim();
    }
  }

  return { body, details, source };
}

function compactKnowledgeAnswer(answer) {
  const noPrefix = stripVerificationPrefix(answer)
    .replace(/^UniGuru Deterministic Knowledge Retrieval:\s*/i, "")
    .replace(/\r/g, "")
    .replace(/\s+Content\s+/g, "\n\n")
    .replace(/\n{3,}/g, "\n\n");
  const lines = noPrefix
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
  const contentLines = [];
  const sourceLines = [];
  for (const line of lines) {
    if (/^source\(s\):/i.test(line)) {
      const sourcePayload = line.replace(/^source\(s\):\s*/i, "").trim();
      const embeddedContent = sourcePayload.match(/^(.*?\)\s+)([A-Z].+)$/);
      if (embeddedContent) {
        sourceLines.push(embeddedContent[1].trim());
        contentLines.push(embeddedContent[2].trim());
      } else {
        sourceLines.push(line);
      }
      continue;
    }
    if (/^(source\(s\):|source:|authors?:|year:|domain:|ingestion date:)/i.test(line)) {
      sourceLines.push(line);
      continue;
    }
    contentLines.push(line);
  }
  const collapsed = contentLines.join("\n");
  if (!collapsed || /^details:/i.test(collapsed)) {
    return {
      body: truncateText(noPrefix, 1000),
      source: sourceLines.join(" | "),
    };
  }
  if (contentLines.length <= 10 && collapsed.length <= 1000) {
    return {
      body: collapsed.trim(),
      source: sourceLines.join(" | "),
    };
  }
  const preview = contentLines.slice(0, 6).join("\n");
  return {
    body: `${preview}\n\n[Truncated for chat view. Full answer is available in raw_answer.]`,
    source: sourceLines.join(" | "),
  };
}

function buildPresentation(response, displayAnswer, fallbackSource = "") {
  const parsed = parseSections(displayAnswer);
  const paragraphs = parsed.body
    .split(/\n{2,}/)
    .map((item) => normalizeText(item))
    .filter(Boolean);
  const summary = truncateText(paragraphs[0] || parsed.body, 240);
  const bulletPoints = parsed.body
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => /^([-*]|\d+\.)\s+/.test(line))
    .map((line) => line.replace(/^([-*]|\d+\.)\s+/, ""));
  const disclaimer =
    response?.verification_status === "UNVERIFIED"
      ? "Unverified response. The UI should display a disclaimer."
      : response?.verification_status === "PARTIAL"
        ? "Partially verified response. The UI should keep the verification badge visible."
        : "";
  const source = normalizeText(parsed.source || fallbackSource);
  return {
    summary,
    body: truncateText(parsed.body, 1200),
    details: truncateText(parsed.details, 600),
    source,
    paragraphs: paragraphs.slice(0, 6),
    bullet_points: bulletPoints.slice(0, 6),
    disclaimer,
    fallback_mode: Boolean(response?.governance_flags?.fallback_mode),
  };
}

function buildIntegrationNotes(response) {
  const notes = [];
  const route = response?.routing?.route;
  const reason = String(response?.reason || "");
  if (route === "ROUTE_LLM" && reason.includes("UNIGURU_LLM_URL")) {
    notes.push("LLM fallback route selected, but UNIGURU_LLM_URL is not configured.");
  }
  if (route === "ROUTE_LLM" && reason.toLowerCase().includes("local ollama route returned an integration failure")) {
    notes.push("Primary LLM request failed and continuity fallback was used.");
  }
  if (response?.verification_status === "UNVERIFIED") {
    notes.push("Response is UNVERIFIED; consumer should show disclaimer.");
  }
  return notes;
}

export function buildSafeMiddlewareFallback({ query, reason, route = "ROUTE_LLM" }) {
  const normalizedQuery = String(query || "").trim();
  const lower = normalizedQuery.toLowerCase();
  let body = "Please ask a specific question and I will explain step by step.";
  let answerText = "";
  if (lower.includes("joke")) {
    body = "Here is one: Why did the function return early? It had a callback.";
  } else if (lower.includes("news") || lower.includes("current") || lower.includes("latest")) {
    body = "In demo safety mode I cannot fetch live feeds, but I can provide a general overview framework.";
  } else if (normalizedQuery) {
    body = `${normalizedQuery} can be explained through definition, context, and examples.`;
  }
  if (route === "ROUTE_LLM") {
    answerText = "System is temporarily busy. Please try again.";
  } else {
    answerText = `I am still learning this topic, but here is a basic explanation... ${body}`;
  }
  const fallback = {
    decision: "answer",
    answer: answerText,
    reason: reason || "Node middleware safe fallback activated.",
    verification_status: "UNVERIFIED",
    status_action: "ALLOW_WITH_DISCLAIMER",
    governance_flags: { fallback_mode: true },
    governance_output: {
      allowed: true,
      reason: "Middleware fallback mode active.",
      flags: { router_route: route },
    },
    routing: { route, query_type: "general_llm_query", router_latency_ms: 0 },
  };
  fallback.presentation = buildPresentation(fallback, fallback.answer, "Node middleware safe fallback");
  fallback.integration_notes = buildIntegrationNotes(fallback);
  return fallback;
}

export function formatEngineResponse(response) {
  if (!response || typeof response !== "object") {
    return response;
  }
  const normalized = { ...response };
  const answer = String(normalized.answer || "");
  const looksLikeKbDump = answer.includes("UniGuru Deterministic Knowledge Retrieval:") || answer.includes("Source(s):");
  let displayAnswer = answer;
  let fallbackSource = "";
  if (looksLikeKbDump) {
    normalized.raw_answer = answer;
    const compacted = compactKnowledgeAnswer(answer);
    displayAnswer = compacted.body;
    fallbackSource = compacted.source;
    normalized.answer = displayAnswer;
  }
  const notes = buildIntegrationNotes(normalized);
  if (notes.length > 0) {
    normalized.integration_notes = notes;
  }
  normalized.presentation = buildPresentation(normalized, displayAnswer, fallbackSource);
  return normalized;
}
