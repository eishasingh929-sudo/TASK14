"""
signals/bucket_logger.py
------------------------
Phase 5: Bucket logging.

Appends one BucketLogEntry per query to a local JSON-lines file.
Logging ALWAYS executes — it is called in a finally block in the pipeline.
Failures are reported to stderr but never suppress the response.

Log file location: demo_logs/signal_bucket_log.jsonl
Each line is a valid JSON object (JSON-lines format for easy streaming/parsing).
"""
from __future__ import annotations

import json
import os
import sys
import time
import uuid
from typing import Optional

from uniguru.signals.schema import BucketLogEntry, FinalResponse

_LOG_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "demo_logs")
)
_LOG_FILE = os.path.join(_LOG_DIR, "signal_bucket_log.jsonl")


def _entry_to_dict(entry: BucketLogEntry) -> dict:
    return {
        "event_id": entry.event_id,
        "query": entry.query,
        "signals_used": entry.signals_used,
        "final_answer": entry.final_answer,
        "confidence": entry.confidence,
        "system_path": entry.system_path,
        "degradation_flag": entry.degradation_flag,
        "logged_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def log_query(
    *,
    query: str,
    response: FinalResponse,
    system_path: str,
    degradation_flag: bool,
) -> BucketLogEntry:
    """
    Phase 5 entry point.
    Builds a BucketLogEntry and appends it to the log file.
    Always executes — never raises to the caller.
    Returns the entry so the pipeline can include it in the API response.
    """
    entry = BucketLogEntry(
        event_id=str(uuid.uuid4()),
        query=query,
        signals_used=[s.source for s in response.supporting_signals],
        final_answer=response.final_answer,
        confidence=response.confidence,
        system_path=system_path,
        degradation_flag=degradation_flag,
    )

    try:
        os.makedirs(_LOG_DIR, exist_ok=True)
        with open(_LOG_FILE, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(_entry_to_dict(entry), ensure_ascii=False) + "\n")
    except OSError as exc:
        print(f"[bucket_logger] WARNING: could not write log entry: {exc}", file=sys.stderr)

    return entry
