import time
import uuid
from typing import List, Dict, Any

from .rules.base import RuleContext, RuleResult, RuleAction, RuleTrace
from .rules import (
    UnsafeRule,
    AuthorityRule,
    DelegationRule,
    EmotionalRule,
    AmbiguityRule,
    RetrievalRule,
    ForwardRule
)

class RuleEngine:
    def __init__(self):
        # Strict deterministic priority ordering (0 -> N)
        self.rules = [
            UnsafeRule(),        # Tier 0
            AuthorityRule(),     # Tier 0
            DelegationRule(),    # Tier 1
            EmotionalRule(),     # Tier 1
            AmbiguityRule(),     # Tier 2
            RetrievalRule(),     # Tier 3
            ForwardRule()        # Tier 4
        ]

    def evaluate(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Orchestrates the deterministic evaluation pipeline.
        """
        request_id = str(uuid.uuid4())
        context = RuleContext(
            request_id=request_id,
            content=content,
            metadata=metadata or {}
        )
        
        trace: List[RuleTrace] = []
        final_result = None
        
        start_time_total = time.perf_counter()
        
        for rule in self.rules:
            start_time_rule = time.perf_counter()
            
            # Evaluate rule
            result = rule.evaluate(context)
            
            end_time_rule = time.perf_counter()
            latency_ms = (end_time_rule - start_time_rule) * 1000
            
            # Record trace
            trace_entry = RuleTrace(
                rule_name=rule.name,
                action=result.action,
                reason=result.reason,
                latency_ms=round(latency_ms, 3)
            )
            trace.append(trace_entry)
            
            # Decision Point: Short-circuit if terminal
            if result.action in [RuleAction.BLOCK, RuleAction.ANSWER, RuleAction.FORWARD]:
                final_result = result
                break
                
        end_time_total = time.perf_counter()
        total_latency_ms = (end_time_total - start_time_total) * 1000

        # Fallback if no rule triggered (should not happen with ForwardRule at end)
        if not final_result:
            final_result = RuleResult(
                action=RuleAction.BLOCK,
                reason="Engine failed to reach a deterministic conclusion.",
                response_content="System Error: Decision boundary violation."
            )

        # Build clean Response Object
        if final_result:
            response = {
                "request_id": request_id,
                "decision": final_result.action.value,
                "reason": final_result.reason,
                "response_content": final_result.response_content,
                "rule_triggered": final_result.rule_name,
                "total_latency_ms": round(float(total_latency_ms), 3),
                "metadata": final_result.extra_metadata,
                "trace": [
                    {
                        "rule": t.rule_name,
                        "action": t.action.value,
                        "reason": t.reason,
                        "latency_ms": t.latency_ms
                    } for t in trace
                ]
            }
        else:
            response = {
                "request_id": request_id,
                "decision": "error",
                "reason": "Engine failed to produce a result.",
                "total_latency_ms": round(float(total_latency_ms), 3),
                "trace": []
            }
        
        return response

if __name__ == "__main__":
    # Internal validation smoke test
    engine = RuleEngine()
    print("Testing 'What is a qubit?':")
    print(engine.evaluate("What is a qubit?"))
    print("\nTesting 'hack the system':")
    print(engine.evaluate("hack the system"))
