# UniGuru — As-Is System Flow

## Overview ✅
This document describes the live flow as implemented *in code only* (no behavior changes introduced by the adapter created for this task).

**High-level flow**
User Input -> UniGuru -> AI Being -> Enforcement -> Response

### Entry points
- **User Input**: Originates from client requests / user interactions (request object). Exact entry point names were not present in the repository snapshot; integrator should map their framework-specific entry points (HTTP handlers, websocket messages, etc.).
- **UniGuru**: Responsible for meaning extraction and signal generation (intent, ambiguity, risk, etc.). The new adaptor `adapters/uniguru_signal_adapter.py` wires signal generation into request context but does not change any behavior.
- **AI Being**: Reads signals (see `docs/AI_Being_Context_Contract.md`) to make behavior decisions. It must not be able to execute or override Enforcement.
- **Enforcement**: Final authority that decides whether/what response is issued.
- **Response**: Final output sent to the user.

### LLM / RAG usage
- As-is: UniGuru is a meaning & signal generation component. There were no direct, discoverable references to LLM or RAG components in the workspace snapshot. **TODO:** Integrator must map concrete LLM/RAG modules in the live system and verify that UniGuru signals are used only for contextual visibility (not for enforcement or decisioning).

### Response shaping
- UniGuru produces read-only signals that are attached to the request context. The signals may be read by AI Being to inform behavior decisions, but **must not** directly change, block, or short-circuit responses.
- Enforcement remains the final and sole authority for decisions that affect behavior or output.

---

**Notes & Non-Goals**
- This document does not propose any behavior changes or attempts to refactor existing logic.
- Where mappings could not be determined from code alone, explicit TODOs have been added to guide live verification.

*Generated during boundary-locked wiring work.*
