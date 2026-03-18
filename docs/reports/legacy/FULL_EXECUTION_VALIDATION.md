# Full Execution Validation

## Request Lifecycle
The UniGuru system enforces a strict request lifecycle to ensure safety and governance are prioritized over generation.

1. **Entrypoint**: User sends a POST request to the Bridge Server (`/chat`).
2. **Identification**: Bridge generates a unique `trace_id` for end-to-end observability.
3. **Reasoning Layer**: Request is sent to the `RuleEngine`.
4. **Tiered Evaluation**:
    - **Tier 0 (Safety & Authority)**: `UnsafeRule` and `AuthorityRule` check for prohibited terms and jailbreak attempts.
    - **Tier 1 (Behavioral)**: `DelegationRule` and `EmotionalRule` manage system boundaries and support.
    - **Tier 2 (Cognitive)**: `AmbiguityRule` checks for unclear intents.
    - **Tier 3 (Retriever)**: `RetrievalRule` attempts a deterministic answer from the local Knowledge Base.
    - **Tier 4 (Handover)**: `ForwardRule` handles legitimate generative queries.
5. **Decision Execution**:
    - **BLOCK**: Rejects the request immediately.
    - **ANSWER**: Returns a local deterministic response.
    - **FORWARD**: Forwards the request to the Legacy UniGuru system.

## Decision Paths
| Path | Decision | Source | bypass possible? |
|---|---|---|---|
| Safety/Jailbreak | BLOCK | RuleEngine (Tier 0) | No |
| Prohibited Task | BLOCK | RuleEngine (Tier 1) | No |
| Known Knowledge | ANSWER | Quantum_KB | No |
| General Intent | FORWARD | Legacy System | Only if cleared by all rules |

## Why Bypass is Impossible
The architecture is designed as a **deterministic gatekeeper**:
- The Legacy UniGuru system is **isolated** and only reachable via the Bridge.
- The Rule Engine uses **short-circuit evaluation**; if a Tier 0 rule blocks a request, it never reaches Tier 4.
- All code logic is strictly tiered, ensuring security checks are completed before any forwarding happens.
