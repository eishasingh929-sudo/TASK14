# Clean Repo Structure

## Canonical Runtime Surface

- `backend/`
  - Canonical Python service, router, KB engine, retrieval, governance, API
- `node-backend/`
  - Canonical middleware and integration surface for UI, Gurukul, and Samachar
- `frontend/`
  - UI client
- `scripts/`
  - Ingestion and operational scripts
- `test/`
  - Executable stack and validation runs
- `backend/tests/`
  - Python unit and integration tests

## Canonical Files

- API entrypoint: [`backend/uniguru/service/api.py`](./backend/uniguru/service/api.py)
- Router: [`backend/uniguru/router/conversation_router.py`](./backend/uniguru/router/conversation_router.py)
- Deterministic KB engine: [`backend/uniguru/service/live_service.py`](./backend/uniguru/service/live_service.py)
- Shared preflight governance: [`backend/uniguru/service/governance_preflight.py`](./backend/uniguru/service/governance_preflight.py)
- Unified retriever: [`backend/uniguru/retrieval/retriever.py`](./backend/uniguru/retrieval/retriever.py)
- Node upstream client: [`node-backend/src/services/uniguruClient.js`](./node-backend/src/services/uniguruClient.js)

## Compatibility-Only Files

- [`backend/uniguru/bridge/server.py`](./backend/uniguru/bridge/server.py)
- [`backend/uniguru/truth/truth_validator.py`](./backend/uniguru/truth/truth_validator.py)
- [`backend/uniguru/retrieval/kb_engine.py`](./backend/uniguru/retrieval/kb_engine.py)
- [`backend/uniguru/core/engine.py`](./backend/uniguru/core/engine.py)

These files remain to preserve imports and older tooling, but they no longer define a second active runtime pipeline.

## Duplication Removed

- Separate KB engine logic no longer exists
- Node port targeting and upstream `/ask` targeting now respect canonical env precedence
- Bridge no longer performs its own rule-engine-plus-forward orchestration
- Legacy "forward to old system" is no longer the primary production fallback path

## Operational Outputs

- 20-query validation: [`demo_logs/final_validation_20_queries.json`](./demo_logs/final_validation_20_queries.json)
- 30-query live validation: [`demo_logs/final_validation_live.json`](./demo_logs/final_validation_live.json)
- Unified summary: [`FINAL_UNIFIED_VALIDATION.json`](./FINAL_UNIFIED_VALIDATION.json)
