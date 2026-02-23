from uniguru.core.rules.base import BaseRule, RuleContext, RuleResult, RuleAction
from uniguru.retrieval.retriever import retrieve_knowledge_with_trace

class RetrievalRule(BaseRule):
    def evaluate(self, context: RuleContext) -> RuleResult:
        kb_content, trace = retrieve_knowledge_with_trace(context.content)
        
        if kb_content:
            return RuleResult(
                action=RuleAction.ANSWER,
                reason="Knowledge found in local KB.",
                severity=0.0,
                governance_flags={
                    "authority": False,
                    "delegation": False,
                    "emotional": False,
                    "ambiguity": False,
                    "safety": False
                },
                response_content=f"UniGuru Deterministic Knowledge Retrieval:\n\n{kb_content}",
                rule_name=self.name,
                extra_metadata={"retrieval_trace": trace}
            )
        
        return RuleResult(
            action=RuleAction.ALLOW,
            reason="No relevant knowledge found in local KB or confidence too low.",
            severity=0.0,
            governance_flags={
                "authority": False,
                "delegation": False,
                "emotional": False,
                "ambiguity": False,
                "safety": False
            },
            rule_name=self.name,
            extra_metadata={"retrieval_trace": trace}
        )
