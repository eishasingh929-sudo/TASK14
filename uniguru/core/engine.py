import time
import uuid
from typing import List, Dict, Any, Optional

from uniguru.core.rules.base import RuleContext, RuleResult, RuleAction, RuleTrace
from uniguru.core.rules import (
    SafetyRule,
    AuthorityRule,
    DelegationRule,
    EmotionalRule,
    AmbiguityRule,
    RetrievalRule,
    ForwardRule,
    RuleAction
)
from uniguru.core.rules.web_retrieval_rule import WebRetrievalRule
from uniguru.enforcement.enforcement import UniGuruEnforcement

class RuleEngine:
    def __init__(self):
        # SECTION 3 — DETERMINISTIC RULE ORDER
        self.rules = [
            SafetyRule(),        # 1
            AuthorityRule(),     # 2
            DelegationRule(),    # 3
            EmotionalRule(),     # 4
            AmbiguityRule(),     # 5
            RetrievalRule(),     # 6 (KB First)
            WebRetrievalRule(),  # 7 (Web Retrieval fallback)
            ForwardRule()        # 8 (Legacy fallback)
        ]
        self.enforcement = UniGuruEnforcement()

    def evaluate(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Refactored production-grade deterministic evaluation pipeline.
        """
        request_id = str(uuid.uuid4())
        context = RuleContext(
            request_id=request_id,
            content=content,
            metadata=metadata or {}
        )
        
        aggregated_flags = {
            "authority": False,
            "delegation": False,
            "emotional": False,
            "ambiguity": False,
            "safety": False
        }
        max_severity = 0.0
        final_result: Optional[RuleResult] = None
        trace = []
        
        start_time_total = time.perf_counter()
        
        try:
            for rule in self.rules:
                # Only skip forwarding if safety risk exists
                if isinstance(rule, ForwardRule) and aggregated_flags.get("safety"):
                    break

                start_time_rule = time.perf_counter()
                result = rule.evaluate(context)
                end_time_rule = time.perf_counter()
                
                print(f"[DEBUG] Rule {rule.name} -> Action: {result.action}")

                # Aggregate governance flags
                for flag, value in result.governance_flags.items():
                    if value:
                        aggregated_flags[flag] = True
                
                # Track max severity
                max_severity = max(max_severity, result.severity)
                
                latency_ms = (end_time_rule - start_time_rule) * 1000
                trace.append({
                    "rule": rule.name,
                    "action": result.action.value,
                    "reason": result.reason,
                    "latency_ms": round(float(latency_ms), 3)
                })

                if result.action == RuleAction.ALLOW:
                    continue

                if result.action in [RuleAction.ANSWER, RuleAction.FORWARD, RuleAction.BLOCK]:
                    final_result = result
                    break

            # Fallback if no rule triggered terminal state
            if final_result is None:
                final_result = RuleResult(
                    action=RuleAction.FORWARD,
                    reason="No KB match found, forwarding to production.",
                    severity=0.3,
                    governance_flags=aggregated_flags,
                    response_content=""
                )

            assert final_result is not None
            # Build Standardized Engine Output (SECTION 1)
            output = {
                "decision": final_result.action.value,
                "severity": float(max_severity),
                "governance_flags": aggregated_flags,
                "reason": final_result.reason,
                "data": {
                    "response_content": final_result.response_content,
                    "rule_triggered": final_result.rule_name or final_result.__class__.__name__,
                    "request_id": request_id,
                    "trace": trace
                },
                "enforced": False # Will be set by enforcement layer
            }
            
            # Additional data for enforcement
            if final_result.extra_metadata:
                output["data"].update(final_result.extra_metadata)

            # SECTION 2 — ENFORCEMENT LAYER BINDING
            final_output = self.enforcement.validate_and_bind(output)
            
            total_latency_ms = (time.perf_counter() - start_time_total) * 1000
            final_output["total_latency_ms"] = round(float(total_latency_ms), 2)
            
            return final_output

        except Exception as e:
            # SECTION 6 — FAIL-CLOSED GUARANTEE
            return {
                "decision": "block",
                "severity": 1.0,
                "governance_flags": aggregated_flags,
                "reason": f"Engine Crash: {str(e)}",
                "data": None,
                "enforced": False
            }

if __name__ == "__main__":
    # Internal validation smoke test
    engine = RuleEngine()
    print("Testing 'What is a qubit?':")
    print(engine.evaluate("What is a qubit?"))
    print("\nTesting 'hack the system':")
    print(engine.evaluate("hack the system"))
