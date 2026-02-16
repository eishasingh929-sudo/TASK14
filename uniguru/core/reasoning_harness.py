import sys
import os

# Ensure project root is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Correct Imports (No monkey-patches)
from uniguru.core.core import UniGuruCoreRequest, UniGuruCoreResponse, PolicyDecision
from uniguru.core.governance import GovernanceEngine, SafetyStatus
from uniguru.core.updated_1m_logic import generate_safe_response, direct_response
from uniguru.enforcement.enforcement import UniGuruEnforcement

class UniGuruHarness:
    """
    Final Hardened Reasoning Harness for UniGuru.
    Pipeline: Input -> Governance -> updated_1m_logic -> Enforcement -> Response.
    """
    
    def __init__(self):
        self.enforcement = UniGuruEnforcement()

    def process_query(self, query):
        print(f"\n--- Query: {query} ---")
        
        # STEP 1: Governance PRE-CHECK on user input
        status, reason = GovernanceEngine.evaluate_input(query)
        if status != SafetyStatus.ALLOWED:
            deny_msg = f"Forbidden input detected: {reason}"
            print(f"GOVERNANCE BLOCK: {deny_msg}")
            return {"status": "DENIED", "reason": reason, "response": deny_msg}

        # STEP 2: Call updated_1m_logic (Deterministic Behavior + Grounding)
        # This layer only runs if governance allowed the input.
        try:
            safeguarded_output = generate_safe_response(query, direct_response)
        except Exception as e:
            safeguarded_output = "Internal logic failure."
            print(f"LOGIC ERROR: {e}")


        # STEP 3: Run ENFORCEMENT on generated output
        # Enforcement is final authority.
        req = UniGuruCoreRequest(
            requestId="final-audit",
            userContext={},
            query={"text": query},
            context=[],
            flags={}
        )
        
        # Governance post-audit check on output
        out_status, out_reason = GovernanceEngine.audit_output(safeguarded_output)
        
        candidate = UniGuruCoreResponse(
            requestId="final-audit",
            status="ok" if out_status == SafetyStatus.ALLOWED else "rejected",
            result={"value": safeguarded_output},
            sources=[],
            policy=PolicyDecision(
                verdict="allow" if out_status == SafetyStatus.ALLOWED else "block", 
                reason=out_reason or "Governance passed"
            )
        )
        
        enforcement_decision = self.enforcement.check(req, candidate)
        
        # Final Verification: Enforcement cannot be bypassed
        if enforcement_decision is None:
            raise RuntimeError("CRITICAL ARCHITECTURAL BREACH: Enforcement step was bypassed.")

        if enforcement_decision.verdict == "allow":
            print(f"UniGuru: {safeguarded_output}")
            return {
                "status": "ALLOWED",
                "response": safeguarded_output
            }
        else:
            block_msg = "Safety violation blocked by Enforcement."
            print(f"ENFORCEMENT BLOCK: {enforcement_decision.reason}")
            return {
                "status": "DENIED",
                "reason": enforcement_decision.reason,
                "response": block_msg
            }

if __name__ == "__main__":
    harness = UniGuruHarness()
    
    test_queries = [
        "What is a qubit?",
        "Help", # < 3 words
        "automate my studies",
        "sudo rm -rf"
    ]
    
    for q in test_queries:
        harness.process_query(q)
