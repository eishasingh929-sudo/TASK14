import express from "express";

import { buildSafeMiddlewareFallback, formatEngineResponse } from "../services/responseFormatter.js";
import { buildUniGuruAskRequest, callUniGuruAsk, UNIGURU_ASK_URL } from "../services/uniguruClient.js";

const router = express.Router();

function parseContext(rawContext) {
  if (!rawContext || typeof rawContext !== "object" || Array.isArray(rawContext)) {
    return {};
  }
  return { ...rawContext };
}

function resolveCaller(context, fallbackCaller) {
  const preferred = String(context?.caller || "").trim();
  return preferred || fallbackCaller;
}

router.get("/health", (_req, res) => {
  res.status(200).json({
    status: "ok",
    service: "node-backend",
    uniguru_target: UNIGURU_ASK_URL,
  });
});

router.get("/health/integration", (_req, res) => {
  res.status(200).json({
    status: "ok",
    service: "node-backend",
    checks: {
      uniguru_ask_url_configured: Boolean(String(process.env.UNIGURU_ASK_URL || "").trim()),
      uniguru_api_token_configured: Boolean(String(process.env.UNIGURU_API_TOKEN || "").trim()),
    },
  });
});

router.get("/ready", (_req, res) => {
  res.status(200).json({
    status: "ready",
    service: "node-backend",
    checks: {
      middleware_running: true,
      ask_route_target: UNIGURU_ASK_URL,
    },
  });
});

router.post("/api/v1/chat/query", async (req, res) => {
  const query = req.body?.query ?? req.body?.message;
  const sessionId = req.body?.session_id ?? req.body?.sessionId ?? null;
  try {
    const allowWeb = Boolean(req.body?.allow_web ?? req.body?.allowWeb ?? false);
    const context = parseContext(req.body?.context);
    const caller = resolveCaller(context, "uniguru-frontend");

    const payload = buildUniGuruAskRequest({
      query,
      caller,
      sessionId,
      allowWeb,
      context,
    });

    const engineResponse = formatEngineResponse(await callUniGuruAsk(payload));
    res.status(200).json({
      success: true,
      source: "uniguru-api",
      data: engineResponse,
    });
  } catch (error) {
    res.status(200).json({
      success: true,
      degraded: true,
      source: "node-backend-safe-fallback",
      data: buildSafeMiddlewareFallback({
        query,
        reason: `Upstream /ask unavailable: ${error.message}`,
      }),
      session_id: sessionId,
    });
  }
});

router.post("/api/v1/samachar/query", async (req, res) => {
  const query = req.body?.query ?? req.body?.headline ?? req.body?.message;
  const sessionId = req.body?.session_id ?? req.body?.sessionId ?? null;
  try {
    const allowWeb = Boolean(req.body?.allow_web ?? req.body?.allowWeb ?? false);
    const context = parseContext(req.body?.context);
    const caller = resolveCaller(context, "samachar-platform");

    const payload = buildUniGuruAskRequest({
      query,
      caller,
      sessionId,
      allowWeb,
      context: {
        ...context,
        channel: context.channel || "samachar",
      },
    });

    const engineResponse = formatEngineResponse(await callUniGuruAsk(payload));
    res.status(200).json({
      success: true,
      integration: "samachar",
      source: "uniguru-api",
      data: engineResponse,
    });
  } catch (error) {
    res.status(200).json({
      success: true,
      degraded: true,
      integration: "samachar",
      source: "node-backend-safe-fallback",
      data: buildSafeMiddlewareFallback({
        query,
        reason: `Upstream /ask unavailable: ${error.message}`,
      }),
      session_id: sessionId,
    });
  }
});

router.post("/api/v1/gurukul/query", async (req, res) => {
  const query = req.body?.query ?? req.body?.student_query;
  const studentId = req.body?.student_id ? String(req.body.student_id) : "";
  const sessionId = req.body?.session_id ?? req.body?.sessionId ?? null;
  try {
    const allowWeb = Boolean(req.body?.allow_web ?? req.body?.allowWeb ?? false);
    const context = parseContext(req.body?.context);
    const caller = resolveCaller(context, "gurukul-platform");

    const payload = buildUniGuruAskRequest({
      query,
      caller,
      sessionId,
      allowWeb,
      context: {
        ...context,
        student_id: studentId || undefined,
      },
    });

    const engineResponse = formatEngineResponse(await callUniGuruAsk(payload));
    res.status(200).json({
      success: true,
      integration: "gurukul",
      student_id: studentId || null,
      source: "uniguru-api",
      data: engineResponse,
    });
  } catch (error) {
    res.status(200).json({
      success: true,
      degraded: true,
      integration: "gurukul",
      student_id: studentId || null,
      source: "node-backend-safe-fallback",
      data: buildSafeMiddlewareFallback({
        query,
        reason: `Upstream /ask unavailable: ${error.message}`,
      }),
      session_id: sessionId,
    });
  }
});

export default router;
