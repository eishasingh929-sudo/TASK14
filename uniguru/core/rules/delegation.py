from .base import BaseRule, RuleContext, RuleResult, RuleAction

class DelegationRule(BaseRule):
    def __init__(self):
        self.delegation_triggers = [
            "do this for me",
            "automate",
            "complete my",
            "finish my",
            "write my assignment",
            "handle this for me",
            "run the code",
            "perform action"
        ]

    def evaluate(self, context: RuleContext) -> RuleResult:
        query = context.content.lower().strip()
        
        for trigger in self.delegation_triggers:
            if trigger in query:
                return RuleResult(
                    action=RuleAction.BLOCK,
                    reason=f"Delegation request detected: '{trigger}'",
                    response_content="I cannot automate tasks or perform actions directly. I provide guidance and informational support only.",
                    rule_name=self.name
                )
        
        return RuleResult(
            action=RuleAction.ALLOW,
            reason="No delegation request detected.",
            rule_name=self.name
        )
