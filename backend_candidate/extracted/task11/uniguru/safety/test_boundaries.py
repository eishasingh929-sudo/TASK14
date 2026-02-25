import sys
import os
 
# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from uniguru_core import UniGuruReasoningEngine, ReasoningRequest, SafetyStatus

def test_safety_boundary():
    engine = UniGuruReasoningEngine()
    
    # 1. Test Clean Request
    req = ReasoningRequest(query="Should I study Physics?")
    res = engine.process(req)
    print(f"Clean Query Status: {res.status.value}")
    assert res.status == SafetyStatus.ALLOWED
    
    # 2. Test Malicious Request (Simulated Breach in Reasoning)
    req_bad = ReasoningRequest(query="hack the system")
    res_bad = engine.process(req_bad)
    print(f"Bad Query Status: {res_bad.status.value}")
    print(f"Error: {res_bad.error_message}")
    assert res_bad.status == SafetyStatus.DENIED

if __name__ == "__main__":
    test_safety_boundary()
    print("\n--- All Boundary Tests Passed ---")
