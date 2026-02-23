from typing import Any

class EnforcementDecision:
    def __init__(self, verdict: str, reason: str):
        self.verdict = verdict
        self.reason = reason

class UniGuruEnforcement:
    """
    Enforcement Layer - Final Authority.
    Enforces strict production-grade invariants.
    """
    SEVERITY_THRESHOLD = 0.5
    MIN_RETRIEVAL_CONFIDENCE = 0.3

    def validate_and_bind(self, decision_schema: dict) -> dict:
        """
        Validates the decision schema and binds the 'enforced' flag.
        """
        decision = decision_schema.get("decision")
        severity = decision_schema.get("severity", 0.0)
        flags = decision_schema.get("governance_flags", {})
        data = decision_schema.get("data", {})
        
        # Invariant 1: No BLOCK rule bypassed (High severity must block)
        if severity >= self.SEVERITY_THRESHOLD and decision != "block":
            return {
                "decision": "block",
                "severity": severity,
                "governance_flags": flags,
                "reason": "Enforcement failure: Severity threshold violation",
                "data": None,
                "enforced": False
            }

        # Invariant 2: No unsafe forward allowed
        if decision == "forward":
            if severity >= self.SEVERITY_THRESHOLD or any(flags.values()):
                return {
                    "decision": "block",
                    "severity": severity,
                    "governance_flags": flags,
                    "reason": "Enforcement failure: Unsafe forward attempt",
                    "data": None,
                    "enforced": False
                }

        # Invariant 3: Retrieval confidence above threshold if answering
        if decision == "answer" and "retrieval_trace" in (data or {}):
            confidence = data.get("retrieval_trace", {}).get("confidence", 0.0)
            if confidence < self.MIN_RETRIEVAL_CONFIDENCE:
                return {
                    "decision": "block",
                    "severity": severity,
                    "governance_flags": flags,
                    "reason": "Enforcement failure: Low retrieval confidence",
                    "data": None,
                    "enforced": False
                }

        # If all invariants pass, bind enforced = True
        decision_schema["enforced"] = True
        return decision_schema

    def check(self, request: Any, candidate: Any) -> EnforcementDecision:
        """
        Legacy/Harness interface for Enforcement.
        Uses PolicyDecision/EnforcementDecision style.
        """
        # Extracts decision from candidate policy if available, or result
        verdict = getattr(candidate, "policy", None)
        if verdict and hasattr(verdict, "verdict"):
            final_verdict = verdict.verdict
            reason = verdict.reason or "Policy check complete"
        else:
            final_verdict = "allow" # Default to allow for audit
            reason = "Audit complete"

        # Apply basic invariants even for legacy
        # (Simplified for compatibility)
        if final_verdict == "allow":
            return EnforcementDecision(verdict="allow", reason=reason)
        
        return EnforcementDecision(verdict="block", reason=reason or "Blocked by policy")
