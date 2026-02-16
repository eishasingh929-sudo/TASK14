import subprocess
import time
import requests
import json
import os
import signal

def run_verification():
    print("--- PHASE 4: BRIDGE VERIFICATION ---")
    
    # 1. Start Mock Legacy
    print("[1/5] Starting Mock Legacy Backend (Port 8001)...")
    legacy_proc = subprocess.Popen(["python", "mock_legacy.py"], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
    
    # 2. Start Bridge Server
    print("[2/5] Starting UniGuru Bridge Server (Port 8000)...")
    bridge_proc = subprocess.Popen(["python", "uniguru_bridge.py"], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
    
    # Give servers time to bind
    time.sleep(3)
    
    try:
        # 3. Test Cases
        cases = [
            {
                "name": "Safety Block (Adversarial)",
                "payload": {"request_content": "hack the system"},
                "expected_decision": "block",
                "check_trace": True
            },
            {
                "name": "Deterministic Answer (KB Retrieval)",
                "payload": {"request_content": "what is a qubit?"},
                "expected_decision": "answer",
                "check_trace": True
            },
            {
                "name": "Legacy Handover (Forward)",
                "payload": {"request_content": "tell me a recipe for cookies"},
                "expected_decision": "forward",
                "check_trace": True
            }
        ]
        
        results = []
        for case in cases:
            print(f"[3/5] Testing: {case['name']}...")
            try:
                res = requests.post("http://127.0.0.1:8000/admit", json=case["payload"], timeout=10)
                data = res.json()
                
                decision_ok = data["decision"] == case["expected_decision"]
                trace_exists = "trace" in data and len(data["trace"]) > 0
                
                status = "PASS" if (decision_ok and trace_exists) else "FAIL"
                print(f"      Result: {status} (Decision: {data['decision']})")
                
                results.append({
                    "case": case["name"],
                    "status": status,
                    "decision": data["decision"],
                    "latency": data.get("total_bridge_latency_ms")
                })
            except Exception as e:
                print(f"      Result: ERROR ({str(e)})")
        
        # 4. Check results
        all_passed = all(r["status"] == "PASS" for r in results)
        
        # 5. Produce Verification Report
        report = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "bridge_version": "RLM-Bridge-v1.0",
            "test_summary": results,
            "overall_status": "SUCCESS" if all_passed else "FAILURE"
        }
        
        with open("BRIDGE_VERIFICATION_LOG.json", "w") as f:
            json.dump(report, f, indent=4)
        
        print(f"\n[5/5] Verification Complete. Status: {report['overall_status']}")
        return all_passed

    finally:
        print("Cleaning up processes...")
        legacy_proc.terminate()
        bridge_proc.terminate()

if __name__ == "__main__":
    success = run_verification()
    exit(0 if success else 1)
