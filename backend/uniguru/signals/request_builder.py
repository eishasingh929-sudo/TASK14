"""
signals/request_builder.py
--------------------------
Phase 1: Convert any incoming query into a CoreRequest.

Intent classification is deterministic keyword-based — no ML, no randomness.
Real intent classifiers can replace _classify_intent() without changing the
rest of the pipeline.
"""
from __future__ import annotations

import hashlib
from typing import List

from uniguru.signals.schema import CoreRequest

# ---------------------------------------------------------------------------
# Intent → required_outputs mapping (placeholder — swap for real taxonomy)
# ---------------------------------------------------------------------------
_INTENT_OUTPUTS: dict[str, List[str]] = {
    "knowledge_query":   ["definition", "explanation", "source_citation"],
    "admission_query":   ["eligibility", "process_steps", "document_list"],
    "placement_query":   ["preparation_tips", "resume_advice", "timeline"],
    "general_chat":      ["conversational_reply"],
    "system_command":    ["policy_block"],
    "workflow_request":  ["task_delegation", "confirmation"],
    "unknown":           ["best_effort_answer"],
}

_KNOWLEDGE_KEYWORDS = {
    "qubit", "quantum", "entanglement", "superposition", "grover", "shor",
    "mahavira", "jain", "ahimsa", "swaminarayan", "vachanamrut", "nyaya",
    "vedic", "algorithm", "physics", "biology", "chemistry",
}
_ADMISSION_KEYWORDS = {"admission", "counseling", "merit", "seat", "document", "eligibility"}
_PLACEMENT_KEYWORDS = {"placement", "resume", "interview", "career", "referral", "portfolio", "linkedin"}
_SYSTEM_KEYWORDS    = {"sudo", "rm -rf", "shutdown", "format", "systemctl", "powershell"}
_WORKFLOW_KEYWORDS  = {"create ticket", "schedule", "approve", "trigger workflow", "start workflow"}
_CHAT_KEYWORDS      = {"hello", "hi", "hey", "joke", "how are you"}


def _classify_intent(query: str) -> str:
    lower = query.lower()
    if any(kw in lower for kw in _SYSTEM_KEYWORDS):
        return "system_command"
    if any(kw in lower for kw in _WORKFLOW_KEYWORDS):
        return "workflow_request"
    if any(kw in lower for kw in _CHAT_KEYWORDS):
        return "general_chat"
    if any(kw in lower for kw in _KNOWLEDGE_KEYWORDS):
        return "knowledge_query"
    if any(kw in lower for kw in _ADMISSION_KEYWORDS):
        return "admission_query"
    if any(kw in lower for kw in _PLACEMENT_KEYWORDS):
        return "placement_query"
    return "unknown"


def _stable_request_id(query: str) -> str:
    """Deterministic ID — same query always produces the same ID."""
    return "req-" + hashlib.sha256(query.encode()).hexdigest()[:16]


def build_core_request(query: str) -> CoreRequest:
    """
    Phase 1 entry point.
    Returns a CoreRequest for any non-empty query string.
    """
    clean = query.strip()
    intent = _classify_intent(clean)
    return CoreRequest(
        request_id=_stable_request_id(clean),
        intent=intent,
        context=clean,
        required_outputs=_INTENT_OUTPUTS.get(intent, _INTENT_OUTPUTS["unknown"]),
    )
