"""
signals/kb_retriever.py
-----------------------
Phase 7: Converts mock KB entries into Signal objects.

Matching is deterministic keyword overlap — no randomness.
Confidence is derived from the entry's confidence_base scaled by match quality.
Returns up to 3 signals sorted by confidence descending.
"""
from __future__ import annotations

from typing import List

from uniguru.signals.mock_kb import MOCK_KB
from uniguru.signals.schema import CoreRequest, Signal

_TOP_N = 3


def _keyword_overlap(query_tokens: set[str], entry_keywords: List[str]) -> int:
    entry_tokens = {kw.lower() for kw in entry_keywords}
    return len(query_tokens & entry_tokens)


def retrieve_signals_from_kb(request: CoreRequest) -> List[Signal]:
    """
    Phase 7 entry point.
    Matches the CoreRequest context against the mock KB.
    Returns up to _TOP_N Signal objects, sorted by confidence descending.
    """
    query_tokens = set(request.context.lower().split())

    scored: List[tuple[float, dict]] = []
    for entry in MOCK_KB:
        overlap = _keyword_overlap(query_tokens, entry["keywords"])
        if overlap == 0:
            continue
        # Scale confidence: base * (overlap / total_keywords), capped at base
        scale = min(overlap / max(len(entry["keywords"]), 1), 1.0)
        confidence = round(entry["confidence_base"] * (0.6 + 0.4 * scale), 4)
        scored.append((confidence, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:_TOP_N]

    return [
        Signal(
            content=entry["content"],
            source=f"{entry['source']} [{entry['type']}]",
            confidence=conf,
            trace=f"kb_retriever → domain={entry['domain']} → title={entry['title']} → overlap={_keyword_overlap(query_tokens, entry['keywords'])}",
        )
        for conf, entry in top
    ]
