# UNIGURU_FLOW

## Simple Runtime Flow
1. Product user or Gurukul sends query to API consumer layer.
2. API consumer enters Node middleware:
   - Product: `POST /api/v1/chat/query`
   - Gurukul: `POST /api/v1/gurukul/query`
3. Node builds canonical payload and forwards to Python API `POST /ask` with `context.caller`.
4. Python API validates payload, token, caller allowlist, and queue/rate limits.
5. API sends normalized query to Conversation Router.
6. Router chooses route:
   - `ROUTE_UNIGURU` for knowledge queries
   - `ROUTE_LLM` for open/general chat
   - `ROUTE_WORKFLOW` for workflow/tool intents
   - `ROUTE_SYSTEM` for system-command intents (blocked)
7. If `ROUTE_UNIGURU`, service runs rule engine + retrieval + verification + enforcement.
8. API returns structured response (decision, answer, verification, routing, signature).
9. Node returns response to consumer:
   - preserves upstream HTTP error codes (401/403/503/etc.)
   - applies UI-safe KB answer compaction and keeps full text in `raw_answer`.

## When KB is used
- KB is used when router classifies query as `KNOWLEDGE_QUERY` and route = `ROUTE_UNIGURU`.
- Retrieval pulls from local markdown knowledge files and verifies source confidence.

## When LLM is used
- LLM is used when router selects `ROUTE_LLM`.
- LLM is also used as fallback if UniGuru latency breaker opens, or if unverified fallback is enabled.
- LLM route requires `UNIGURU_LLM_URL`; without it, route returns a configuration message.
- Node adds `integration_notes` for this state so consumers can detect fallback-unavailable behavior.

## When system blocks
- Router blocks system-command type queries (`ROUTE_SYSTEM`).
- Rule engine/governance can block unsafe or disallowed content.
- API blocks early on auth/caller/queue failures (for example 401/403/503).
