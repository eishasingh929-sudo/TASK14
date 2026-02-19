# RULE_MATRIX.md

## Purpose
This document defines the deterministic behaviour rules of UniGuru.
It acts as the single source of truth for how the system responds to
different types of user queries.

Each rule maps:
Query Type → Detection Pattern → System Action → Implementing File

This ensures predictable and governed behaviour.

---

## Rule Matrix

| Query Type | Rule Name | Trigger Pattern | Response Type | RuleAction | Implementing File | Description |
|---|---|---|---|---|---|---|
| Ambiguous Query | AmbiguityRule | Vague references (e.g., "tell me about it", "explain this", missing subject/context) | Clarification | ANSWER (clarification prompt) | `uniguru/governance/ambiguity.py` | Requests more context instead of guessing. Prevents hallucinations. |
| Delegation Request | DelegationRule | User asks system to make life decisions (e.g., "decide for me", "choose my career") | Refusal | BLOCK | `uniguru/governance/delegation.py` | Prevents the system from taking responsibility for user decisions. |
| Authority Assumption | AuthorityRule | User assumes system has official authority (e.g., "as an official advisor confirm...") | Correction | BLOCK / ANSWER | `uniguru/governance/authority.py` | Corrects false authority claims and prevents misinformation. |
| Emotional Distress | EmotionalRule | Emotional language (e.g., "I feel lost", "I feel useless") | Acknowledgment | ANSWER | `uniguru/governance/emotional.py` | Provides supportive acknowledgement without giving harmful advice. |
| Unsafe / Prohibited Query | UnsafeRule | Harmful or unsafe instructions | Refusal | BLOCK | `uniguru/enforcement/safety.py` | Stops unsafe or harmful requests at the governance layer. |
| Knowledge Query | RetrievalRule | Questions matching knowledge base topics | Retrieval | RETRIEVE | `uniguru/retrieval/retriever.py` | Retrieves grounded answers from Quantum_KB. |
| General Safe Query | ForwardRule | Queries not matching other rules | Forward to legacy system | FORWARD | `uniguru/core/engine.py` | Forwards safe queries to the legacy backend. |

---

## Deterministic Behaviour Summary

The Rule Engine processes rules in a fixed order:

1. Safety / Governance Rules  
2. Ambiguity Detection  
3. Emotional Support  
4. Knowledge Retrieval  
5. Forward to Legacy System  

Only one final action is selected.

This guarantees:
- No randomness
- No hidden behaviour
- Same input → Same outcome

---

## Rule Execution Flow

User Query
↓
Governance Rules (BLOCK if unsafe)
↓
Ambiguity Rule (CLARIFY if unclear)
↓
Emotional Rule (ACKNOWLEDGE if emotional)
↓
Retrieval Rule (RETRIEVE if knowledge query)
↓
Forward Rule (FORWARD if general query)

---

## Conclusion

The rule matrix guarantees UniGuru behaves in a
**predictable, governed, and deterministic manner.**
