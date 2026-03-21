from __future__ import annotations

import json
import os
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


NODE_BASE_URL = os.getenv("UNIGURU_NODE_BASE_URL", "http://127.0.0.1:8080").rstrip("/")
PYTHON_BASE_URL = os.getenv("UNIGURU_PYTHON_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
CALLER = os.getenv("UNIGURU_CALLER", "bhiv-assistant")
OUTPUT_PATH = Path(os.getenv("UNIGURU_PHASE8_OUTPUT", "demo_logs/phase8_test_outputs.json"))


def _get_json(url: str) -> Dict[str, Any]:
    request = urllib.request.Request(url=url, method="GET")
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _post_json(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    request = urllib.request.Request(
        url=url,
        method="POST",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload).encode("utf-8"),
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def run_phase8_queries() -> List[Dict[str, Any]]:
    cases = [
        ("Knowledge query", "What is a qubit?"),
        ("Religious query", "Who is Mahavira?"),
        ("General query", "What is Python?"),
        ("Random query", "What is happening in the world?"),
        ("Invalid query", "sudo rm -rf"),
    ]
    results: List[Dict[str, Any]] = []

    for name, query in cases:
        started = time.perf_counter()
        response = _post_json(
            f"{NODE_BASE_URL}/api/v1/chat/query",
            {"query": query, "context": {"caller": CALLER, "channel": "phase8-check"}},
        )
        latency_ms = (time.perf_counter() - started) * 1000
        data = response.get("data", {})
        routing = data.get("routing") or {}
        results.append(
            {
                "name": name,
                "query": query,
                "latency_ms": round(latency_ms, 3),
                "success": response.get("success"),
                "degraded": response.get("degraded"),
                "decision": data.get("decision"),
                "verification_status": data.get("verification_status"),
                "route": routing.get("route"),
                "answer": data.get("answer"),
                "reason": data.get("reason"),
            }
        )

    return results


def main() -> None:
    output = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python_health": _get_json(f"{PYTHON_BASE_URL}/health"),
        "python_ready": _get_json(f"{PYTHON_BASE_URL}/ready"),
        "node_health": _get_json(f"{NODE_BASE_URL}/health"),
        "test_results": run_phase8_queries(),
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(str(OUTPUT_PATH))


if __name__ == "__main__":
    main()
