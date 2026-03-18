from __future__ import annotations

import json
import os
import time
import urllib.request


def post_ask(base_url: str, token: str, query: str) -> dict:
    payload = {"query": query, "context": {"caller": "uniguru-frontend"}}
    request = urllib.request.Request(
        url=f"{base_url}/ask",
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-Caller-Name": "uniguru-frontend",
        },
        data=json.dumps(payload).encode("utf-8"),
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    base_url = os.getenv("UNIGURU_TEST_URL", "http://127.0.0.1:8000")
    token = os.getenv("UNIGURU_API_TOKEN", "uniguru-dev-token-2026")
    queries = [
        "What is a qubit?",
        "Explain superposition",
        "What is Nyaya logic?",
    ]

    for query in queries:
        started = time.perf_counter()
        result = post_ask(base_url=base_url, token=token, query=query)
        latency = (time.perf_counter() - started) * 1000
        print(f"\nQ: {query}")
        print(f"Latency: {latency:.2f} ms")
        print(f"Decision: {result.get('decision')}")
        print(f"Verification: {result.get('verification_status')}")
        print(f"Answer: {str(result.get('answer', ''))[:220]}")


if __name__ == "__main__":
    main()
