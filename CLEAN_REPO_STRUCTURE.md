# Clean Repo Structure — Unified UniGuru

## Status: ONE system. ONE pipeline. ONE deployable.

---

## Active Runtime Surface

```
backend/
  main.py                              ← Python entrypoint (uvicorn)
  uniguru/
    service/
      api.py                           ← FastAPI app, /ask endpoint
      live_service.py                  ← Deterministic KB engine
      governance_preflight.py          ← Shared preflight governance
      query_classifier.py              ← Query type classification
      response_format.py               ← Structured answer builder
    router/
      conversation_router.py           ← Route selection + LLM fallback
    retrieval/
      retriever.py                     ← AdvancedRetriever (single KB source)
      web_retriever.py                 ← Optional web retrieval
    knowledge/
      quantum/                         ← Quantum KB (markdown)
      jain/                            ← Jain KB (markdown)
      swaminarayan/                    ← Swaminarayan KB (markdown)
      gurukul/                         ← Gurukul KB (markdown)
      datasets/
        ankita/                        ← Admissions support (JSON)
        nupur/                         ← Career/placement support (JSON)
      index/
        master_index.json              ← Runtime keyword index
    enforcement/                       ← Response sealing
    governance/                        ← Output guard
    ontology/                          ← Concept registry + graph
    reasoning/                         ← Trace generation

node-backend/
  src/
    server.js                          ← Node entrypoint (:3000)
    app.js                             ← Express app
    routes/
      queryRoutes.js                   ← /api/v1/chat|gurukul|samachar/query
    services/
      uniguruClient.js                 ← Upstream /ask caller
      responseFormatter.js             ← Presentation formatter

scripts/
  ingest_kb.py                         ← Dataset ingestion pipeline

run/
  run_backend.ps1 / run_backend.sh     ← Start Python backend
  run_node.ps1 / run_node.sh           ← Start Node middleware

test/
  run_final_validation_live.py         ← 30-query live validation
  run_final_validation_20_queries.py   ← 20-query validation
  run_phase8_validation.py             ← Phase 8 checks
  run_demo_safety_proof.py             ← Failure injection proof

config/
  env/.env.example                     ← Environment template
```

---

## Canonical Files (6 that define the entire runtime)

| File | Role |
|---|---|
| `backend/uniguru/service/api.py` | FastAPI app, all endpoints |
| `backend/uniguru/router/conversation_router.py` | Route selection + LLM fallback |
| `backend/uniguru/service/live_service.py` | KB engine + verification |
| `backend/uniguru/retrieval/retriever.py` | Single retriever for all KB sources |
| `node-backend/src/routes/queryRoutes.js` | All Node integration routes |
| `node-backend/src/services/uniguruClient.js` | Node → Python upstream client |

---

## Retired / Compatibility-Only (NOT in active pipeline)

| File | Status | Reason |
|---|---|---|
| `backend/uniguru/core/engine.py` | Deprecated | Old RuleEngine, replaced by ConversationRouter |
| `backend/uniguru/bridge/server.py` | Deprecated | Old bridge server, not deployed |
| `backend/uniguru/retrieval/kb_engine.py` | Wrapper only | Delegates to canonical retriever |
| `backend/uniguru/truth/truth_validator.py` | Wrapper only | Compatibility shim |

---

## Duplication Removed in This Task

| What was removed | How |
|---|---|
| Second execution path via RuleEngine | Deprecated header added to `core/engine.py` |
| Bridge as runtime entrypoint | Deprecated header added to `bridge/server.py` |
| `UNIGURU_BRIDGE_URL` env var (`:8002`) | Removed from `.env` |
| Parallel KB retrieval logic | Single `AdvancedRetriever` is the only retriever |
| Confusion in architecture docs | All 4 canonical docs updated to reflect one pipeline |

---

## Environment Variables (Canonical Set)

```env
UNIGURU_HOST=0.0.0.0
UNIGURU_PORT=8000
NODE_BACKEND_PORT=3000
UNIGURU_ASK_URL=http://localhost:8000/ask
UNIGURU_API_AUTH_REQUIRED=false
UNIGURU_API_TOKEN=secure_token
UNIGURU_ALLOWED_CALLERS=bhiv-assistant,gurukul-platform,samachar-platform,internal-testing,uniguru-frontend
UNIGURU_LLM_URL=http://localhost:11434/api/generate
UNIGURU_LLM_MODEL=gpt-oss:120b-cloud
UNIGURU_LLM_TIMEOUT_SECONDS=12
UNIGURU_KB_CONFIDENCE_THRESHOLD=0.25
UNIGURU_METRICS_STATE_FILE=demo_logs/metrics_state.json
```

---

## Validation Outputs

| File | Queries | Result |
|---|---|---|
| `demo_logs/final_validation_20_queries.json` | 20 | 20/20 passed |
| `demo_logs/final_validation_live.json` | 30 | 30/30 passed |
| `FINAL_UNIFIED_VALIDATION.json` | 50 combined | 50/50 passed, 0 failures |
