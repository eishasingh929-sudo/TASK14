# REVIEW_PACKET.md

## 1. ENTRY POINT

Frontend entry (if exists):
Path: frontend/src/main.tsx

Backend entry:
Path: backend/uniguru/service/api.py

Explain in 2 lines:
Frontend boots React in `main.tsx`, then user messages are sent from ChatWidget through `frontend/src/services/uniguru-api.ts` to `POST /ask`.
Backend starts at FastAPI `api.py`; `/ask` normalizes/authenticates request and hands it to `conversation_router.route_query(...)`.

## 2. CORE EXECUTION FLOW (MAX 3 FILES ONLY)

File 1: Router / Decision Layer
Path: backend/uniguru/router/conversation_router.py
What it does (2 lines)
Classifies query type and selects route: `ROUTE_UNIGURU`, `ROUTE_LLM`, `ROUTE_WORKFLOW`, or `ROUTE_SYSTEM`.
Dispatches to `LiveUniGuruService` for knowledge route or builds delegated/block responses for other routes.

File 2: API Layer
Path: backend/uniguru/service/api.py
What it does (2 lines)
Defines `/ask`, `/voice/query`, `/health`, `/metrics`, with request validation, auth, caller allowlist, rate limit, and telemetry hooks.
For `/ask`, it builds normalized context and invokes `conversation_router.route_query(...)`, returning final response JSON.

File 3: Execution Layer (KB / LLM / Workflow)
Path: backend/uniguru/service/live_service.py
What it does (2 lines)
Runs `RuleEngine` and deterministic KB pipeline, then applies reasoning trace + output governance + enforcement seal.
If KB cannot answer and web retrieval is allowed, resolves through web retriever path; otherwise returns verified block/unknown response.

## 3. LIVE FLOW (REAL EXECUTION)

User action:
User asks: "What is a qubit?"

System flow:
Frontend -> API (`/ask`) -> Router -> Engine -> Response

Now provide ONE REAL RESPONSE:
```json
{
  "decision": "answer",
  "answer": "Based on verified source: qubit.md\n\nUniGuru Deterministic Knowledge Retrieval:\n\nTitle: Nielsen & Chuang Core Concepts\nSource(s): Nielsen, M. A. & Chuang, I. L., \"Quantum Computation and Quantum Information\" (2010)\nAuthors: Michael A. Nielsen; Isaac L. Chuang (summarized)\nYear: 2010\nDomain: Quantum Foundations / Quantum Information\nIngestion date: 2026-02-06\n\nDefinitions\n- Qubit: Two-level quantum system represented by state vector $|\\psi\\rangle=\\alpha|0\\rangle+\\beta|1\\rangle$.\n- Density operator: $\\rho$ describing mixed states; $\\rho=\\sum_i p_i|\\psi_i\\rangle\\langle\\psi_i|$.\n- Unitary evolution: Closed-system dynamics described by $\\rho\\mapsto U\\rho U^{\\dagger}$.\n- Measurement (projective): Born rule $p_i=\\langle\\psi|\\Pi_i|\\psi\\rangle$ for projector $\\Pi_i$.\n- Entanglement: Non-separable joint states with correlations beyond classical mixtures.\n\nKey Concepts\n- State space: Hilbert space formalism and tensor-product composition.\n- Quantum gates: Reversible operations implemented by unitary matrices.\n- Quantum circuits: Composition of gates to implement algorithms.\n- Quantum error: Decoherence and noise motivating error correction.\n\nLight equation context\n- State normalization: $\\langle\\psi|\\psi\\rangle=1$.\n- Expectation value: $\\langle A\\rangle=\\mathrm{Tr}(\\rho A)$.\n\nConcept explanations\n- Superposition: Linear combination of basis states enabling interference.\n- Measurement collapse (operational): Probabilistic update of state post-measurement.\n- Quantum tomography (summary): Reconstruction of $\\rho$ from measurement statistics.\n\nCitations\n- Nielsen & Chuang (2010). Core textbook treatment of these foundational topics.SSSS\n\n",
  "session_id": null,
  "reason": "Knowledge found in local KB and verified.",
  "ontology_reference": {
    "concept_id": "2200072c-5a0d-4f68-a56a-a0c807f6cf5e",
    "domain": "quantum",
    "snapshot_version": 1,
    "snapshot_hash": "e7292c6b78cfa8c7fe0008b36f6916879af5b9c78d763a3cbf402d3e3d6895ad",
    "truth_level": 3
  },
  "reasoning_trace": {
    "sources_consulted": [
      "ontology_graph",
      "ontology_registry",
      "quantum"
    ],
    "retrieval_confidence": 1.0,
    "ontology_domain": "quantum",
    "verification_status": "VERIFIED",
    "verification_details": "VERIFIED"
  },
  "verification_status": "VERIFIED",
  "status_action": "ALLOW",
  "routing": {
    "query_type": "KNOWLEDGE_QUERY",
    "route": "ROUTE_UNIGURU",
    "router_latency_ms": 23.57
  }
}
```

## 4. WHAT WAS BUILT IN THIS TASK

• Added: REVIEW_PACKET.md
• Modified: REVIEW_PACKET.md
• Not touched: backend runtime code, frontend runtime code, deploy config

## 5. FAILURE CASES

• If backend fails -> frontend `useChat` catches request error and shows: "Request failed. Please try again."
• If invalid input -> `/ask` returns `422` (Pydantic validation) or `400` for governance/input violations.
• If router blocks -> response returns `decision: "block"` with policy block answer (e.g., system-command route).

## 6. PROOF

Test output:
```text
$ pytest backend/tests/test_router.py -q
......                                                                   [100%]
```
