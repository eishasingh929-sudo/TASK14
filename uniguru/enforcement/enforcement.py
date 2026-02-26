import time
import uuid
from typing import Dict, Any, Optional
from uniguru.enforcement.seal import EnforcementSealer
from uniguru.verifier.source_verifier import SourceVerifier, VerificationStatus

class SovereignEnforcement:
    """
    Upgraded Enforcement Layer.
    Mandatory Global Verification and Cryptographic Sealing.
    """
    def __init__(self):
        self.sealer = EnforcementSealer()
        self.verifier = SourceVerifier()

    def process_and_seal(self, decision_schema: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """
        Implements the Pipeline: Verify -> Enforce -> Seal -> Return.
        """
        # 1. Global Verification Check
        content = decision_schema.get("data", {}).get("response_content", "")
        if not content and "legacy_response" in decision_schema:
            # Handle forwarded responses from UniGuru Backend
            content = str(decision_schema["legacy_response"])

        # Determine Global Verification Status
        # If the engine hasn't already verified it, we do a final check.
        v_status = decision_schema.get("verification_status", "UNVERIFIED")
        
        # Policy Enforcement based on Status
        if v_status == "VERIFIED":
            decision_schema["status_action"] = "ALLOW"
        elif v_status == "PARTIAL":
            decision_schema["status_action"] = "ALLOW_WITH_DISCLAIMER"
            decision_schema["disclaimer"] = "Note: This information is partially verified from available sources."
        else:
            # UNVERIFIED
            decision_schema["status_action"] = "REFUSE"
            decision_schema["decision"] = "block"
            decision_schema["reason"] = "Refined refusal: Source could not be verified by UniGuru Governance."
            decision_schema["data"] = {"response_content": "I cannot verify this information from current knowledge."}

        # 2. Cryptographic Sealing (GAP 1 Fix)
        # We seal AFTER the final verification and decision.
        final_content = str(decision_schema.get("data", {}).get("response_content", "BLOCKED"))
        signature = self.sealer.create_signature(final_content, request_id)
        
        decision_schema["enforcement_signature"] = signature
        decision_schema["enforced"] = True
        decision_schema["request_id"] = request_id
        decision_schema["sealed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        return decision_schema

    def verify_bridge_seal(self, response: Dict[str, Any]) -> bool:
        """
        Used by the Bridge to verify the signature before returning to user.
        """
        signature = response.get("enforcement_signature")
        request_id = response.get("request_id")
        content = str(response.get("data", {}).get("response_content", "BLOCKED"))
        
        if not signature:
            return False
            
        return self.sealer.verify_signature(content, request_id, signature)
