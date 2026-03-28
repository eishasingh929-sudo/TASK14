from __future__ import annotations

import re
import os
from typing import Any, Dict, Optional

from uniguru.enforcement.enforcement import UniGuruEnforcement
from uniguru.governance.output_guard import OutputGovernanceGuard
from uniguru.ontology.registry import OntologyRegistry
from uniguru.reasoning.concept_resolver import ConceptResolver
from uniguru.reasoning.graph_reasoner import GraphReasoner
from uniguru.reasoning.reasoning_trace import ReasoningTraceGenerator
from uniguru.retrieval.retriever import retrieve_knowledge_with_trace
from uniguru.retrieval.web_retriever import web_retrieve
from uniguru.service.governance_preflight import GovernancePreflight
from uniguru.service.response_format import build_structured_answer
from uniguru.verifier.source_verifier import SourceVerifier


UNKNOWN_MESSAGE = "I do not have verified knowledge to answer this question."
UNVERIFIED_REFUSAL = "I cannot verify this information from current knowledge."
MAX_KB_RESPONSE_CHARS = 2000


def _clean_kb_content(raw_content: str) -> str:
    text = str(raw_content or "").replace("\ufeff", "").replace("\r", "")
    text = re.sub(r"^---[\s\S]*?---\n*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"\$(.*?)\$", r"\1", text)
    text = re.sub(r"`{1,3}", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(text) <= MAX_KB_RESPONSE_CHARS:
        return text
    shortened = text[:MAX_KB_RESPONSE_CHARS].rsplit(" ", 1)[0].strip()
    return f"{shortened}\n\n[Content trimmed for readability.]"


def _summarize_kb_content(raw_content: str, *, max_chars: int = 420) -> str:
    cleaned = _clean_kb_content(raw_content)
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    if not lines:
        return "I will help you with this. Please try again."

    candidate_lines = []
    for line in lines:
        lowered = line.lower()
        if re.match(r"^(title|source(?:\(s\))?|authors?|year|domain|ingestion date|citations?)\s*:", lowered):
            continue
        if lowered in {"definitions", "key concepts", "concept explanations", "light equation context"}:
            continue
        candidate_lines.append(line)

    selected = candidate_lines if candidate_lines else lines
    summary = " ".join(selected[:3]).strip()
    if len(summary) <= max_chars:
        return summary
    shortened = summary[:max_chars].rsplit(" ", 1)[0].strip()
    return f"{shortened}..."


def _format_kb_answer(raw_content: str, trace: Dict[str, Any]) -> str:
    source_parts = [
        str(trace.get("source_title") or "").strip(),
        str(trace.get("kb_file_path") or trace.get("kb_file") or "").strip(),
    ]
    return build_structured_answer(
        answer=_summarize_kb_content(raw_content),
        details=f"Matched keyword: {trace.get('matched_keyword')}" if trace.get("matched_keyword") else None,
        source=" | ".join(part for part in source_parts if part) or None,
    )


class LiveUniGuruService:
    """Canonical deterministic KB engine used behind the router."""

    def __init__(self):
        self.enforcement = UniGuruEnforcement()
        self.ontology_registry = OntologyRegistry()
        self.concept_resolver = ConceptResolver()
        self.graph_reasoner = GraphReasoner()
        self.output_guard = OutputGovernanceGuard()
        self.preflight = GovernancePreflight()
        self.kb_confidence_threshold = float(os.getenv("UNIGURU_KB_CONFIDENCE_THRESHOLD", "0.25"))

    def preflight_response(
        self,
        *,
        user_query: str,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        decision = self.preflight.evaluate(query=user_query, context=context)
        if decision is None:
            return None
        return self._finalize_decision(decision=decision, session_id=session_id)

    def ask(
        self,
        user_query: str,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        allow_web_retrieval: bool = False,
    ) -> Dict[str, Any]:
        metadata = dict(context or {})
        if not metadata.get("preflight_checked"):
            preflight_response = self.preflight_response(
                user_query=user_query,
                session_id=session_id,
                context=metadata,
            )
            if preflight_response is not None:
                return preflight_response

        decision = self._resolve_with_kb(user_query)
        if decision is None:
            if allow_web_retrieval:
                decision = self._resolve_with_web(query=user_query)
            else:
                decision = self._resolve_unknown()

        return self._finalize_decision(decision=decision, session_id=session_id)

    def _resolve_with_kb(self, query: str) -> Optional[Dict[str, Any]]:
        kb_content, trace = retrieve_knowledge_with_trace(query)
        confidence = float(trace.get("confidence", 0.0) or 0.0)
        if not kb_content or confidence < self.kb_confidence_threshold:
            return None

        verification = SourceVerifier.verify_retrieval_trace(trace=trace, min_confidence=self.kb_confidence_threshold)
        is_verified = verification.get("truth_declaration") in {"VERIFIED", "VERIFIED_PARTIAL"}
        response_content = _format_kb_answer(kb_content, trace) if is_verified else UNVERIFIED_REFUSAL
        return {
            "decision": "answer" if is_verified else "block",
            "reason": "Knowledge found in the canonical KB and verified."
            if is_verified
            else "Knowledge found but failed verification gate.",
            "data": {
                "response_content": response_content,
                "retrieval_trace": trace,
                "verification": verification,
            },
        }

    def _resolve_unknown(self) -> Dict[str, Any]:
        return {
            "decision": "block",
            "reason": "No verified KB response and web retrieval is disabled.",
            "data": {
                "response_content": build_structured_answer(
                    answer=UNKNOWN_MESSAGE,
                    details="No verified match was found in the canonical UniGuru knowledge layer.",
                    source="UniGuru canonical KB",
                ),
                "verification": {
                    "truth_declaration": "UNVERIFIED",
                    "verification_status": "UNVERIFIED",
                    "formatted_response": UNVERIFIED_REFUSAL,
                    "source_name": "UniGuru canonical KB",
                },
            },
        }

    def _resolve_with_web(self, query: str) -> Dict[str, Any]:
        web_result = web_retrieve(query)
        data: Dict[str, Any] = {}

        status = str(web_result.get("verification_status") or "UNVERIFIED").upper()
        allowed = bool(web_result.get("allowed"))
        if allowed and status in {"VERIFIED", "PARTIAL"}:
            concept_resolution = self.concept_resolver.resolve(query=query, retrieval_trace=None)
            reasoning_path = self.graph_reasoner.reasoning_path_from_domain_root(
                concept_id=concept_resolution["concept_id"],
                domain=concept_resolution["domain"],
            )
            data["concept_resolution"] = concept_resolution
            data["reasoning_path"] = reasoning_path
            data["reasoning_trace"] = ReasoningTraceGenerator.from_reasoning_path(
                reasoning_path=reasoning_path,
                snapshot_version=concept_resolution["snapshot_version"],
                snapshot_hash=concept_resolution["snapshot_hash"],
            )
            data["retrieval_trace"] = {
                "engine": "WebRetriever_v1",
                "match_found": True,
                "confidence": 1.0 if status == "VERIFIED" else 0.6,
                "kb_file": None,
                "sources_consulted": [
                    concept_resolution["domain"],
                    "web",
                    "ontology_registry",
                    "ontology_graph",
                ],
                "web_source": web_result.get("source"),
            }
            data["web_source"] = {
                "url": web_result.get("source"),
                "title": web_result.get("source_title"),
            }
            truth_decl = "VERIFIED" if status == "VERIFIED" else "VERIFIED_PARTIAL"
            data["verification"] = {
                "truth_declaration": truth_decl,
                "verification_status": status,
                "formatted_response": web_result.get("truth_declaration"),
                "source_name": web_result.get("source_title") or web_result.get("source"),
            }
            data["response_content"] = build_structured_answer(
                answer=str(web_result.get("answer") or ""),
                details=f"Verified web retrieval returned status {status}.",
                source=web_result.get("source_title") or web_result.get("source"),
            )
            return {
                "decision": "answer",
                "reason": f"Verified web retrieval succeeded with status {status}.",
                "ontology_reference": self.ontology_registry.build_reference(
                    decision="answer",
                    trace=data.get("retrieval_trace"),
                    resolved_concept=concept_resolution,
                    reasoning_path=reasoning_path,
                ),
                "data": data,
            }

        data["web_source"] = {
            "url": web_result.get("source"),
            "title": web_result.get("source_title"),
        }
        data["verification"] = {
            "truth_declaration": "UNVERIFIED",
            "verification_status": "UNVERIFIED",
            "formatted_response": UNVERIFIED_REFUSAL,
            "source_name": web_result.get("source_title") or "Unverified web source",
        }
        data["response_content"] = UNVERIFIED_REFUSAL
        return {
            "decision": "block",
            "reason": "Information retrieved but not verified.",
            "data": data,
        }

    def _finalize_decision(self, *, decision: Dict[str, Any], session_id: Optional[str]) -> Dict[str, Any]:
        self._attach_reasoning_trace(decision)
        self._apply_output_governance(decision)
        sealed = self.enforcement.validate_and_bind(decision)
        return self._build_contract_response(sealed, session_id=session_id)

    def _apply_output_governance(self, decision: Dict[str, Any]) -> None:
        data = decision.setdefault("data", {})
        response_content = str(data.get("response_content") or "").strip()
        if response_content and not response_content.startswith("Answer:") and not response_content.startswith("Verification status:"):
            data["response_content"] = build_structured_answer(answer=response_content)
            response_content = data["response_content"]

        result = self.output_guard.evaluate(response_content)
        decision["governance_output"] = {
            "allowed": result.allowed,
            "reason": result.reason,
            "flags": result.flags,
        }
        decision.setdefault("governance_flags", {}).update(result.flags)

        if result.allowed:
            return

        decision["decision"] = "block"
        decision["reason"] = result.reason
        data["response_content"] = UNVERIFIED_REFUSAL
        data["verification"] = {
            "truth_declaration": "UNVERIFIED",
            "verification_status": "UNVERIFIED",
            "formatted_response": UNVERIFIED_REFUSAL,
            "source_name": "Output Governance",
        }

    def _attach_reasoning_trace(self, decision: Dict[str, Any]) -> None:
        data = decision.get("data", {})
        retrieval_trace = data.get("retrieval_trace") or {}
        verification = data.get("verification") or {}
        ontology_reference = decision.get("ontology_reference") or self.ontology_registry.default_reference()

        sources_consulted = list(retrieval_trace.get("sources_consulted") or [])
        trace_entries = data.get("trace") or []
        if trace_entries:
            sources_consulted.extend(entry.get("rule", "") for entry in trace_entries if entry.get("rule"))
        sources_consulted.extend(["ontology_registry", "ontology_graph"])
        web_source = data.get("web_source") or {}
        if web_source.get("url"):
            sources_consulted.append(web_source["url"])
        sources_consulted = [item for item in dict.fromkeys(sources_consulted) if item]

        decision["reasoning_trace"] = {
            "sources_consulted": sources_consulted,
            "retrieval_confidence": float(retrieval_trace.get("confidence", 0.0) or 0.0),
            "ontology_domain": ontology_reference.get("domain", "core"),
            "verification_status": verification.get("verification_status") or self._derive_verification_status(decision),
            "verification_details": verification.get("truth_declaration", "UNVERIFIED"),
        }

        if "ontology_reference" not in decision:
            concept_resolution = data.get("concept_resolution")
            reasoning_path = data.get("reasoning_path") or []
            decision["ontology_reference"] = self.ontology_registry.build_reference(
                decision=decision.get("decision", "block"),
                trace=retrieval_trace,
                resolved_concept=concept_resolution,
                reasoning_path=reasoning_path,
            )

    @staticmethod
    def _derive_verification_status(decision: Dict[str, Any]) -> str:
        verification = (decision.get("data") or {}).get("verification") or {}
        truth_decl = str(verification.get("truth_declaration") or "")
        if truth_decl == "VERIFIED":
            return "VERIFIED"
        if truth_decl == "VERIFIED_PARTIAL":
            return "PARTIAL"
        return "UNVERIFIED"

    def _build_contract_response(self, sealed: Dict[str, Any], session_id: Optional[str]) -> Dict[str, Any]:
        ontology_reference = sealed.get("ontology_reference") or self.ontology_registry.default_reference()
        data = sealed.get("data", {})
        reasoning_trace = sealed.get("reasoning_trace") or {}
        return {
            "decision": sealed.get("decision"),
            "answer": data.get("response_content"),
            "session_id": session_id,
            "reason": sealed.get("reason"),
            "ontology_reference": {
                "concept_id": ontology_reference.get("concept_id"),
                "domain": ontology_reference.get("domain"),
                "snapshot_version": ontology_reference.get("snapshot_version"),
                "snapshot_hash": ontology_reference.get("snapshot_hash"),
                "truth_level": ontology_reference.get("truth_level"),
            },
            "reasoning_trace": reasoning_trace,
            "governance_flags": sealed.get("governance_flags", {}),
            "governance_output": sealed.get("governance_output", {}),
            "verification_status": sealed.get("verification_status"),
            "status_action": sealed.get("status_action"),
            "enforcement_signature": sealed.get("enforcement_signature"),
            "request_id": sealed.get("request_id"),
            "sealed_at": sealed.get("sealed_at"),
            "latency_ms": sealed.get("total_latency_ms", 0.0),
        }
