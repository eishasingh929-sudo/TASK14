from uniguru.core.rules.base import BaseRule, RuleContext, RuleResult, RuleAction

class ForwardRule(BaseRule):
    def evaluate(self, context: RuleContext) -> RuleResult:
        # Compatibility-only: the canonical router now decides whether to use LLM fallback.
        return RuleResult(
            action=RuleAction.FORWARD,
            reason="Query is safe and clear. Canonical router may delegate to LLM fallback.",
            severity=0.0,
            governance_flags={
                "authority": False,
                "delegation": False,
                "emotional": False,
                "ambiguity": False,
                "safety": False
            },
            rule_name=self.name
        )
