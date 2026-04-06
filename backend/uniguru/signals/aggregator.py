"""
signals/aggregator.py
---------------------
Phase 3: Signal aggregation engine.

Steps (in order):
  1. Validate all signals via guardrails (Phase 8).
  2. Filter out signals with confidence < MIN_CONFIDENCE.
  3. Sort remaining signals by confidence descending (stable sort — deterministic).
  4. Keep top MAX_SIGNALS.
  5. Return AggregatedResult with degradation_flag if all signals were weak.

No randomness. Same input always produces same output.
"""
from __future__ import annotations

from typing import List

from uniguru.signals.guardrails import validate_and_flag
from uniguru.signals.schema import AggregatedResult, Signal

MIN_CONFIDENCE = 0.5
MAX_SIGNALS = 5


def aggregate_signals(raw_signals: List[Signal]) -> AggregatedResult:
    """
    Phase 3 entry point.
    Accepts a flat list of signals from all sources (KB + mock + external).
    Returns a validated, ranked, filtered AggregatedResult.
    """
    # Phase 8 validation — raises SignalValidationError on structural failure
    validated = validate_and_flag(raw_signals)

    # Filter weak signals
    strong = [s for s in validated.signals if s.confidence >= MIN_CONFIDENCE]

    # Stable sort descending by confidence, then by source name for tie-breaking
    strong.sort(key=lambda s: (-s.confidence, s.source))

    # Cap at MAX_SIGNALS
    top = strong[:MAX_SIGNALS]

    # degradation_flag: true if nothing survived the filter
    degradation_flag = len(top) == 0

    return AggregatedResult(signals=top, degradation_flag=degradation_flag)
