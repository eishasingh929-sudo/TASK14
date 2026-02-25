# Phase-0 Discovery: UniGuru Robustness Audit

## System Overview (Black-Box Observation)
**Target:** [uni-guru.in](https://uni-guru.in)
**Status:** Observation Mode (Phase-0)

### 1. Observed Behaviors
*   **Input Handling:** Accepts natural language queries related to academic and career guidance.
*   **Response Generation:** Provides structured reasoning and recommendations.
*   **Safety Boundaries:** Refuses non-academic or harmful queries.
*   **Failures:** Potential for hallucinations or ambiguous reasoning paths if not hardened.

### 2. Documented Assumptions
*   **Inference Engine:** Assumed to be LLM-based (proprietary or open-source).
*   **Reasoning Path:** Non-deterministic unless explicitly constrained.
*   **External Integration:** Assumed to eventually connect with "AI Being" and "Enforcement Engine".

### 3. Canonical Contracts (Provisional)
| Aspect | Expectation |
| :--- | :--- |
| **Input** | Valid academic/career query. |
| **Output** | Reasoned response, no execution commands, no tool calls. |
| **Determinism** | Structured format, repeatable core logic. |

### 4. "Do Not Build Yet" List
*   **DO NOT** implement tool-calling or execution logic.
*   **DO NOT** add self-mutation or RL capabilities.
*   **DO NOT** bypass enforcement boundaries.
*   **DO NOT** implement production-grade database connectors until repo access is granted.

### 5. Patch Plan (Strategy for Phase-1)
1.  **Harden Entry Points:** Standardize input normalization.
2.  **Inject Fallback Ladders:** Define what happens when confidence is low.
3.  **Audit Logs:** Implement the "Bucket-ready" write-only audit structure.
4.  **Proof of Boundary:** Implement static checks to ensure no tool-use strings are generated.
