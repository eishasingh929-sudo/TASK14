from uniguru.core.rules.base import BaseRule, RuleContext, RuleResult, RuleAction
from uniguru.retrieval.retriever import retrieve_knowledge_with_trace
from uniguru.verifier.source_verifier import SourceVerifier

KB_CONFIDENCE_THRESHOLD = 0.5
UNVERIFIED_REFUSAL = "I cannot verify this information with current knowledge."

class RetrievalRule(BaseRule):
    def evaluate(self, context: RuleContext) -> RuleResult:
        kb_content, trace = retrieve_knowledge_with_trace(context.content)

        if kb_content and float(trace.get("confidence", 0.0) or 0.0) >= KB_CONFIDENCE_THRESHOLD:
            verification = SourceVerifier.verify_retrieval_trace(
                trace=trace,
                min_confidence=KB_CONFIDENCE_THRESHOLD
            )
            is_verified = verification.get("truth_declaration") in {"VERIFIED", "VERIFIED_PARTIAL"}

            return RuleResult(
                action=RuleAction.ANSWER,
                reason="Knowledge found in local KB and verified."
                if is_verified else "Knowledge found but failed verification gate.",
                severity=0.0,
                governance_flags={
                    "authority": False,
                    "delegation": False,
                    "emotional": False,
                    "ambiguity": False,
                    "safety": False
                },
                response_content=(
                    f"UniGuru Deterministic Knowledge Retrieval:\n\n{kb_content}"
                    if is_verified else UNVERIFIED_REFUSAL
                ),
                rule_name=self.name,
                extra_metadata={
                    "retrieval_trace": trace,
                    "verification": verification
                }
            )

        return RuleResult(
            action=RuleAction.ALLOW,
            reason="No relevant knowledge found in local KB or confidence below 0.5.",
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
