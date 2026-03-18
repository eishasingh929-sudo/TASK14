from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def _headers(token: str, caller: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Caller-Name": caller,
    }


def _http_get_json(url: str, headers: Dict[str, str], timeout: int = 20) -> Dict[str, Any]:
    request = urllib.request.Request(url=url, headers=headers, method="GET")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _http_get_text(url: str, headers: Dict[str, str], timeout: int = 20) -> str:
    request = urllib.request.Request(url=url, headers=headers, method="GET")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def _http_post_json(url: str, headers: Dict[str, str], payload: Dict[str, Any], timeout: int = 20) -> Dict[str, Any]:
    request = urllib.request.Request(
        url=url,
        headers=headers,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    base_url = os.getenv("UNIGURU_PUBLIC_BASE_URL", "https://uni-guru.in").rstrip("/")
    token = os.getenv("UNIGURU_API_TOKEN", "uniguru-dev-token-2026")
    caller = os.getenv("UNIGURU_PUBLIC_CALLER", "bhiv-assistant")
    session_id = f"public-api-{int(time.time())}"
    headers = _headers(token=token, caller=caller)

    output = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "base_url": base_url,
        "checks": {},
    }

    def capture(name: str, fn):
        started = time.perf_counter()
        try:
            data = fn()
            output["checks"][name] = {
                "ok": True,
                "latency_ms": round((time.perf_counter() - started) * 1000, 3),
                "data": data,
            }
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            output["checks"][name] = {
                "ok": False,
                "latency_ms": round((time.perf_counter() - started) * 1000, 3),
                "status_code": exc.code,
                "error": body,
            }
        except Exception as exc:  # pragma: no cover - operational script
            output["checks"][name] = {
                "ok": False,
                "latency_ms": round((time.perf_counter() - started) * 1000, 3),
                "error": str(exc),
            }

    capture("GET /health", lambda: _http_get_json(f"{base_url}/health", headers=headers))
    capture("GET /ready", lambda: _http_get_json(f"{base_url}/ready", headers=headers))
    capture(
        "POST /ask",
        lambda: _http_post_json(
            f"{base_url}/ask",
            headers=headers,
            payload={
                "query": "What is a qubit?",
                "allow_web": False,
                "session_id": session_id,
                "context": {"caller": caller, "allow_web": False},
            },
        ),
    )
    capture("GET /metrics", lambda: _http_get_text(f"{base_url}/metrics", headers=headers))

    target = Path("demo_logs") / "public_api_validation.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(str(target))


if __name__ == "__main__":
    main()
