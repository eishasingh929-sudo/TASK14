# Final Pipeline Diagram

```text
Frontend / UI
    |
    v
Node Middleware
  - /api/v1/chat/query
  - /api/v1/gurukul/query
  - /api/v1/samachar/query
    |
    v
FastAPI /ask
  - schema validation
  - caller validation
  - auth / metrics / throttling
    |
    v
ConversationRouter
  - governance preflight
  - deterministic route selection
    |
    +--> ROUTE_SYSTEM ----> deterministic refusal
    |
    +--> ROUTE_WORKFLOW --> workflow delegation response
    |
    +--> ROUTE_UNIGURU --> LiveUniGuruService
    |                       - canonical retriever
    |                       - KB verification
    |                       - ontology / reasoning trace
    |                       - enforcement
    |                            |
    |                            +--> verified KB answer
    |                            |
    |                            +--> no KB answer
    |                                     |
    +-------------------------------------+
                                          |
                                          v
                                   ROUTE_LLM fallback
                                   - configured LLM endpoint
                                   - structured answer contract
                                          |
                                          v
                                   Node presentation formatter
                                          |
                                          v
                                       UI response
```

## Route Contract

- Knowledge and support-domain queries: `ROUTE_UNIGURU`
- Open-domain or general chat queries: `ROUTE_LLM`
- Explicit workflow/task orchestration requests: `ROUTE_WORKFLOW`
- System or dangerous command patterns: `ROUTE_SYSTEM`

## Compatibility Note

`backend/uniguru/bridge/server.py`, `backend/uniguru/truth/truth_validator.py`, and `backend/uniguru/retrieval/kb_engine.py` still exist for compatibility, but each now delegates back into this same pipeline.
