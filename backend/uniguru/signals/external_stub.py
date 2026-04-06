"""
signals/external_stub.py
------------------------
Phase 6: Mock external system call.

simulate_external_call() returns a single placeholder Signal.
In production, replace the body with a real HTTP call to an external API.
The return type (Signal) and function signature must not change.
"""
from __future__ import annotations

import hashlib

from uniguru.signals.schema import Signal

_EXTERNAL_SOURCE = "ExternalStub-v1 [mock]"


def simulate_external_call(query: str) -> Signal:
    """
    Phase 6 entry point.
    Returns a deterministic placeholder signal for any query.
    Confidence is fixed at 0.55 — above the filter threshold but clearly external.
    """
    query_hash = hashlib.sha256(query.encode()).hexdigest()[:8]
    return Signal(
        content=f"[EXTERNAL PLACEHOLDER] No real external data. Query fingerprint: {query_hash}.",
        source=_EXTERNAL_SOURCE,
        confidence=0.55,
        trace=f"external_stub → query_hash={query_hash} → mock_response=true",
    )
