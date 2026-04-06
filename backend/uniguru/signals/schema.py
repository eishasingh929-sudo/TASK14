"""
signals/schema.py
-----------------
Canonical dataclasses for every object that flows through the signal pipeline.
All phases import from here — nothing defines its own shape elsewhere.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class CoreRequest:
    """Phase 1 — structured request derived from a raw query."""
    request_id: str
    intent: str
    context: str
    required_outputs: List[str]


@dataclass(frozen=True)
class Signal:
    """Phase 2 — atomic unit of knowledge produced by any source."""
    content: str
    source: str
    confidence: float   # 0.0 – 1.0
    trace: str


@dataclass(frozen=True)
class AggregatedResult:
    """Phase 3 — ranked, filtered, combined signals."""
    signals: List[Signal]
    degradation_flag: bool


@dataclass(frozen=True)
class FinalResponse:
    """Phase 4 — structured output derived entirely from signals."""
    final_answer: str
    supporting_signals: List[Signal]
    confidence: float
    reasoning_trace: List[str]


@dataclass
class BucketLogEntry:
    """Phase 5 — immutable audit record written for every query."""
    event_id: str
    query: str
    signals_used: List[str]          # signal source labels
    final_answer: str
    confidence: float
    system_path: str
    degradation_flag: bool = False
