from .base import BaseRule, RuleContext, RuleResult, RuleAction

class ForwardRule(BaseRule):
    def evaluate(self, context: RuleContext) -> RuleResult:
        # If we reached this point, the query is safe, clear, and not in the local KB.
        return RuleResult(
            action=RuleAction.FORWARD,
            reason="Query is safe and clear. Ready for legacy system processing.",
            rule_name=self.name
        )
