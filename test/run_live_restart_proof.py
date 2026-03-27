from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import requests


ROOT = Path(__file__).resolve().parents[1]
PYTHON_PORT = int(os.getenv("UNIGURU_PYTHON_PORT", "8000"))
NODE_PORT = int(os.getenv("UNIGURU_NODE_PORT", "3000"))
PYTHON_BASE = f"http://127.0.0.1:{PYTHON_PORT}"
NODE_BASE = f"http://127.0.0.1:{NODE_PORT}"
OUTPUT_JSON = ROOT / "demo_logs" / "live_restart_proof.json"
OUTPUT_MD = ROOT / "docs" / "reports" / "LIVE_RESTART_PROOF.md"
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


def _probe(label: str) -> Dict[str, Any]:
    health = requests.get(f"{PYTHON_BASE}/health", timeout=10).json()
    response = requests.post(
        f"{NODE_BASE}/api/v1/chat/query",
        json={
            "query": "Tell me a short joke.",
            "session_id": f"restart-proof-{label.lower()}",
            "context": {"caller": "bhiv-assistant", "channel": "restart-proof"},
        },
        timeout=35,
    )
    payload = response.json()
    data = payload.get("data", {}) if isinstance(payload, dict) else {}
    answer = str(data.get("answer") or "").strip()
    return {
        "label": label,
        "health": health,
        "status_code": response.status_code,
        "route": (data.get("routing") or {}).get("route"),
        "verification_status": data.get("verification_status"),
        "answer_preview": answer[:240],
        "non_empty_answer": bool(answer),
    }


def _write_markdown(payload: Dict[str, Any]) -> None:
    lines = [
        "# Live Restart Proof",
        "",
        f"Execution date (UTC): {payload['timestamp_utc']}",
        "",
        "## Summary",
        f"- Restart proof passed: {payload['restart_proof_passed']}",
        f"- Sample before restart returned answer: {payload['before_restart']['non_empty_answer']}",
        f"- Sample after restart returned answer: {payload['after_restart']['non_empty_answer']}",
        "",
        "## Health Snapshot",
        f"- Before restart LLM available: {payload['before_restart']['health']['checks']['llm_available']}",
        f"- After restart LLM available: {payload['after_restart']['health']['checks']['llm_available']}",
        f"- Before restart auth mode: {payload['before_restart']['health']['auth']['mode']}",
        f"- After restart auth mode: {payload['after_restart']['health']['auth']['mode']}",
    ]
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    backend_proc: subprocess.Popen[Any] | None = None
    node_proc: subprocess.Popen[Any] | None = None

    try:
        backend_proc, node_proc = _start_stack()
        before_restart = _probe("before-restart")
        _stop(node_proc)
        _stop(backend_proc)
        backend_proc, node_proc = _start_stack()
        after_restart = _probe("after-restart")
        payload = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "restart_proof_passed": bool(
                before_restart["status_code"] == 200
                and after_restart["status_code"] == 200
                and before_restart["non_empty_answer"]
                and after_restart["non_empty_answer"]
            ),
            "before_restart": before_restart,
            "after_restart": after_restart,
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
