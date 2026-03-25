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
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from uniguru.runtime_env import load_project_env

PYTHON_PORT = int(os.getenv("UNIGURU_PYTHON_PORT", "8000"))
NODE_PORT = int(os.getenv("UNIGURU_NODE_PORT", "8080"))
PYTHON_BASE = f"http://127.0.0.1:{PYTHON_PORT}"
NODE_BASE = f"http://127.0.0.1:{NODE_PORT}"
OUTPUT_JSON = ROOT / "demo_logs" / "final_validation_20_queries.json"
OUTPUT_MD = ROOT / "docs" / "reports" / "FINAL_VALIDATION_20_QUERIES.md"


load_project_env()


def _wait_for_health(url: str, timeout_seconds: int = 40) -> None:
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
    env_backend["UNIGURU_API_AUTH_REQUIRED"] = "false"
    env_backend["UNIGURU_LLM_URL"] = env_backend.get("UNIGURU_LLM_URL", "http://127.0.0.1:11434/api/generate")
    env_backend["UNIGURU_LLM_MODEL"] = env_backend.get("UNIGURU_LLM_MODEL", "gpt-oss:120b-cloud")
    env_backend["UNIGURU_LLM_TIMEOUT_SECONDS"] = env_backend.get("UNIGURU_LLM_TIMEOUT_SECONDS", "60")
    env_backend["UNIGURU_ALLOWED_CALLERS"] = (
        "bhiv-assistant,gurukul-platform,internal-testing,uniguru-frontend"
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


def _run_case(case: Dict[str, Any]) -> Dict[str, Any]:
    started = time.perf_counter()
    response = requests.post(
        f"{NODE_BASE}/api/v1/chat/query",
        json={
            "query": case["query"],
            "session_id": f"final-20-{case['id']}",
            "context": {"caller": "bhiv-assistant", "channel": "final-validation-20"},
        },
        timeout=30,
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
        "query": case["query"],
        "bucket": case["bucket"],
        "expected_routes": expected_routes,
        "status_code": response.status_code,
        "route": route,
        "decision": data.get("decision"),
        "verification_status": data.get("verification_status"),
        "has_answer": bool(answer),
        "answer_preview": answer[:220],
        "latency_ms": latency_ms,
        "passed": passed,
    }


def _build_cases() -> List[Dict[str, Any]]:
    return [
        {"id": "01", "bucket": "KB", "query": "What is a qubit?", "expected_routes": ["ROUTE_UNIGURU"]},
        {"id": "02", "bucket": "KB", "query": "Explain quantum entanglement.", "expected_routes": ["ROUTE_UNIGURU"]},
        {"id": "03", "bucket": "KB", "query": "Who is Mahavira?", "expected_routes": ["ROUTE_UNIGURU"]},
        {"id": "04", "bucket": "KB", "query": "Explain ahimsa in Jainism.", "expected_routes": ["ROUTE_UNIGURU", "ROUTE_LLM"]},
        {"id": "05", "bucket": "KB", "query": "What is Swamini Vato?", "expected_routes": ["ROUTE_UNIGURU"]},
        {"id": "06", "bucket": "KB", "query": "Explain Nyaya logic.", "expected_routes": ["ROUTE_UNIGURU"]},
        {"id": "07", "bucket": "KB", "query": "What is Vedic math?", "expected_routes": ["ROUTE_UNIGURU"]},
        {"id": "08", "bucket": "KB", "query": "Explain university admission basics.", "expected_routes": ["ROUTE_UNIGURU"]},
        {"id": "09", "bucket": "KB", "query": "How does placement support work?", "expected_routes": ["ROUTE_UNIGURU"]},
        {"id": "10", "bucket": "General", "query": "hello there", "expected_routes": ["ROUTE_LLM"]},
        {"id": "11", "bucket": "General", "query": "Explain Python list comprehension in simple words.", "expected_routes": ["ROUTE_LLM"]},
        {"id": "12", "bucket": "General", "query": "Tell me a short joke.", "expected_routes": ["ROUTE_LLM"]},
        {"id": "13", "bucket": "General", "query": "Give me a latest world news summary.", "expected_routes": ["ROUTE_LLM"]},
        {"id": "14", "bucket": "General", "query": "What is the capital of France?", "expected_routes": ["ROUTE_LLM"]},
        {"id": "15", "bucket": "Random", "query": "asdkjh qweoiu zmxn", "expected_routes": ["ROUTE_LLM"]},
        {"id": "16", "bucket": "Random", "query": "!!??###", "expected_routes": ["ROUTE_LLM"]},
        {"id": "17", "bucket": "Random", "query": "create workflow ticket for demo rehearsal", "expected_routes": ["ROUTE_WORKFLOW"]},
        {"id": "18", "bucket": "Random", "query": "sudo rm -rf /", "expected_routes": ["ROUTE_SYSTEM"]},
        {"id": "19", "bucket": "Random", "query": "How should I prepare a resume for placements?", "expected_routes": ["ROUTE_UNIGURU", "ROUTE_LLM"]},
        {"id": "20", "bucket": "Random", "query": "What is counseling round in admissions?", "expected_routes": ["ROUTE_UNIGURU", "ROUTE_LLM"]},
    ]


def _write_markdown(payload: Dict[str, Any]) -> None:
    lines = [
        "# Final Validation - 20 Queries",
        "",
        f"Execution date (UTC): {payload['timestamp_utc']}",
        "",
        "## Summary",
        f"- Total queries: {payload['total_queries']}",
        f"- Passed: {payload['passed_queries']}",
        f"- Failed: {payload['failed_queries']}",
        f"- Any 503 observed: {payload['any_503_observed']}",
        f"- No empty responses: {payload['no_empty_responses']}",
        "",
        "## Route Distribution",
    ]
    for route, count in sorted(payload["route_counts"].items()):
        lines.append(f"- {route}: {count}")
    lines.append("")
    lines.append("## Result Grid")
    lines.append("| ID | Bucket | Status | Route | Query |")
    lines.append("|---|---|---|---|---|")
    for item in payload["results"]:
        status = "PASS" if item["passed"] else "FAIL"
        lines.append(f"| {item['id']} | {item['bucket']} | {status} | {item['route']} | {item['query']} |")

    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    backend_proc: subprocess.Popen[Any] | None = None
    node_proc: subprocess.Popen[Any] | None = None

    try:
        backend_proc, node_proc = _start_stack()
        cases = _build_cases()
        results = [_run_case(case) for case in cases]
        route_counts: Dict[str, int] = {}
        for item in results:
            route = item.get("route") or "UNKNOWN"
            route_counts[route] = route_counts.get(route, 0) + 1

        passed_queries = sum(1 for item in results if item["passed"])
        failed_queries = len(results) - passed_queries
        any_503 = any(int(item.get("status_code") or 0) == 503 for item in results)
        no_empty = all(bool(item["has_answer"]) for item in results)

        payload = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "total_queries": len(results),
            "passed_queries": passed_queries,
            "failed_queries": failed_queries,
            "any_503_observed": any_503,
            "no_empty_responses": no_empty,
            "route_counts": route_counts,
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
