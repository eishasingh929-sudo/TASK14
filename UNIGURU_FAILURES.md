# UNIGURU_FAILURES

## 1) Why 503 error happens
- Service auth is enabled, but no API token is configured (`UNIGURU_API_AUTH_REQUIRED=true` and token missing). In this case `/ask` returns `503` before routing.
- Router queue guard returns `503` when inflight requests exceed `UNIGURU_ROUTER_QUEUE_LIMIT`.
- Voice route returns `503` when STT engine is unavailable.

## 2) Why auth fails
- Missing or wrong Bearer token causes `401` on protected endpoints.
- Missing caller identity causes `400`; caller not in allowlist causes `403`.
- Integration fails when Node token/env does not match Python token/env.
- Token header mismatch previously caused confusion; runtime now accepts both:
  - `Authorization: Bearer <token>`
  - `X-Service-Token: <token>`

## 3) Why KB gives raw output
- Retrieval currently returns full markdown content from KB files, not a summarized answer layer.
- `RetrievalRule` prepends a fixed header and then returns the KB body directly, so responses look like raw document dumps.
- Integration fix applied: Node middleware now compacts KB-heavy answers for chat UI and preserves full source in `raw_answer`.

## 4) Why Python / 2+2 gets blocked
- In the current environment, these requests often fail early with `503` because auth is required but token is not configured.
- After auth is fixed, short/general prompts like `python` or `2+2` go to `ROUTE_LLM`; if `UNIGURU_LLM_URL` is not set, no real LLM answer is produced.
- Query form like `What is 2+2?` goes through KB route, and if no verified KB match exists (and web is not allowed), response is blocked as `UNVERIFIED`.
- Integration fix applied: Node now returns real upstream status codes (not generic 502), so Tiwari can see true blocker source.
