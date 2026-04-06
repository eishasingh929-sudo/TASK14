"""
signals/mock_generator.py
-------------------------
Phase 2: Mock signal generator.

Produces 2–4 placeholder signals per query.
Output is deterministic — same query always returns the same signals.
Signal count is derived from query length (no randomness).

In production, replace this with real signal sources (LLM, retrieval, etc.)
without changing the return type List[Signal].
"""
from __future__ import annotations

import hashlib
from typing import List

from uniguru.signals.schema import CoreRequest, Signal

_MOCK_SIGNAL_TEMPLATES = [
    {
        "content": "[MOCK SIGNAL A] Placeholder primary knowledge signal for intent: {intent}.",
        "source": "MockGenerator-Primary",
        "confidence": 0.82,
        "trace": "mock_generator → slot=A → intent={intent}",
    },
    {
        "content": "[MOCK SIGNAL B] Placeholder secondary context signal. Query fingerprint: {fp}.",
        "source": "MockGenerator-Secondary",
        "confidence": 0.71,
        "trace": "mock_generator → slot=B → fingerprint={fp}",
    },
    {
        "content": "[MOCK SIGNAL C] Placeholder domain signal for domain: {domain}.",
        "source": "MockGenerator-Domain",
        "confidence": 0.65,
        "trace": "mock_generator → slot=C → domain={domain}",
    },
    {
        "content": "[MOCK SIGNAL D] Placeholder low-confidence supplementary signal.",
        "source": "MockGenerator-Supplementary",
        "confidence": 0.48,   # intentionally below 0.5 to test filtering
        "trace": "mock_generator → slot=D → supplementary=true",
    },
]

_DOMAIN_MAP = {
    "knowledge_query":  "knowledge",
    "admission_query":  "admissions",
    "placement_query":  "placement",
    "general_chat":     "general",
    "system_command":   "system",
    "workflow_request": "workflow",
    "unknown":          "general",
}


def _signal_count(query: str) -> int:
    """Deterministic count 2–4 based on query length."""
    length = len(query.strip())
    if length < 20:
        return 2
    if length < 60:
        return 3
    return 4


def generate_mock_signals(request: CoreRequest) -> List[Signal]:
    """
    Phase 2 entry point.
    Returns 2–4 deterministic placeholder signals for the given CoreRequest.
    """
    fp = hashlib.sha256(request.context.encode()).hexdigest()[:8]
    domain = _DOMAIN_MAP.get(request.intent, "general")
    count = _signal_count(request.context)

    signals: List[Signal] = []
    for template in _MOCK_SIGNAL_TEMPLATES[:count]:
        signals.append(
            Signal(
                content=template["content"].format(intent=request.intent, fp=fp, domain=domain),
                source=template["source"],
                confidence=template["confidence"],
                trace=template["trace"].format(intent=request.intent, fp=fp, domain=domain),
            )
        )
    return signals
