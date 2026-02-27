import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def http_get_json(url: str, timeout: int = 12):
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def http_post_json(url: str, payload: dict, timeout: int = 20):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def wait_http_ready(url: str, max_seconds: int = 45):
    start = time.time()
    while time.time() - start < max_seconds:
        try:
            http_get_json(url, timeout=4)
            return
        except Exception:
            time.sleep(0.8)
    raise RuntimeError(f"Timeout waiting for endpoint: {url}")


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    prod_dir = root / "Complete-Uniguru" / "server"
    log_dir = root / "demo_logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    prod_out = log_dir / "production.log"
    prod_err = log_dir / "production.err.log"
    bridge_out = log_dir / "bridge.log"
    bridge_err = log_dir / "bridge.err.log"
    proof_json = log_dir / "live_demo_proof.json"

    for p in [prod_out, prod_err, bridge_out, bridge_err]:
        if p.exists():
            p.unlink()

    print("[1/7] Starting production UniGuru backend on port 8000...")
    prod_proc = subprocess.Popen(
        ["node", "server.js"],
        cwd=str(prod_dir),
        stdout=prod_out.open("w", encoding="utf-8"),
        stderr=prod_err.open("w", encoding="utf-8"),
    )

    print("[2/7] Starting UniGuru Bridge on port 8001...")
    env = os.environ.copy()
    env["LEGACY_URL"] = env.get("LEGACY_URL", "http://127.0.0.1:8000/api/v1/chat/new")
    bridge_proc = subprocess.Popen(
        [sys.executable, "-m", "uniguru.bridge.server"],
        cwd=str(root),
        stdout=bridge_out.open("w", encoding="utf-8"),
        stderr=bridge_err.open("w", encoding="utf-8"),
        env=env,
    )

    try:
        print("[3/7] Health checks...")
        wait_http_ready("http://127.0.0.1:8000/health")
        wait_http_ready("http://127.0.0.1:8001/health")
        prod_health = http_get_json("http://127.0.0.1:8000/health")
        bridge_health = http_get_json("http://127.0.0.1:8001/health")

        print("[4/7] KB-first answer validation...")
        kb_resp = http_post_json(
            "http://127.0.0.1:8001/chat",
            {"message": "What are the seven tattvas in Jainism?"},
        )

        print("[5/7] Legacy forwarding validation...")
        try:
            legacy_resp = http_post_json(
                "http://127.0.0.1:8001/chat",
                {"message": "Tell me current weather in Delhi in one line."},
            )
        except urllib.error.HTTPError as e:
            legacy_resp = {"http_error": e.code, "detail": e.read().decode("utf-8", errors="ignore")}

        print("[6/7] Enforcement seal tamper simulation...")
        tampered = json.loads(json.dumps(kb_resp))
        if "data" in tampered:
            tampered["data"]["response_content"] = "TAMPERED CONTENT"
        from uniguru.enforcement.enforcement import SovereignEnforcement

        tamper_detected = not SovereignEnforcement().verify_bridge_seal(tampered)

        print("[7/7] Saving proof artifact...")
        proof = {
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "production_health_status": prod_health.get("status"),
            "bridge_health_status": bridge_health.get("status"),
            "bridge_target": bridge_health.get("production_target"),
            "kb_status_action": kb_resp.get("status_action"),
            "kb_has_signature": bool(kb_resp.get("enforcement_signature")),
            "legacy_status_action": legacy_resp.get("status_action"),
            "legacy_has_signature": bool(legacy_resp.get("enforcement_signature")),
            "tamper_detected": tamper_detected,
        }
        proof_json.write_text(json.dumps(proof, indent=2), encoding="utf-8")

        print("\n=== LIVE DEMO SUMMARY ===")
        print(f"Production health: {prod_health.get('status')}")
        print(f"Bridge health: {bridge_health.get('status')}")
        print(f"Bridge target: {bridge_health.get('production_target')}")
        print(f"KB status_action: {kb_resp.get('status_action')}")
        print(f"Legacy/refusal status_action: {legacy_resp.get('status_action')}")
        print(f"Tamper detected by seal check: {tamper_detected}")
        print(f"Proof JSON: {proof_json}")
        print(f"Production log: {prod_out}")
        print(f"Production err log: {prod_err}")
        print(f"Bridge log: {bridge_out}")
        print(f"Bridge err log: {bridge_err}")

    finally:
        for proc in [bridge_proc, prod_proc]:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=6)
                except subprocess.TimeoutExpired:
                    proc.kill()


if __name__ == "__main__":
    main()
