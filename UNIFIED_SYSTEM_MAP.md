# Unified UniGuru System Map

## Status: UNIFIED — One System, One Pipeline

This document is the canonical architecture reference for UniGuru after full system unification.

---

## Single Execution Path

```
UI
 └─► Node middleware (:3000)
       └─► FastAPI /ask (:8000)
             └─► ConversationRouter
                   ├─► ROUTE_UNIGURU → LiveUniGuruService → deterministic KB answer
                   ├─► ROUTE_LLM    → configured LLM endpoint (Ollama / Groq / local)
                   ├─► ROUTE_WORKFLOW → workflow delegation response
                   └─► ROUTE_SYSTEM  → deterministic refusal
```

No other execution path exists. The old VectorDB/RAG bridge and RuleEngine are retired.

---

## What Was Unified (This Task)

| Old System | New System | Outcome |
|---|---|---|
| `RuleEngine` in `core/engine.py` | `ConversationRouter` + `LiveUniGuruService` | RuleEngine retired, marked deprecated |
| `bridge/server.py` as runtime entrypoint | `service/api.py` as sole entrypoint | Bridge marked compatibility-only, not deployed |
| `UNIGURU_BRIDGE_URL` env var pointing to `:8002` | Removed from `.env` | No second system target exists |
| Parallel KB retrieval paths | Single `AdvancedRetriever` in `retrieval/retriever.py` | One retriever, one KB layer |

---

## Where Each Concern Lives

| Concern | File |
|---|---|
| API entrypoint | `backend/uniguru/service/api.py` |
| Routing logic | `backend/uniguru/router/conversation_router.py` |
| KB engine | `backend/uniguru/service/live_service.py` |
| Retriever | `backend/uniguru/retrieval/retriever.py` |
| Knowledge storage | `backend/uniguru/knowledge/` |
| KB ingestion | `scripts/ingest_kb.py` |
| Node middleware | `node-backend/src/routes/queryRoutes.js` |
| Node upstream client | `node-backend/src/services/uniguruClient.js` |
| Governance preflight | `backend/uniguru/service/governance_preflight.py` |

---

## KB Layer

- Markdown files: `backend/uniguru/knowledge/` (quantum, jain, swaminarayan, gurukul)
- JSON datasets: `backend/uniguru/knowledge/datasets/` (ankita, nupur)
- Runtime index: `backend/uniguru/knowledge/index/master_index.json`
- All sources loaded by one retriever: `AdvancedRetriever` in `retrieval/retriever.py`
- Confidence threshold: `UNIGURU_KB_CONFIDENCE_THRESHOLD=0.25` (env-configurable)

---

## LLM Layer

- LLM is called only when KB cannot answer (`ROUTE_LLM` fallback)
- Endpoint: `UNIGURU_LLM_URL` (default: `http://127.0.0.1:11434/api/generate`)
- Model: `UNIGURU_LLM_MODEL` (default: `llama3`)
- If LLM is unreachable: safe fallback phrase returned, no 503
- Safe fallback phrase: `"I am still learning this topic, but here is a basic explanation..."`

---

## Node Integration Routes

| Route | Caller identity |
|---|---|
| `POST /api/v1/chat/query` | `uniguru-frontend` |
| `POST /api/v1/gurukul/query` | `gurukul-platform` |
| `POST /api/v1/samachar/query` | `samachar-platform` |

All three routes forward to the same `POST /ask` on the Python backend.

---

## Retired / Compatibility-Only

These files exist but are NOT part of the active runtime:

- `backend/uniguru/core/engine.py` — RuleEngine, deprecated header added
- `backend/uniguru/bridge/server.py` — compatibility bridge, deprecated header added, not deployed
- `backend/uniguru/retrieval/kb_engine.py` — wrapper, delegates to canonical retriever
- `backend/uniguru/truth/truth_validator.py` — compatibility wrapper

---

## Deployable Entry Points

```bash
# Python backend
python -m uvicorn uniguru.service.api:app --host 0.0.0.0 --port 8000

# Node middleware
node node-backend/src/server.js
```

Or via run scripts:
```
run/run_backend.ps1   (Windows)
run/run_backend.sh    (Linux/macOS)
run/run_node.ps1      (Windows)
run/run_node.sh       (Linux/macOS)
```

---

## Validation

- 20-query validation (20/20): `demo_logs/final_validation_20_queries.json`
- 30-query live validation (30/30): `demo_logs/final_validation_live.json`
- Unified summary: `FINAL_UNIFIED_VALIDATION.json`
