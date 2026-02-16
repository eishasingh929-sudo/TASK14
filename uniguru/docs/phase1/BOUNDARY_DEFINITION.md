# Boundary Definition

## 1. Governance Boundary

| Responsibility | Current System | Unified Vision (RLM v1) |
| :--- | :--- | :--- |
| **Logic** | Python Core (Logic) | Python RLM |
| **Enforcement** | Basic String Matching (Logic) | Structured Rule Classes (Unsafe, Authority, Emotional) |
| **Validation** | Basic Validation (None?) | Strict Type Checking / Input Contract |
| **Persistence** | None (Stateless/Demo) | None (Stateless) |
| **Integration** | Ad-hoc (Functions) | Middleware HTTP Bridge |

**Hard Invariants:**
1.  **Authority**: The system MUST NEVER override its own rules.
2.  **Unsafe**: The system MUST NEVER process harmful/prohibited content.
3.  **Ambiguity**: The system MUST NEVER guess intent when unclear.
4.  **Delegation**: The system MUST NEVER generate academic work or execute on behalf of User without explicit permission/scope.
5.  **Emotional**: The system MUST ACKNOWLEDGE distress but NEVER attempt therapy/counseling.

## 2. Logic Boundary

**Middleware (Python RLM):**
*   **Role**: Decision Engine / Gatekeeper.
*   **Scope**: Rules, Safety, Governance, Deterministic Retrieval.
*   **Contract**: JSON Input -> Decision (Allow/Block/Answer).

**Legacy Node/Express Logic:**
*   **Role**: Generative Capability / Chat.
*   **Scope**: RAG, Conversational Flow, Persona, Creativity.
*   **Contract**: JSON Input -> Text Response.

## 3. Retrieval Boundary

**Deterministic Retrieval (RLM):**
*   **Method**: Keyword Matching (`core/retriever.py`).
*   **Source**: `Quantum_KB` (Markdown files).
*   **Scope**: Foundational concepts only (Qubit, Superposition, etc.).
*   **Purpose**: Grounding responses in fact, preventing hallucination.

**Semantic Retrieval (Legacy Node):**
*   **Method**: Vector Embeddings / Semantic Search.
*   **Source**: Existing Vector DB (Assumed).
*   **Scope**: Broader knowledge discovery.
*   **Purpose**: Answering open-ended questions.

## 4. Enforcement Boundary

**Rule Precedence:**
1.  **Safety/Prohibited**: IMMEDIATE BLOCK.
2.  **Authority Challenge**: IMMEDIATE BLOCK.
3.  **Ambiguity**: CLARIFY.
4.  **Emotional**: EMPATHETIC REDIRECT.
5.  **Delegation Request**: REFUSAL / GUIDANCE.
6.  **Fact Retrieval**: DETERMINISTIC ANSWER.
7.  **General Chat**: FORWARD to Legacy Node.

The Middleware MUST execute rules strictly in this order.
The Legacy Node MUST assume all input it receives has passed this gate.
