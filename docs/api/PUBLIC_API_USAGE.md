# PUBLIC_API_USAGE

## Base URL
`https://uni-guru.in`

Direct host ports for deployment:
- `http://<HOST_OR_IP>:8000/ask`
- `http://<HOST_OR_IP>:3000/api/v1/chat/query`

## Authentication
All requests to protected endpoints MUST include the `Authorization` header:
`Authorization: Bearer <your_access_token>`

## Caller Identification
Callers MUST identify themselves via:
- JSON field: `context.caller`
- OR Header: `X-Caller-Name`

Supported callers: `bhiv-assistant`, `gurukul-platform`, `samachar-platform`, `internal-testing`, `uniguru-frontend`.

If auth is enabled:
- Missing or invalid token -> `401`
- Unknown caller -> `403`

## Endpoints

### 1. Ask (POST /ask)
Primary reasoning endpoint.
**Payload:**
```json
{
  "query": "What is ahimsa?",
  "context": {
    "caller": "bhiv-assistant"
  },
  "allow_web": false
}
```

### 2. External UI (POST /api/v1/chat/query)
Node middleware endpoint for NIC or other frontend callers.

### 3. Gurukul (POST /api/v1/gurukul/query)
Specialized Node middleware endpoint for Gurukul student traffic.

### 4. Samachar (POST /api/v1/samachar/query)
Specialized Node middleware endpoint for news-style or bulletin traffic.

### 5. Health (GET /health)
Public health status (no auth).
```json
{
  "status": "ok",
  "service": "uniguru-live-reasoning",
  "version": "1.1.0"
}
```

### 6. Metrics (GET /metrics)
Prometheus compatible metrics (requires auth).

### 7. Dashboard (GET /monitoring/dashboard)
Structured live dashboard data (requires auth).
