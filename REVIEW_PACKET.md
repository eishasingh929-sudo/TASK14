# UniGuru System Execution Flow (Integration Aware)

## 1. ENTRY POINT & MIDDLEWARE

**Frontend to Node Middleware:**
Path: `node-backend/src/routes/queryRoutes.js`
The system begins at the Node.js middleware wrapper (e.g., `/api/v1/chat/query` or `/api/v1/gurukul/query`). This middleware processes the initial request from external consumers (e.g., React frontend or BHIV assistant).

**Node to Python Execution:**
Path: `node-backend/src/services/uniguruClient.js`
The Node layer acts as an integration bridge, securely passing the query, caller identity, and context downstream to the Python backend via the `/ask` endpoint. 

**Backend Orchestration:**
Path: `backend/uniguru/service/api.py`
The FastAPI service validates incoming requests, enforces Service Token Authentication, and hands off the query to the Conversation Router.

---

## 2. CORE RUNTIME FLOW & PATHS

**Path A: Deterministic Knowledge (ROUTE_UNIGURU)**
Path: `backend/uniguru/core/engine.py`
Queries identifying as Knowledge queries invoke the Ontology Rule Engine to fetch snapshots and determine an exact, verifiable answer.

**Path B: LLM Fallback & Chat (ROUTE_LLM)**
Path: `backend/uniguru/router/conversation_router.py`
If a query is unverified, open-ended, or the KB engine fails to produce a deterministic answer, the router automatically delegates the query to `ROUTE_LLM`. The query is forwarded to an external Language Model configured by `UNIGURU_LLM_URL`.

---

## 3. REAL SYSTEM INTEGRATION CONTEXT

### Authentication & Token Passing
Tokens are handled exclusively via `.env` variables and propagated through standard headers.
The Node layer relies on `UNIGURU_API_TOKEN`, which it passes upstream to the Python backend in the `Authorization: Bearer <token>` or `X-Service-Token` header. The Python `api.py` layer compares this incoming token against its own string of valid `UNIGURU_API_TOKENS`.

### Environment Dependencies
- **Node Layer Dependencies:** `UNIGURU_ASK_URL` and `UNIGURU_API_TOKEN`.
- **Python Layer Dependencies:** `UNIGURU_LOG_LEVEL`, `UNIGURU_LLM_URL`, `UNIGURU_ROUTER_LATENCY_THRESHOLD_MS`, and `UNIGURU_API_AUTH_REQUIRED`.

---

## 4. FAILURE HANDLING & FALLBACK STRATEGY

Unlike standalone operation, failures in production DO NOT result in a direct 503 crash or loss of context for the end user.

- **Python Layer Resiliency:** If routing queue saturation occurs, or there are unhandled exceptions/latency spikes, the `api.py` component intercepts these events and returns a smooth `_build_safe_fallback_response`.
- **Node Layer Middleware Resiliency (Critical):** If the Python upstream server is entirely offline, the connection drops, or a severe 5xx error slips out, the Node middleware catches the `UniGuruUpstreamError`. It responds to the caller with a controlled HTTP 200 OK status containing:
  ```json
  {
    "success": true,
    "degraded": true,
    "source": "node-backend-safe-fallback",
    "data": { ... }
  }
  ```
  This guarantees no blank screens or raw stack traces degrade the user experience.

---

## 5. SETUP & EXECUTION INSTRUCTIONS

To run the full integrated path:

### Environment Setup
1. Copy `.env.example` to `.env` in the root.
2. Provide aligned secure values for `UNIGURU_API_TOKEN` in both Node and Python environments.
3. Ensure the Node `.env` correctly maps `UNIGURU_ASK_URL=http://localhost:8000/ask`.

### Option A: Manual Local Execution
**1. Python Backend**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn uniguru.service.api:app --host 0.0.0.0 --port 8000
```
**2. Node Middleware**
```bash
cd node-backend
npm install
npm start
```
The Node API will be accessible on the configuration-defined port (usually 3000), acting as the true API gateway.

### Option B: Docker Compose (Recommended)
Simply spin up the ecosystem utilizing the composed containers:
```bash
docker-compose up --build
```
This isolates dependencies and simulates true integration conditions.
