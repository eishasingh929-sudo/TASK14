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
OUTPUT_JSON = ROOT / "demo_logs" / "live_integration_proof.json"
OUTPUT_MD = ROOT / "docs" / "reports" / "LIVE_INTEGRATION_PROOF.md"
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
    env_node["UNIGURU_REQUEST_TIMEOUT_MS"] = env_node.get("UNIGURU_REQUEST_TIMEOUT_MS", "15000")
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


def _post(url: str, payload: Dict[str, Any], *, headers: Dict[str, str] | None = None) -> Dict[str, Any]:
    started = time.perf_counter()
    response = requests.post(url, json=payload, headers=headers or {}, timeout=30)
    latency_ms = round((time.perf_counter() - started) * 1000, 3)
    body = response.json()
    return {
        "status_code": response.status_code,
        "latency_ms": latency_ms,
        "body": body,
    }


def _extract_result(name: str, execution: Dict[str, Any]) -> Dict[str, Any]:
    body = execution["body"]
    data = body.get("data", body) if isinstance(body, dict) else {}
    answer = str(data.get("answer") or "").strip()
    presentation = data.get("presentation") or {}
    return {
        "name": name,
        "status_code": execution["status_code"],
        "latency_ms": execution["latency_ms"],
        "route": (data.get("routing") or {}).get("route"),
        "verification_status": data.get("verification_status"),
        "integration": body.get("integration"),
        "presentation_available": bool(presentation.get("summary") or presentation.get("body")),
        "non_empty_answer": bool(answer),
        "answer_preview": answer[:220],
    }


def _write_markdown(payload: Dict[str, Any]) -> None:
    lines = [
        "# Live Integration Proof",
        "",
        f"Execution date (UTC): {payload['timestamp_utc']}",
        "",
        "## Summary",
        f"- All scenarios passed: {payload['all_passed']}",
        f"- Structured UI payload present in all scenarios: {payload['ui_payload_present_for_all']}",
        "",
        "## Scenarios",
    ]
    for item in payload["results"]:
        lines.append(
            f"- {item['name']}: HTTP {item['status_code']}, route `{item['route']}`, "
            f"verification `{item['verification_status']}`, UI payload `{item['presentation_available']}`"
        )
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    backend_proc: subprocess.Popen[Any] | None = None
    node_proc: subprocess.Popen[Any] | None = None

    try:
        backend_proc, node_proc = _start_stack()
        auth_headers = {"Authorization": f"Bearer {LIVE_TOKEN}"}

        runs: List[Dict[str, Any]] = []
        runs.append(
            _extract_result(
                "External UI via Node",
                _post(
                    f"{NODE_BASE}/api/v1/chat/query",
                    {
                        "query": "What is a qubit?",
                        "session_id": "proof-ui-1",
                        "context": {"caller": "uniguru-frontend", "channel": "nic-demo"},
                    },
                ),
            )
        )
        runs.append(
            _extract_result(
                "Gurukul integration",
                _post(
                    f"{NODE_BASE}/api/v1/gurukul/query",
                    {
                        "student_query": "Explain Nyaya logic.",
                        "student_id": "STU-1001",
                        "session_id": "proof-gurukul-1",
                        "context": {"caller": "gurukul-platform", "class_id": "CLASS-9"},
                    },
                ),
            )
        )
        runs.append(
            _extract_result(
                "Samachar integration",
                _post(
                    f"{NODE_BASE}/api/v1/samachar/query",
                    {
                        "query": "Summarize this student update: admissions portal opens Monday morning.",
                        "session_id": "proof-samachar-1",
                        "context": {"caller": "samachar-platform", "channel": "headline-card"},
                    },
                ),
            )
        )
        runs.append(
            _extract_result(
                "Direct /ask API",
                _post(
                    f"{PYTHON_BASE}/ask",
                    {
                        "query": "How does placement support work?",
                        "session_id": "proof-ask-1",
                        "context": {"caller": "uniguru-frontend", "channel": "direct-api"},
                    },
                    headers=auth_headers,
                ),
            )
        )

        payload = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "all_passed": all(item["status_code"] == 200 and item["non_empty_answer"] for item in runs),
            "ui_payload_present_for_all": all(item["presentation_available"] for item in runs),
            "results": runs,
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
