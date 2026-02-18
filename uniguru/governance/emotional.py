from core.rules.base import BaseRule, RuleContext, RuleResult, RuleAction

class EmotionalRule(BaseRule):
    def __init__(self):
        self.emotional_triggers = [
            "overwhelmed",
            "overwhelming",
            "stressed",
            "anxious",
            "burned out",
            "confused",
            "frustrated",
            "urgent",
            "asap",
            "quickly"
        ]

    def evaluate(self, context: RuleContext) -> RuleResult:
        query = context.content.lower().strip()
        
        for trigger in self.emotional_triggers:
            if trigger in query:
                return RuleResult(
                    action=RuleAction.ANSWER,
                    reason=f"Emotional load/Pressure detected: '{trigger}'",
                    response_content="I understand things may feel overwhelming or urgent right now. Let's break this down step-by-step to provide structured guidance.",
                    rule_name=self.name
                )
        
        return RuleResult(
            action=RuleAction.ALLOW,
            reason="No emotional distress detected.",
            rule_name=self.name
        )
