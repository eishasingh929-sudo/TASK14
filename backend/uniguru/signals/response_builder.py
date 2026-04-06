"""
signals/response_builder.py
---------------------------
Phase 4: Final response builder.

Rules:
  - final_answer is derived ONLY from signal content — no raw query echoing.
  - reasoning_trace is a list of short steps, NOT paragraphs.
  - confidence is the mean of top signal confidences (deterministic).
  - If degradation_flag is set, final_answer reflects degraded state explicitly.
"""
from __future__ import annotations

from typing import List

from uniguru.signals.schema import AggregatedResult, FinalResponse, Signal

_DEGRADED_ANSWER = (
    "[DEGRADED] All available signals fell below the confidence threshold. "
    "No reliable answer can be constructed from current signal sources."
)


def _compute_confidence(signals: List[Signal]) -> float:
    if not signals:
        return 0.0
    return round(sum(s.confidence for s in signals) / len(signals), 4)


def _build_answer(signals: List[Signal]) -> str:
    """
    Combine top signal contents into a single answer string.
    Uses the highest-confidence signal as the primary answer,
    then appends supporting content from remaining signals.
    """
    if not signals:
        return _DEGRADED_ANSWER

    primary = signals[0].content
    if len(signals) == 1:
        return primary

    supporting_parts = " | ".join(s.content for s in signals[1:])
    return f"{primary} [Supporting: {supporting_parts}]"


def _build_reasoning_trace(
    signals: List[Signal],
    degradation_flag: bool,
) -> List[str]:
    """Returns a list of short step strings — never paragraphs."""
    steps: List[str] = [
        f"Step 1: Received {len(signals)} signal(s) after aggregation and filtering.",
    ]
    for i, signal in enumerate(signals, start=2):
        steps.append(
            f"Step {i}: Signal from '{signal.source}' — confidence={signal.confidence} — {signal.trace}"
        )
    next_step = len(signals) + 2
    if degradation_flag:
        steps.append(f"Step {next_step}: degradation_flag=True — all signals were weak.")
    else:
        steps.append(
            f"Step {next_step}: Final answer constructed from top {len(signals)} signal(s)."
        )
    return steps


def build_final_response(aggregated: AggregatedResult) -> FinalResponse:
    """
    Phase 4 entry point.
    Converts an AggregatedResult into a FinalResponse.
    """
    signals = aggregated.signals

    if aggregated.degradation_flag or not signals:
        return FinalResponse(
            final_answer=_DEGRADED_ANSWER,
            supporting_signals=[],
            confidence=0.0,
            reasoning_trace=_build_reasoning_trace([], degradation_flag=True),
        )

    return FinalResponse(
        final_answer=_build_answer(signals),
        supporting_signals=signals,
        confidence=_compute_confidence(signals),
        reasoning_trace=_build_reasoning_trace(signals, degradation_flag=False),
    )
