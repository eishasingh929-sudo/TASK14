from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from uniguru.service import api as api_module
from uniguru.service.api import app


def main() -> None:
    original_auth_required = api_module._API_AUTH_REQUIRED
    original_tokens = set(api_module._API_TOKENS)
    original_pytest_runtime = api_module._is_pytest_runtime
    original_rate_limit = api_module._RATE_LIMIT_MAX_REQUESTS
    original_queue_limit = api_module._ASK_QUEUE_LIMIT
    api_module._API_AUTH_REQUIRED = False
    api_module._API_TOKENS = set()
    api_module._is_pytest_runtime = lambda: True
    api_module._RATE_LIMIT_MAX_REQUESTS = 1000
    api_module._ASK_QUEUE_LIMIT = 200

    client = TestClient(app)
    headers = {"X-Caller-Name": "bhiv-assistant"}

    scenarios = [
        (
            "bhiv_assistant_query",
            {
                "query": "What is a qubit?",
                "session_id": "eco-bhiv-1",
                "allow_web": False,
                "context": {"caller": "bhiv-assistant", "allow_web": False},
            },
        ),
        (
            "gurukul_knowledge_query",
            {
                "query": "Explain ahimsa",
                "session_id": "eco-gurukul-1",
                "allow_web": False,
                "context": {"caller": "gurukul-platform", "allow_web": False},
            },
        ),
        (
            "workflow_request",
            {
                "query": "create workflow ticket for onboarding",
                "session_id": "eco-workflow-1",
                "allow_web": False,
                "context": {"caller": "bhiv-assistant", "allow_web": False},
            },
        ),
        (
            "system_command_block",
            {
                "query": "sudo delete all files",
                "session_id": "eco-system-1",
                "allow_web": False,
                "context": {"caller": "bhiv-assistant", "allow_web": False},
            },
        ),
    ]

    try:
        evidence = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "results": [],
        }
        for name, payload in scenarios:
            response = client.post("/ask", json=payload, headers=headers)
            row = {"name": name, "status_code": response.status_code}
            if response.status_code == 200:
                body = response.json()
                row["decision"] = body.get("decision")
                row["verification_status"] = body.get("verification_status")
                row["route"] = (body.get("routing") or {}).get("route")
                row["request_id"] = body.get("request_id")
            else:
                row["error"] = response.text
            evidence["results"].append(row)

        output_path = Path("demo_logs") / "ecosystem_validation_report.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
        print(str(output_path))
    finally:
        api_module._API_AUTH_REQUIRED = original_auth_required
        api_module._API_TOKENS = original_tokens
        api_module._is_pytest_runtime = original_pytest_runtime
        api_module._RATE_LIMIT_MAX_REQUESTS = original_rate_limit
        api_module._ASK_QUEUE_LIMIT = original_queue_limit


if __name__ == "__main__":
    main()
