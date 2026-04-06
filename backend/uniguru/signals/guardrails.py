"""
signals/guardrails.py
---------------------
Phase 8: Signal validation and degradation detection.

Rules:
  - Reject any signal missing source, confidence, or trace.
  - Reject any signal with confidence outside [0.0, 1.0].
  - Set degradation_flag=True if ALL remaining signals have confidence < 0.5.
  - No silent fallback: raises SignalValidationError on structural violations.
"""
from __future__ import annotations

from typing import List, Tuple

from uniguru.signals.schema import AggregatedResult, Signal

_CONFIDENCE_THRESHOLD = 0.5


class SignalValidationError(ValueError):
    """Raised when a signal fails structural validation."""


def _validate_signal(signal: Signal) -> None:
    """Raises SignalValidationError if the signal is structurally invalid."""
    if not signal.source or not str(signal.source).strip():
        raise SignalValidationError(f"Signal missing 'source': {signal!r}")
    if signal.confidence is None:
        raise SignalValidationError(f"Signal missing 'confidence': {signal!r}")
    if not (0.0 <= signal.confidence <= 1.0):
        raise SignalValidationError(
            f"Signal confidence {signal.confidence} out of range [0,1]: {signal!r}"
        )
    if not signal.trace or not str(signal.trace).strip():
        raise SignalValidationError(f"Signal missing 'trace': {signal!r}")


def validate_and_flag(signals: List[Signal]) -> AggregatedResult:
    """
    Phase 8 entry point.
    Validates each signal structurally, then sets degradation_flag if all
    signals are weak (confidence < 0.5).

    Returns an AggregatedResult with the validated signal list and flag.
    Raises SignalValidationError immediately on any structural violation.
    """
    for signal in signals:
        _validate_signal(signal)

    degradation_flag = bool(signals) and all(
        s.confidence < _CONFIDENCE_THRESHOLD for s in signals
    )

    return AggregatedResult(signals=signals, degradation_flag=degradation_flag)
