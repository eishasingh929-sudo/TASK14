from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import requests


ROOT = Path(__file__).resolve().parents[1]
PYTHON_PORT = int(os.getenv("UNIGURU_PYTHON_PORT", "8000"))
NODE_PORT = int(os.getenv("UNIGURU_NODE_PORT", "3000"))
PYTHON_BASE = f"http://127.0.0.1:{PYTHON_PORT}"
NODE_BASE = f"http://127.0.0.1:{NODE_PORT}"
OUTPUT_JSON = ROOT / "demo_logs" / "final_validation_live.json"
OUTPUT_MD = ROOT / "docs" / "reports" / "FINAL_VALIDATION_LIVE.md"
LIVE_TOKEN = os.getenv("UNIGURU_API_TOKEN", "uniguru-live-validation-token")


def _wait_for_health(url: str, timeout_seconds: int = 45) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(0.5)
    raise RuntimeError(f"Service did not become healthy in time: {url}")


def _stop(proc: subprocess.Popen[Any]) -> None:
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


def _start_stack() -> tuple[subprocess.Popen[Any], subprocess.Popen[Any]]:
    env_backend = os.environ.copy()
    env_backend["PYTHONPATH"] = str(ROOT / "backend")
    env_backend["UNIGURU_HOST"] = "127.0.0.1"
    env_backend["UNIGURU_PORT"] = str(PYTHON_PORT)
    env_backend["UNIGURU_API_AUTH_REQUIRED"] = "true"
    env_backend["UNIGURU_API_TOKEN"] = LIVE_TOKEN
    env_backend["UNIGURU_LLM_URL"] = env_backend.get("UNIGURU_LLM_URL", "http://127.0.0.1:11434/api/generate")
    env_backend["UNIGURU_LLM_MODEL"] = env_backend.get("UNIGURU_LLM_MODEL", "gpt-oss:120b-cloud")
    env_backend["UNIGURU_LLM_TIMEOUT_SECONDS"] = env_backend.get("UNIGURU_LLM_TIMEOUT_SECONDS", "12")
    env_backend["UNIGURU_ALLOWED_CALLERS"] = (
        "bhiv-assistant,gurukul-platform,samachar-platform,internal-testing,uniguru-frontend"
    )
    backend_proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "uniguru.service.api:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(PYTHON_PORT),
        ],
        cwd=str(ROOT),
        env=env_backend,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    env_node = os.environ.copy()
    env_node["NODE_BACKEND_PORT"] = str(NODE_PORT)
    env_node["UNIGURU_ASK_URL"] = f"{PYTHON_BASE}/ask"
    env_node["UNIGURU_API_TOKEN"] = LIVE_TOKEN
    env_node["UNIGURU_REQUEST_TIMEOUT_MS"] = env_node.get("UNIGURU_REQUEST_TIMEOUT_MS", "25000")
    node_proc = subprocess.Popen(
        ["node", "src/server.js"],
        cwd=str(ROOT / "node-backend"),
        env=env_node,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    _wait_for_health(f"{PYTHON_BASE}/health")
    _wait_for_health(f"{NODE_BASE}/health")
    return backend_proc, node_proc


def _cases() -> List[Dict[str, Any]]:
    return [
        {"id": "01", "bucket": "KB", "query": "What is a qubit?", "expected_routes": ["ROUTE_UNIGURU"]},
        {"id": "02", "bucket": "KB", "query": "Explain quantum entanglement.", "expected_routes": ["ROUTE_UNIGURU"]},
        {"id": "03", "bucket": "KB", "query": "What is Grover's algorithm?", "expected_routes": ["ROUTE_UNIGURU"]},
        {"id": "04", "bucket": "KB", "query": "What is Shor's algorithm used for?", "expected_routes": ["ROUTE_UNIGURU"]},
        {"id": "05", "bucket": "KB", "query": "Who is Mahavira?", "expected_routes": ["ROUTE_UNIGURU", "ROUTE_LLM"]},
        {"id": "06", "bucket": "KB", "query": "Explain ahimsa in Jainism.", "expected_routes": ["ROUTE_UNIGURU", "ROUTE_LLM"]},
        {"id": "07", "bucket": "KB", "query": "What is Swamini Vato?", "expected_routes": ["ROUTE_UNIGURU"]},
        {"id": "08", "bucket": "KB", "query": "Explain Vachanamrut core teachings.", "expected_routes": ["ROUTE_UNIGURU"]},
        {"id": "09", "bucket": "KB", "query": "Explain Nyaya logic.", "expected_routes": ["ROUTE_UNIGURU"]},
        {"id": "10", "bucket": "KB", "query": "What is Vedic math?", "expected_routes": ["ROUTE_UNIGURU"]},
        {"id": "11", "bucket": "KB", "query": "Explain university admission basics.", "expected_routes": ["ROUTE_UNIGURU"]},
        {"id": "12", "bucket": "KB", "query": "What happens in a counseling round?", "expected_routes": ["ROUTE_UNIGURU", "ROUTE_LLM"]},
        {"id": "13", "bucket": "KB", "query": "How does placement support work?", "expected_routes": ["ROUTE_UNIGURU"]},
        {"id": "14", "bucket": "KB", "query": "How should I prepare a resume for placements?", "expected_routes": ["ROUTE_UNIGURU", "ROUTE_LLM"]},
        {"id": "15", "bucket": "General", "query": "hello there", "expected_routes": ["ROUTE_LLM"]},
        {"id": "16", "bucket": "General", "query": "Explain Python list comprehension in simple words.", "expected_routes": ["ROUTE_LLM"]},
        {"id": "17", "bucket": "General", "query": "Tell me a short joke.", "expected_routes": ["ROUTE_LLM"]},
        {"id": "18", "bucket": "General", "query": "Give me a latest world news summary.", "expected_routes": ["ROUTE_LLM"]},
        {"id": "19", "bucket": "General", "query": "What is the capital of France?", "expected_routes": ["ROUTE_LLM"]},
        {"id": "20", "bucket": "General", "query": "Explain recursion in easy words.", "expected_routes": ["ROUTE_LLM"]},
        {"id": "21", "bucket": "General", "query": "Summarize cloud computing for beginners.", "expected_routes": ["ROUTE_LLM"]},
        {"id": "22", "bucket": "General", "query": "What is photosynthesis?", "expected_routes": ["ROUTE_LLM"]},
        {"id": "23", "bucket": "Workflow", "query": "create workflow ticket for NIC demo rehearsal", "expected_routes": ["ROUTE_WORKFLOW"]},
        {"id": "24", "bucket": "Workflow", "query": "schedule workflow job for health check", "expected_routes": ["ROUTE_WORKFLOW"]},
        {"id": "25", "bucket": "System", "query": "sudo rm -rf /", "expected_routes": ["ROUTE_SYSTEM"]},
        {"id": "26", "bucket": "System", "query": "restart systemctl nginx", "expected_routes": ["ROUTE_SYSTEM"]},
        {"id": "27", "bucket": "Random", "query": "asdkjh qweoiu zmxn", "expected_routes": ["ROUTE_LLM"]},
        {"id": "28", "bucket": "Random", "query": "!!??###", "expected_routes": ["ROUTE_LLM"]},
        {"id": "29", "bucket": "Random", "query": "Can you help me understand study planning?", "expected_routes": ["ROUTE_LLM"]},
        {"id": "30", "bucket": "Random", "query": "What is quantum biology?", "expected_routes": ["ROUTE_UNIGURU", "ROUTE_LLM"]},
    ]


def _run_case(case: Dict[str, Any]) -> Dict[str, Any]:
    started = time.perf_counter()
    response = requests.post(
        f"{NODE_BASE}/api/v1/chat/query",
        json={
            "query": case["query"],
            "session_id": f"live-validation-{case['id']}",
            "context": {"caller": "bhiv-assistant", "channel": "final-validation-live"},
        },
        timeout=35,
    )
    latency_ms = round((time.perf_counter() - started) * 1000, 3)
    payload = response.json()
    data = payload.get("data", {}) if isinstance(payload, dict) else {}
    answer = str(data.get("answer") or "").strip()
    route = str((data.get("routing") or {}).get("route") or "")
    expected_routes = list(case.get("expected_routes") or [])
    route_ok = True if not expected_routes else route in expected_routes
    passed = response.status_code == 200 and bool(answer) and route_ok
    return {
        "id": case["id"],
        "bucket": case["bucket"],
        "query": case["query"],
        "expected_routes": expected_routes,
        "status_code": response.status_code,
        "route": route,
        "route_ok": route_ok,
        "decision": data.get("decision"),
        "verification_status": data.get("verification_status"),
        "source": payload.get("source"),
        "degraded": bool(payload.get("degraded", False)),
        "has_answer": bool(answer),
        "answer_preview": answer[:240],
        "latency_ms": latency_ms,
        "passed": passed,
    }


def _write_markdown(payload: Dict[str, Any]) -> None:
    lines = [
        "# Final Validation - Live 30 Queries",
        "",
        f"Execution date (UTC): {payload['timestamp_utc']}",
        "",
        "## Summary",
        f"- Total queries: {payload['total_queries']}",
        f"- Passed: {payload['passed_queries']}",
        f"- Failed: {payload['failed_queries']}",
        f"- Zero failures: {payload['zero_failures']}",
        f"- Zero empty responses: {payload['zero_empty_responses']}",
        f"- Max latency ms: {payload['max_latency_ms']}",
        "",
        "## Route Distribution",
    ]
    for route, count in sorted(payload["route_counts"].items()):
        lines.append(f"- {route}: {count}")
    lines.extend(
        [
            "",
            "## Result Grid",
            "| ID | Bucket | Status | Route | Latency ms | Query |",
            "|---|---|---|---|---:|---|",
        ]
    )
    for item in payload["results"]:
        status = "PASS" if item["passed"] else "FAIL"
        lines.append(
            f"| {item['id']} | {item['bucket']} | {status} | {item['route']} | {item['latency_ms']} | {item['query']} |"
        )
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    backend_proc: subprocess.Popen[Any] | None = None
    node_proc: subprocess.Popen[Any] | None = None

    try:
        backend_proc, node_proc = _start_stack()
        health = requests.get(f"{PYTHON_BASE}/health", timeout=10).json()
        cases = _cases()
        results = [_run_case(case) for case in cases]

        route_counts: Dict[str, int] = {}
        for item in results:
            route = item.get("route") or "UNKNOWN"
            route_counts[route] = route_counts.get(route, 0) + 1

        passed_queries = sum(1 for item in results if item["passed"])
        failed_queries = len(results) - passed_queries
        zero_empty = all(bool(item["has_answer"]) for item in results)
        max_latency_ms = max(float(item["latency_ms"]) for item in results) if results else 0.0
        payload = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "total_queries": len(results),
            "concurrency": 1,
            "passed_queries": passed_queries,
            "failed_queries": failed_queries,
            "zero_failures": failed_queries == 0,
            "zero_empty_responses": zero_empty,
            "max_latency_ms": round(max_latency_ms, 3),
            "route_counts": route_counts,
            "health_snapshot": health,
            "results": results,
        }
        OUTPUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        _write_markdown(payload)
        print(str(OUTPUT_JSON))
    finally:
        if node_proc is not None:
            _stop(node_proc)
        if backend_proc is not None:
            _stop(backend_proc)


if __name__ == "__main__":
    main()
