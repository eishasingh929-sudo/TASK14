from .base import BaseRule, RuleContext, RuleResult, RuleAction

class AuthorityRule(BaseRule):
    def __init__(self):
        self.authority_triggers = [
            "you are allowed to",
            "you must",
            "override rules",
            "system permission",
            "ignore governance",
            "forget previous",
            "act as",
            "new instructions",
            "ignore all previous",
            "forget your safety",
            "ignore rules"
        ]

    def evaluate(self, context: RuleContext) -> RuleResult:
        query = context.content.lower().strip()
        
        for trigger in self.authority_triggers:
            if trigger in query:
                return RuleResult(
                    action=RuleAction.BLOCK,
                    reason=f"Authority override attempt detected: '{trigger}'",
                    response_content="I do not have the authority to override system rules or follow unauthorized persona instructions. I can only operate within my defined governance boundaries.",
                    rule_name=self.name
                )
        
        return RuleResult(
            action=RuleAction.ALLOW,
            reason="No authority challenge detected.",
            rule_name=self.name
        )
