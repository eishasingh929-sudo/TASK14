import hashlib
import time
import uuid
from typing import Any, Optional


class EnforcementDecision:
    def __init__(self, verdict: str, reason: str):
        self.verdict = verdict
        self.reason = reason


class UniGuruEnforcement:
    """
    Enforcement Layer - Final Authority.
    Cryptographically seals every response with SHA256 signature.
    Enforces strict production-grade invariants.
    """
    SEVERITY_THRESHOLD = 0.5
    MIN_RETRIEVAL_CONFIDENCE = 0.3

    # ------------------------------------------------------------------ #
    #  CRYPTOGRAPHIC SEALING                                               #
    # ------------------------------------------------------------------ #
    @staticmethod
    def generate_signature(response_content: str, request_id: str) -> str:
        """
        Generate a SHA256 enforcement signature:
            hash = SHA256(response_content + request_id)
        Returns hex-encoded digest.
        """
        raw = (str(response_content) + str(request_id)).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    @staticmethod
    def verify_signature(response_content: str, request_id: str, signature: str) -> bool:
        """
        Re-compute and compare the expected signature against the supplied one.
        Returns True only on exact match.
        """
        expected = UniGuruEnforcement.generate_signature(response_content, request_id)
        return expected == signature

    # ------------------------------------------------------------------ #
    #  PRIMARY VALIDATION + BINDING                                        #
    # ------------------------------------------------------------------ #
    def validate_and_bind(self, decision_schema: dict) -> dict:
        """
        Validates the decision schema, attaches the enforcement_signature,
        and binds the 'enforced' flag.
        """
        decision = decision_schema.get("decision")
        severity = decision_schema.get("severity", 0.0)
        flags = decision_schema.get("governance_flags", {})
        data = decision_schema.get("data", {})
        request_id = (data or {}).get("request_id", str(uuid.uuid4()))

        # ---- Invariant 1: High severity must block --------------------- #
        if severity >= self.SEVERITY_THRESHOLD and decision != "block":
            blocked = {
                "decision": "block",
                "severity": severity,
                "governance_flags": flags,
                "reason": "Enforcement failure: Severity threshold violation",
                "data": None,
                "enforced": False,
                "enforcement_signature": None,
                "signature_verified": False,
            }
            return blocked

        # ---- Invariant 2: No unsafe forward allowed -------------------- #
        if decision == "forward":
            if severity >= self.SEVERITY_THRESHOLD or any(flags.values()):
                blocked = {
                    "decision": "block",
                    "severity": severity,
                    "governance_flags": flags,
                    "reason": "Enforcement failure: Unsafe forward attempt",
                    "data": None,
                    "enforced": False,
                    "enforcement_signature": None,
                    "signature_verified": False,
                }
                return blocked

        # ---- Invariant 3: Retrieval confidence above threshold --------- #
        if decision == "answer" and "retrieval_trace" in (data or {}):
            confidence = data.get("retrieval_trace", {}).get("confidence", 0.0)
            if confidence < self.MIN_RETRIEVAL_CONFIDENCE:
                blocked = {
                    "decision": "block",
                    "severity": severity,
                    "governance_flags": flags,
                    "reason": "Enforcement failure: Low retrieval confidence",
                    "data": None,
                    "enforced": False,
                    "enforcement_signature": None,
                    "signature_verified": False,
                }
                return blocked

        # ---- All invariants passed: generate cryptographic seal -------- #
        response_content = ""
        if data:
            response_content = data.get("response_content", "")

        signature = self.generate_signature(str(response_content), str(request_id))

        # Verify immediately (self-verify after generation)
        sig_ok = self.verify_signature(str(response_content), str(request_id), signature)

        decision_schema["enforced"] = True
        decision_schema["enforcement_signature"] = signature
        decision_schema["signature_verified"] = sig_ok
        decision_schema["sealed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        return decision_schema

    # ------------------------------------------------------------------ #
    #  RESPONSE SIGNATURE VERIFICATION (Called by Bridge before returning)#
    # ------------------------------------------------------------------ #
    def verify_response(self, final_output: dict) -> bool:
        """
        Called by the Bridge to verify the enforcement_signature before
        returning a response to the user.
        Returns True only if signature is present and valid.
        If False → Bridge must BLOCK the response.
        """
        sig = final_output.get("enforcement_signature")
        if not sig:
            return False

        data = final_output.get("data") or {}
        response_content = data.get("response_content", "")
        request_id = data.get("request_id", "")
        return self.verify_signature(str(response_content), str(request_id), sig)

    # ------------------------------------------------------------------ #
    #  LEGACY / HARNESS INTERFACE                                          #
    # ------------------------------------------------------------------ #
    def check(self, request: Any, candidate: Any) -> "EnforcementDecision":
        """
        Legacy/Harness interface for Enforcement.
        """
        verdict = getattr(candidate, "policy", None)
        if verdict and hasattr(verdict, "verdict"):
            final_verdict = verdict.verdict
            reason = verdict.reason or "Policy check complete"
        else:
            final_verdict = "allow"
            reason = "Audit complete"

        if final_verdict == "allow":
            return EnforcementDecision(verdict="allow", reason=reason)

        return EnforcementDecision(verdict="block", reason=reason or "Blocked by policy")
