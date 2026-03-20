# UNIGURU_COMPONENTS

Integration context (critical):
- API Consumer (Product): Frontend / BHIV calls Node middleware.
- API Consumer (Gurukul): Gurukul calls Node middleware.
- Node middleware calls Python `/ask`.

## 1. API Layer
USE THIS:
- Repo/File: `backend/uniguru/service/api.py`
- Correct version: Current active API (`FastAPI app version 1.1.0`) used by Docker `uvicorn uniguru.service.api:app`.

DO NOT USE:
- `backend/uniguru/bridge/server.py` as main API entry for integration; this is an older bridge path (`/chat`) and not the canonical `/ask` entry.

## 2. Router
USE THIS:
- Repo/File: `backend/uniguru/router/conversation_router.py`
- Correct version: Current router used directly by `service/api.py` via `conversation_router.route_query(...)`.

DO NOT USE:
- Any legacy docs that treat bridge `/chat` as the only entrypoint.

## 3. Knowledge Base
USE THIS:
- Repo/Files: `backend/uniguru/knowledge/**` (domain markdown files), plus `backend/uniguru/knowledge/index/*` metadata.
- Correct version: Current KB folders under `backend/uniguru/knowledge`.

DO NOT USE:
- Legacy KB path references in old docs (for example `Quantum_KB` legacy naming).

## 4. Retrieval Logic
USE THIS:
- Repo/Files: `backend/uniguru/core/rules/retrieval.py` + `backend/uniguru/retrieval/retriever.py` + `backend/uniguru/verifier/source_verifier.py`
- Correct version: Active deterministic retrieval path called by `RuleEngine` in runtime.

DO NOT USE:
- `backend/uniguru/retrieval/kb_engine.py` (legacy retrieval utility, not on main `/ask` flow).
- `backend/uniguru/truth/truth_validator.py` (legacy path, not called by current API flow).
- `backend/uniguru/core/rules/web_retrieval_rule.py` (defined but not registered in active rule chain).

## 5. LLM Fallback
USE THIS:
- Repo/File: `backend/uniguru/router/conversation_router.py` (`ROUTE_LLM` + `_request_llm`)
- Correct version: Environment-driven fallback via `UNIGURU_LLM_URL`.

DO NOT USE:
- Any older bridge-level assumptions that LLM fallback is outside the router.

## USE THIS (Integration Canonical)
- `backend/uniguru/service/api.py`
- `backend/uniguru/router/conversation_router.py`
- `backend/uniguru/service/live_service.py`
- `backend/uniguru/core/engine.py`
- `backend/uniguru/core/rules/retrieval.py`
- `backend/uniguru/retrieval/retriever.py`
- `node-backend/src/server.js`
- `node-backend/src/uniguruClient.js`
- `node-backend/src/responseFormatter.js` (UI-safe post-processing for KB-heavy answers)
- `frontend/src/services/uniguru-api.ts` (consumer integration point)
- `Complete-Uniguru/server/config/rag.js` (legacy consumer path, still used in older app wiring)

## DO NOT USE (for current integration wiring)
- `backend/uniguru/bridge/server.py` as the primary production entrypoint.
- `backend/uniguru/truth/truth_validator.py`
- `backend/uniguru/retrieval/kb_engine.py`
- `backend/uniguru/core/rules/web_retrieval_rule.py`
- `docs/HANDOVER.md` (contains outdated paths and startup instructions).
- `docs/reports/legacy/*` for current runtime decisions.

## Auth / ENV (must align across services)
USE THIS:
- Python env: `UNIGURU_API_AUTH_REQUIRED`, `UNIGURU_API_TOKEN`, `UNIGURU_API_TOKENS`, `UNIGURU_ALLOWED_CALLERS`
- Node env: `UNIGURU_API_TOKEN`, `UNIGURU_ASK_URL`
- Auth headers supported by Python API: `Authorization: Bearer <token>` and `X-Service-Token: <token>`

DO NOT USE:
- Mixed token values between Node and Python environments.
- Assuming auth is optional in production.

## Phase 6: Pre-Canonical Structure Map (No file moves yet)

Target structure:

`uniguru/`
- maps from workspace root coordination (`README.md`, `docker-compose.yml`, `.env*`, docs)

`uniguru/backend/`
- map: `backend/uniguru/service/api.py`
- map: `backend/uniguru/service/live_service.py`
- map: `backend/uniguru/core/*`
- map: `backend/uniguru/enforcement/*`

`uniguru/router/`
- map: `backend/uniguru/router/conversation_router.py`
- map: `backend/uniguru/service/query_classifier.py`

`uniguru/kb/`
- map: `backend/uniguru/knowledge/**`
- map: `backend/uniguru/retrieval/retriever.py`
- map: `backend/uniguru/verifier/source_verifier.py`

`uniguru/integrations/`
- map: `node-backend/src/server.js`
- map: `node-backend/src/uniguruClient.js`
- map: `backend/uniguru/integrations/*`
- legacy reference only (do not wire as primary): `Complete-Uniguru/server/config/rag.js`
