"""
signals/pipeline.py
-------------------
Signal pipeline orchestrator.

Execution order (matches task phases):
  Phase 1  — build_core_request        (request_builder)
  Phase 2  — generate_mock_signals      (mock_generator)
  Phase 6  — simulate_external_call     (external_stub)
  Phase 7  — retrieve_signals_from_kb   (kb_retriever)
  Phase 3  — aggregate_signals          (aggregator)  ← includes Phase 8 guardrails
  Phase 4  — build_final_response       (response_builder)
  Phase 5  — log_query                  (bucket_logger)  ← always in finally block

Entry point: run_signal_pipeline(query) → dict
The dict is the full structured response suitable for the /ask/signal endpoint.
"""
from __future__ import annotations

import time
from typing import Any, Dict

from uniguru.signals.aggregator import aggregate_signals
from uniguru.signals.bucket_logger import log_query
from uniguru.signals.external_stub import simulate_external_call
from uniguru.signals.guardrails import SignalValidationError
from uniguru.signals.kb_retriever import retrieve_signals_from_kb
from uniguru.signals.mock_generator import generate_mock_signals
from uniguru.signals.request_builder import build_core_request
from uniguru.signals.response_builder import build_final_response
from uniguru.signals.schema import FinalResponse, Signal

_SYSTEM_PATH = "request_builder > mock_generator > external_stub > kb_retriever > aggregator > response_builder > bucket_logger"


def run_signal_pipeline(query: str) -> Dict[str, Any]:
    """
    Full signal pipeline for a single query.
    Always returns a structured dict — never raises to the caller.
    Logging always executes via the finally block.
    """
    started = time.perf_counter()
    response: FinalResponse | None = None
    degradation_flag = False
    log_entry = None

    try:
        # Phase 1 — structured request
        core_request = build_core_request(query)

        # Phase 2 — mock signals
        mock_signals = generate_mock_signals(core_request)

        # Phase 6 — external stub signal
        external_signal = simulate_external_call(query)

        # Phase 7 — KB signals
        kb_signals = retrieve_signals_from_kb(core_request)

        # Combine all signal sources
        all_signals: list[Signal] = mock_signals + [external_signal] + kb_signals

        # Phase 3 + Phase 8 — aggregate (guardrails run inside)
        aggregated = aggregate_signals(all_signals)
        degradation_flag = aggregated.degradation_flag

        # Phase 4 — final response
        response = build_final_response(aggregated)

    except SignalValidationError as exc:
        # Structural signal failure — surface explicitly, no silent fallback
        response = FinalResponse(
            final_answer=f"[SIGNAL VALIDATION FAILURE] {exc}",
            supporting_signals=[],
            confidence=0.0,
            reasoning_trace=[
                "Step 1: Signal validation error detected.",
                f"Step 2: Error detail — {exc}",
                "Step 3: Pipeline halted. No answer produced.",
            ],
        )
        degradation_flag = True

    except Exception as exc:
        response = FinalResponse(
            final_answer=f"[PIPELINE ERROR] {exc}",
            supporting_signals=[],
            confidence=0.0,
            reasoning_trace=[
                "Step 1: Unexpected pipeline error.",
                f"Step 2: Error — {exc}",
            ],
        )
        degradation_flag = True

    finally:
        # Phase 5 — logging always executes
        if response is not None:
            log_entry = log_query(
                query=query,
                response=response,
                system_path=_SYSTEM_PATH,
                degradation_flag=degradation_flag,
            )

    latency_ms = round((time.perf_counter() - started) * 1000, 3)

    return {
        "request_id": core_request.request_id if "core_request" in dir() else "unknown",
        "intent": core_request.intent if "core_request" in dir() else "unknown",
        "required_outputs": core_request.required_outputs if "core_request" in dir() else [],
        "final_answer": response.final_answer,
        "supporting_signals": [
            {
                "content": s.content,
                "source": s.source,
                "confidence": s.confidence,
                "trace": s.trace,
            }
            for s in response.supporting_signals
        ],
        "confidence": response.confidence,
        "reasoning_trace": response.reasoning_trace,
        "degradation_flag": degradation_flag,
        "event_id": log_entry.event_id if log_entry else None,
        "latency_ms": latency_ms,
    }
