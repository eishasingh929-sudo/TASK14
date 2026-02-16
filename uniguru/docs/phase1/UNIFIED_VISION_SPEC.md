# Unified Vision Specification: RLM v1

## 1. System Philosophy

**Goal**: Transform UniGuru from a "Demo-Safe Reasoning System" into a **Product-Ready Middleware Layer** that enforces governance while enabling safe integration with the legacy generative system (`Legacy Node/Express`).

*   **Deterministic Core**: All decisions, rejections, and direct answers MUST be fully deterministic.
*   **Stateless Enforcer**: The RLM layer handles permissions, intent scanning, and refusal logic.
*   **Safe Delegation**: RLM filters requests before they ever reach the costly/risky generative model.
*   **Audit Trail**: Every request is logged at the decision point.

## 2. Target Architecture

The unified system sits **between** the User and the Legacy Node application.

*   `User` (Frontend/API Client)
    ↓ (HTTP POST)
*   [ **UniGuru RLM Middleware** (Python / FastAPI) ]
    *   `GovernanceEngine` (Enforce Invariants)
    *   `RuleEngine` (Evaluate `Authority`, `Unsafe`, `Ambiguity`, etc.)
    *   `RetrievalEngine` (Keyword Match `Quantum_KB`)
    *   `DecisionGate` (Allow / Block / Direct Answer)
    ↓ (If `FORWARD` Decision)
*   [ **Legacy Node Application** (Express) ]
    *   `Auth Middleware` (Existing)
    *   `RAG Pipeline` (Existing - Vector DB)
    *   `LLM Connector` (Existing - OpenAI/Anthropic)
    ↓
*   `User` (Response)

## 3. Implementation Phases

1.  **Phase 1: System Mapping** (COMPLETED)
    - Defined boundaries.
    - Audited KB structure.
    - Mapped legacy system assumptions.

2.  **Phase 2: RLM v1 Design** (COMPLETED)
    - Formalize `Rule` classes.
    - Implement rigorous priority logic.
    - Create test harness (`58` cases passed).

3.  **Phase 3: Retrieval Engine V2** (COMPLETED)
    - Expand keyword matching to cover all subdirectories.
    - Add fallback hierarchy (`Domain` -> `Foundations`).

4.  **Phase 4: Middleware Bridge** (COMPLETED)
    - Build `FastAPI` server wrapper.
    - Define JSON Schema Contract.
    - Create Integration Simulator.

5.  **Phase 5: Controlled Integration** (COMPLETED)
    - Launch Integration Environment.
    - Connect real requests (via canonical Node mock).
    - Validate end-to-end flow.

6.  **Phase 6: Hardening**
    - Boundary leak audit.
    - Documentation handover.
    - Final polish.

## 4. Key Success Metrics

1.  **Determinism**: 100% consistent behavior for identical inputs (excluding legacy generative variances).
2.  **Coverage**: All defined `Unsafe` or `Prohibited` inputs act as immediate blockers.
3.  **Latency**: Middleware overhead < 50ms.
4.  **Retrieval**: Correctly surfaces local KB content for exact matches.
5.  **Audit**: Full traceability of `Input -> Rule Triggered -> Decision`.
