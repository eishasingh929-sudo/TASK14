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
OUTPUT_JSON = ROOT / "demo_logs" / "llm_fallback_proof.json"
OUTPUT_MD = ROOT / "docs" / "reports" / "LLM_FALLBACK_PROOF.md"
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
    env_backend["UNIGURU_LLM_URL"] = "http://127.0.0.1:65534/unreachable-llm"
    env_backend["UNIGURU_LLM_MODEL"] = "gpt-oss:120b-cloud"
    env_backend["UNIGURU_LLM_TIMEOUT_SECONDS"] = "2"
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
    env_node["UNIGURU_REQUEST_TIMEOUT_MS"] = "8000"
    node_proc = subprocess.Popen(
        ["node", "src/server.js"],
        cwd=str(ROOT / "node-backend"),
        env=env_node,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    _wait_for_health(f"{PYTHON_BASE}/health/live")
    _wait_for_health(f"{NODE_BASE}/health")
    return backend_proc, node_proc


def _capture(name: str, url: str, payload: Dict[str, Any], headers: Dict[str, str] | None = None) -> Dict[str, Any]:
    started = time.perf_counter()
    response = requests.post(url, json=payload, headers=headers or {}, timeout=20)
    latency_ms = round((time.perf_counter() - started) * 1000, 3)
    body = response.json()
    data = body.get("data", body) if isinstance(body, dict) else {}
    answer = str(data.get("answer") or "").strip()
    presentation = data.get("presentation") or {}
    return {
        "name": name,
        "status_code": response.status_code,
        "latency_ms": latency_ms,
        "route": (data.get("routing") or {}).get("route"),
        "verification_status": data.get("verification_status"),
        "non_empty_answer": bool(answer),
        "answer_preview": answer[:220],
        "integration_notes": data.get("integration_notes") or [],
        "presentation_available": bool(presentation.get("body") or presentation.get("summary")),
    }


def _write_markdown(payload: Dict[str, Any]) -> None:
    lines = [
        "# LLM Fallback Proof",
        "",
        f"Execution date (UTC): {payload['timestamp_utc']}",
        "",
        "## Health Snapshot",
        f"- LLM available: {payload['health_snapshot']['checks']['llm_available']}",
        f"- LLM reachable: {payload['health_snapshot']['llm']['reachable']}",
        f"- Model loaded: {payload['health_snapshot']['llm']['model_loaded']}",
        "",
        "## Query Results",
    ]
    for item in payload["results"]:
        lines.append(
            f"- {item['name']}: HTTP {item['status_code']}, route `{item['route']}`, "
            f"non-empty `{item['non_empty_answer']}`, UI payload `{item['presentation_available']}`"
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
        headers = {"Authorization": f"Bearer {LIVE_TOKEN}"}
        results: List[Dict[str, Any]] = [
            _capture(
                "External UI fallback",
                f"{NODE_BASE}/api/v1/chat/query",
                {
                    "query": "Explain recursion in simple words.",
                    "session_id": "llm-fallback-ui",
                    "context": {"caller": "uniguru-frontend"},
                },
            ),
            _capture(
                "Samachar fallback",
                f"{NODE_BASE}/api/v1/samachar/query",
                {
                    "query": "Give me a latest world news summary.",
                    "session_id": "llm-fallback-samachar",
                    "context": {"caller": "samachar-platform"},
                },
            ),
            _capture(
                "Direct /ask fallback",
                f"{PYTHON_BASE}/ask",
                {
                    "query": "What is the capital of France?",
                    "session_id": "llm-fallback-ask",
                    "context": {"caller": "uniguru-frontend"},
                },
                headers=headers,
            ),
        ]

        payload = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "health_snapshot": health,
            "fallback_proof_passed": bool(
                health["checks"]["llm_available"] is False
                and all(item["status_code"] == 200 and item["non_empty_answer"] for item in results)
            ),
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
