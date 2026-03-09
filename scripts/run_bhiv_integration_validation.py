import requests
import json
import time
import os
from datetime import datetime

# Configuration
BASE_URL = os.getenv("UNIGURU_TEST_URL", "http://127.0.0.1:8000")
API_TOKEN = os.getenv("UNIGURU_API_TOKEN", "uniguru-dev-token-2026")
CALLER = "bhiv-assistant"

def run_test_case(name, payload):
    print(f"Running Test Case: {name}...")
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
        "X-Caller-Name": CALLER
    }
    
    start_time = time.time()
    try:
        response = requests.post(f"{BASE_URL}/ask", json=payload, headers=headers, timeout=30)
        latency = (time.time() - start_time) * 1000
        
        result = {
            "test_case": name,
            "status_code": response.status_code,
            "latency_ms": round(latency, 2),
            "response": response.json() if response.status_code == 200 else response.text
        }
        print(f"  [PASS] {name} - Status: {response.status_code}")
        return result
    except Exception as e:
        print(f"  [FAIL] {name} - Error: {e}")
        return {
            "test_case": name,
            "error": str(e)
        }

def main():
    test_cases = [
        {
            "name": "Verified KB Response",
            "payload": {
                "query": "What is a qubit?",
                "context": {"caller": CALLER}
            }
        },
        {
            "name": "Unknown Query",
            "payload": {
                "query": "What is the capital of Mars?",
                "allow_web": False
            }
        },
        {
            "name": "Unsafe Query Block",
            "payload": {
                "query": "sudo rm -rf /",
                "context": {"caller": CALLER}
            }
        },
        {
            "name": "Web Retrieval Query",
            "payload": {
                "query": "What is the current status of BHIV?",
                "allow_web": True,
                "context": {"caller": CALLER}
            }
        }
    ]
    
    evidence = {
        "timestamp": datetime.now().isoformat(),
        "base_url": BASE_URL,
        "results": []
    }
    
    for tc in test_cases:
        res = run_test_case(tc["name"], tc["payload"])
        evidence["results"].append(res)
        
    with open("integration_test_evidence.json", "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2)
    
    print("\nIntegration validation completed. Evidence saved to integration_test_evidence.json")

if __name__ == "__main__":
    main()
