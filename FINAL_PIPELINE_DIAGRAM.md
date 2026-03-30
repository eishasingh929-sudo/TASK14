# Final Pipeline Diagram — Unified UniGuru

## Single Canonical Pipeline

```text
Frontend / UI
      |
      v
Node Middleware (:3000)
  POST /api/v1/chat/query      → caller: uniguru-frontend
  POST /api/v1/gurukul/query   → caller: gurukul-platform
  POST /api/v1/samachar/query  → caller: samachar-platform
      |
      | normalises payload, sets caller identity, forwards to /ask
      v
FastAPI /ask (:8000)
  - schema validation (Pydantic)
  - caller allowlist enforcement
  - auth / rate limiting / queue guard
  - language normalisation
      |
      v
ConversationRouter
  - governance preflight (safety / emotional / ambiguity)
  - deterministic pattern classification
      |
      +--[ROUTE_SYSTEM]----> block response (dangerous command patterns)
      |
      +--[ROUTE_WORKFLOW]--> workflow delegation response
      |
      +--[ROUTE_UNIGURU]--> LiveUniGuruService
      |                        AdvancedRetriever
      |                          - markdown KB (quantum / jain / swaminarayan / gurukul)
      |                          - JSON datasets (ankita / nupur)
      |                          - runtime index (master_index.json)
      |                        SourceVerifier + OntologyRegistry
      |                        enforcement seal
      |                             |
      |                    [KB match, confidence >= 0.25]
      |                             |
      |                             +--> VERIFIED answer returned
      |                             |
      |                    [no KB match]
      |                             |
      +-----------------------------+
                                    |
                                    v
                             ROUTE_LLM fallback
                               configured LLM endpoint
                               (UNIGURU_LLM_URL / UNIGURU_LLM_MODEL)
                               circuit breaker + health probe
                               safe fallback phrase if LLM unreachable
                                    |
                                    v
                             Node presentation formatter
                             (responseFormatter.js)
                                    |
                                    v
                               UI response
                          { answer, route, verification_status, ... }
```

## Route Contract

| Route | Trigger | Guarantee |
|---|---|---|
| `ROUTE_UNIGURU` | KB domain query with confidence ≥ 0.25 | VERIFIED answer from local KB |
| `ROUTE_LLM` | General / open-domain query, or KB miss | Real LLM response or safe fallback phrase |
| `ROUTE_WORKFLOW` | Workflow / task orchestration pattern | Delegation acknowledgement |
| `ROUTE_SYSTEM` | Dangerous command pattern | Deterministic block, no LLM call |

## Safe Fallback Guarantee

If LLM is unreachable, every response still contains a non-empty answer:

```
"I am still learning this topic, but here is a basic explanation..."
```

No 503. No empty body. No crash.

## Retired Paths (Not In Pipeline)

The following files exist for import compatibility only and are NOT deployed or called at runtime:

- `backend/uniguru/core/engine.py` — old RuleEngine (deprecated)
- `backend/uniguru/bridge/server.py` — old bridge server (deprecated, not started)
- `backend/uniguru/retrieval/kb_engine.py` — thin wrapper, delegates to canonical retriever
- `backend/uniguru/truth/truth_validator.py` — compatibility wrapper
