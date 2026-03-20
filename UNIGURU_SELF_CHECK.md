# UNIGURU_SELF_CHECK

## 1) Which is your main backend file?
- `backend/uniguru/service/api.py`

## 2) Which file actually runs the router?
- `backend/uniguru/service/api.py` creates `ConversationRouter` and calls `route_query(...)`.
- Router implementation itself is in `backend/uniguru/router/conversation_router.py`.

## 3) Where does KB live?
- Main KB content: `backend/uniguru/knowledge/**`
- Retrieval path using it: `backend/uniguru/retrieval/retriever.py` via `backend/uniguru/core/rules/retrieval.py`

## 4) Why does system fail currently?
- Frequent `503` because auth is required but token setup is inconsistent/missing in runtime.
- LLM route often cannot answer because `UNIGURU_LLM_URL` is not configured.
- Documentation and legacy files still mix old and current paths, causing integration confusion.
- Fragmentation exists across backend, node middleware, frontend, and legacy app folders; wrong entrypoint selection causes avoidable failures.

## 5) What needs to be fixed for integration?
- Set and align `UNIGURU_API_TOKEN` across Python API, Node middleware, and deployment env.
- Keep one canonical runtime path: `Node /api/v1/* -> Python /ask` (avoid legacy bridge as primary path).
- Decide and configure LLM fallback endpoint (`UNIGURU_LLM_URL`) or explicitly disable that path for testing.
- Keep current docs only; mark legacy docs/files as non-canonical for Yashika and Tiwari.
- Use Node-formatted response (`answer` + `raw_answer`) for UI consumers to avoid raw KB dumps.
