# CANONICAL_SYSTEM_DECISION

Date: 2026-03-21  
Owner: UniGuru TASK14 stabilization handoff

This document is the **single source of truth** for integration and deployment decisions.

## 1. Final Canonical Decision (Locked)

### Keep (Production/Integration Path)

- Python UniGuru API at `backend/uniguru/service/api.py` (**KEEP**)
- Python router at `backend/uniguru/router/conversation_router.py` (**KEEP**)
- Python deterministic KB path (`core/engine.py`, `core/rules/retrieval.py`, `retrieval/retriever.py`) (**KEEP**)
- Node middleware at `node-backend/src/server.js` and `node-backend/src/uniguruClient.js` (**KEEP**)

### Remove From Runtime Path (Do Not Integrate/Deploy)

- Legacy bridge-first entrypoint `backend/uniguru/bridge/server.py` (**REMOVE from canonical runtime path**)
- Legacy retrieval utility `backend/uniguru/retrieval/kb_engine.py` (**REMOVE from runtime usage**)
- Legacy truth path `backend/uniguru/truth/truth_validator.py` (**REMOVE from runtime usage**)
- Legacy app wiring under `Complete-Uniguru/**` (**REMOVE from integration path for Gurukul/Samachar**)

Note: files may remain in repository for historical reference, but they are **non-canonical** and must not be wired into runtime.

## 2. Final Architecture Lock (BHIV/Gurukul/Samachar)

**This is the architecture BHIV will use going forward:**

`UI / API Consumer -> Node Middleware -> Python POST /ask -> Conversation Router -> KB OR LLM fallback -> Response`

### Canonical Endpoints

- Consumer ingress (Node):
  - `POST /api/v1/chat/query`
  - `POST /api/v1/gurukul/query`
- Core reasoning ingress (Python):
  - `POST /ask` (**only canonical text query entrypoint**)

No alternate production entrypoint is approved.

## 3. KB Decision (Explicit)

Current KB retrieval is keyword/token heuristic (`AdvancedRetriever`) with verification gating.

Decision:
- **Acceptable for current integration + demo readiness**: **YES**
- **Acceptable as long-term scale retrieval engine**: **NO**

Rationale:
- It is deterministic, local, and now protected by fallback-safe routing.
- It is not semantic/vector retrieval and will miss broader paraphrase coverage at scale.

Locked policy for this handoff:
- Keep current KB retrieval in production path for immediate integration.
- Do not replace during this stabilization task.
- Any retrieval modernization (embedding/vector/hybrid) is post-handoff work, not part of canonical lock.

## 4. Integration Readiness Statement

**System is READY for integration in demo-safe mode.**

Readiness basis:
- Canonical path is locked and deterministic.
- `/ask` returns a response for all tested required query classes.
- Auth/env failure mode is safety-handled (`demo-no-auth` fallback when tokens missing).
- Health/readiness endpoints expose router/KB/LLM status for DevOps verification.

Known non-blocking constraints:
- Live-news quality is generic unless external live LLM/web endpoint is configured.
- Legacy docs/components still in repo are non-canonical and must be ignored.

## 5. Handover Contract

### Yashika (Integration)
- Integrate only against Node middleware endpoints listed above.
- Do not consume bridge `/chat` or legacy Complete-Uniguru server paths.

### Alay (DevOps)
- Deploy only `backend` + `node-backend` stack.
- Verify:
  - `GET /health` and `GET /ready` on Python
  - `GET /health` and `GET /ready` on Node

### Vinayak (Testing)
- Use `scripts/run_phase8_checks.py` and `demo_logs/phase8_test_outputs.json`.
- Required five queries are already captured and should remain passing.

## 6. Supersession

If any other report conflicts with this file, this file wins.
