# Difference Matrix: Demo-Safe vs Unified RLM v1

| Feature | Current Python Core (task11) | Proposed Unified RLM v1 | Legacy Node (Assumed) |
| :--- | :--- | :--- | :--- |
| **Logic** | Simple Functions (`detect_x`) | Structured Classes (`AuthorityRule`) | Generative RAG/LLM |
| **State** | Stateless | Stateless | Session-based |
| **Retrieval** | Minimal Keyword Map (6 items) | Dynamic Recursive Scan (All KBs) | Vector Search (Embeddings) |
| **Governance** | String Match (Brittle) | Formal Rule Engine (Robust) | Prompt Engineering (Soft) |
| **Integration** | None (Local Script) | HTTP Middleware Bridge | HTTP API |
| **Execution** | Single File Logic | Orchestrated Pipeline | Async Pipeline |
| **Audit** | None | Request/Decision Log | Application Logs |
| **Safety** | Basic Detection | Hardened Invariants | High Variance |

## Key Deltas to Address

1.  **Rule Formalization**: Transform `detect_ambiguity(str)` -> `AmbiguityRule.evaluate(context)`.
2.  **Retrieval Expansion**: Move from hardcoded dictionary to filesystem scanner.
3.  **Middleware Bridge**: Build the API layer to serve the logic.
4.  **Integration**: Connect the Middleware to the Legacy inputs/outputs.
5.  **Logging**: Add structured audit trails for every decision.
