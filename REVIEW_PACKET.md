# REVIEW_PACKET

## Scope
Integration-readiness review for UniGuru (engine + Node middleware + API consumers), without modifying core reasoning logic.

## Canonical Runtime Path
1. API Consumer (Product UI or Gurukul)
2. `node-backend` (`/api/v1/chat/query`, `/api/v1/gurukul/query`)
3. Python UniGuru API `POST /ask` (`backend/uniguru/service/api.py`)
4. Router (`backend/uniguru/router/conversation_router.py`)
5. UniGuru KB path or LLM/workflow/system route
6. Structured response back through Node to consumer

## Critical Integration Findings
1. Auth/ENV is the top blocker:
- If `UNIGURU_API_AUTH_REQUIRED=true` and token missing, `/ask` returns `503`.
- Token mismatch between Node and Python causes integration failure.

2. KB output was UI-hostile:
- Verified answers can include long raw markdown dumps.

3. LLM fallback readiness gap:
- `ROUTE_LLM` requires `UNIGURU_LLM_URL`; when missing, open/general prompts return config message.

4. Fragmentation risk:
- Active runtime uses `backend + node-backend`; legacy bridge/docs can mislead integration.

## Improvements Completed In This Task
1. Auth compatibility fix:
- Python now accepts `X-Service-Token` in addition to `Authorization: Bearer ...`.
- File: `backend/uniguru/service/api.py`
- Test added: `backend/tests/test_registry.py::test_service_token_header_can_be_enforced`

2. Upstream error transparency fix:
- Node now propagates real upstream status (401/403/503/etc.) instead of generic 502.
- Files: `node-backend/src/uniguruClient.js`, `node-backend/src/server.js`

3. KB response usability fix (integration-layer):
- Node compacts KB-heavy answer text for chat UI and preserves full content in `raw_answer`.
- File: `node-backend/src/responseFormatter.js`
- Wired in: `node-backend/src/server.js`

4. Integration health endpoint added:
- `GET /health/integration` in Node for quick env readiness checks.
- File: `node-backend/src/server.js`

## Verification Executed
- `pytest backend/tests/test_registry.py -q` -> pass
- `node --check src/server.js` -> pass
- `node --check src/uniguruClient.js` -> pass
- `node --check src/responseFormatter.js` -> pass

## Status for Handoff
- Yashika (integration): can wire against Node canonical path with clear auth + fallback signals.
- Tiwari (testing): can test true upstream failure codes and UI-safe answer behavior.
- Alay (devops): can deploy once env token + LLM fallback policy are finalized.
