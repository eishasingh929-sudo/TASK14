# Unified UniGuru System Map

## Canonical Decision

UniGuru now has one active execution path:

`UI -> Node middleware -> FastAPI /ask -> ConversationRouter -> deterministic KB or LLM fallback -> response`

The old "legacy bridge -> rule engine -> downstream legacy backend" model is no longer the active runtime architecture.

## What Survives

- Deterministic routing in [`backend/uniguru/router/conversation_router.py`](./backend/uniguru/router/conversation_router.py)
- Canonical KB engine in [`backend/uniguru/service/live_service.py`](./backend/uniguru/service/live_service.py)
- Dataset ingestion in [`scripts/ingest_kb.py`](./scripts/ingest_kb.py) and [`backend/uniguru/loaders/ingestor.py`](./backend/uniguru/loaders/ingestor.py)
- Node middleware integration in [`node-backend/src/routes/queryRoutes.js`](./node-backend/src/routes/queryRoutes.js)
- Real LLM fallback wiring in [`backend/uniguru/router/conversation_router.py`](./backend/uniguru/router/conversation_router.py)

## What Was Unified

- Markdown KB, JSON datasets, and the old runtime keyword index now flow through one retriever in [`backend/uniguru/retrieval/retriever.py`](./backend/uniguru/retrieval/retriever.py)
- Preflight governance is shared through [`backend/uniguru/service/governance_preflight.py`](./backend/uniguru/service/governance_preflight.py)
- Compatibility helpers now delegate into the canonical path:
  - [`backend/uniguru/retrieval/kb_engine.py`](./backend/uniguru/retrieval/kb_engine.py)
  - [`backend/uniguru/truth/truth_validator.py`](./backend/uniguru/truth/truth_validator.py)
  - [`backend/uniguru/bridge/server.py`](./backend/uniguru/bridge/server.py)

## What No Longer Owns Runtime Flow

- `RuleEngine` is no longer the primary `/ask` execution pipeline
- The bridge is compatibility-only, not the canonical entrypoint
- The old standalone KB engine is now a wrapper, not a separate retriever
- "Legacy system processing" is no longer the fallback contract

## Final Execution Flow

1. Node receives product traffic on `/api/v1/chat/query`, `/api/v1/gurukul/query`, or `/api/v1/samachar/query`.
2. Node normalizes payload shape, caller identity, auth token, and upstream `/ask` target.
3. FastAPI `/ask` validates schema, caller, auth, throttling, and metrics.
4. `ConversationRouter` runs preflight governance and picks exactly one route:
   - `ROUTE_UNIGURU`
   - `ROUTE_LLM`
   - `ROUTE_WORKFLOW`
   - `ROUTE_SYSTEM`
5. `ROUTE_UNIGURU` calls the canonical deterministic KB engine.
6. If KB cannot answer and fallback is allowed, router sends the query to the configured LLM endpoint.
7. Response metadata, verification status, enforcement signature, and presentation payload are returned to Node and then to the UI.

## Responsibility Map

- Routing: [`backend/uniguru/router/conversation_router.py`](./backend/uniguru/router/conversation_router.py)
- KB and verification: [`backend/uniguru/service/live_service.py`](./backend/uniguru/service/live_service.py)
- Knowledge storage:
  - [`backend/uniguru/knowledge/`](./backend/uniguru/knowledge/)
  - [`backend/uniguru/knowledge/index/master_index.json`](./backend/uniguru/knowledge/index/master_index.json)
- Ingestion: [`scripts/ingest_kb.py`](./scripts/ingest_kb.py)
- Node integration: [`node-backend/src/services/uniguruClient.js`](./node-backend/src/services/uniguruClient.js)
- API entrypoint: [`backend/uniguru/service/api.py`](./backend/uniguru/service/api.py)

## LLM Placement

- LLM calls happen only inside router fallback handling.
- The deterministic KB path never calls the LLM.
- Health and readiness now fast-fail LLM discovery instead of blocking service startup.

## Deployable Entry Points

- Python API: `python -m uvicorn uniguru.service.api:app`
- Node middleware: `node node-backend/src/server.js`

## Validation Sources

- [`demo_logs/final_validation_20_queries.json`](./demo_logs/final_validation_20_queries.json)
- [`demo_logs/final_validation_live.json`](./demo_logs/final_validation_live.json)
- [`FINAL_UNIFIED_VALIDATION.json`](./FINAL_UNIFIED_VALIDATION.json)
