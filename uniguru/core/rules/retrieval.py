from .base import BaseRule, RuleContext, RuleResult, RuleAction
from ..retriever import retrieve_knowledge_with_trace

class RetrievalRule(BaseRule):
    def evaluate(self, context: RuleContext) -> RuleResult:
        kb_content, trace = retrieve_knowledge_with_trace(context.content)
        
        if kb_content:
            return RuleResult(
                action=RuleAction.ANSWER,
                reason="Knowledge found in local KB.",
                response_content=f"UniGuru Deterministic Knowledge Retrieval:\n\n{kb_content}",
                rule_name=self.name,
                extra_metadata={"retrieval_trace": trace}
            )
        
        return RuleResult(
            action=RuleAction.ALLOW,
            reason="No relevant knowledge found in local KB.",
            rule_name=self.name,
            extra_metadata={"retrieval_trace": trace}
        )
