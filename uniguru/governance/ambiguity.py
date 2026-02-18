from core.rules.base import BaseRule, RuleContext, RuleResult, RuleAction

class AmbiguityRule(BaseRule):
    def __init__(self):
        self.vague_terms = [
            "this", "that", "it", "something", "anything",
            "what is that?", "what is this?", "tell me more"
        ]

    def evaluate(self, context: RuleContext) -> RuleResult:
        query = context.content.strip()
        tokens = query.split()

        # Check for single word or solely vague pronouns
        is_ambiguous = False
        if len(tokens) == 1:
            is_ambiguous = True
        elif query.lower() in self.vague_terms:
            is_ambiguous = True

        if is_ambiguous:
            return RuleResult(
                action=RuleAction.ANSWER,
                reason="Input is too vague or lacks context.",
                response_content="I'm sorry, I'm not sure I understand your request. Could you please provide more context or clarify what you're looking for?",
                rule_name=self.name
            )
        
        return RuleResult(
            action=RuleAction.ALLOW,
            reason="Input appears clear.",
            rule_name=self.name
        )
