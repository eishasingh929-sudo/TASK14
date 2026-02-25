# UniGuru Admission Layer API Contract

**Base URL**: `http://localhost:3000`

---

## 1. POST /admit
The primary admission endpoint for all requests intended for UniGuru Core.

### Request
**Headers**:
- `Content-Type: application/json`
- `Content-Length: <integer>` (Must be <= 1MB)

**Body**:
Any JSON object required by UniGuru. The middleware does not enforce schema validation on the *content* itself, only *structural safety*.

**Example**:
```json
{
  "user_id": "u123",
  "action": "query_grades",
  "payload": { "sem": 5 }
}
```

### Response Scenarios

#### Scenario A: Allowed (Success)
If validation passes, the request is forwarded to `TARGET_URL`. The response from UniGuru is returned directly.
**Status**: `200 OK` (or whatever the upstream returns).
**Body**: Passed from UniGuru.

#### Scenario B: Rejected (Validation Failure)
If validation fails (unsafe content, empty body, etc.).
**Status**: `400 Bad Request`
**Body**:
```json
{
  "allowed": false,
  "reason": "Unsafe tokens detected in payload",
  "timestamp": "2023-10-27T10:00:00.000Z",
  "trace_id": "uuid-v4-string"
}
```

#### Scenario C: Payload Too Large
If body exceeds 1MB.
**Status**: `413 Payload Too Large`
**Body**:
```json
{
  "allowed": false,
  "reason": "Payload exceeds size limit (1MB)",
  "timestamp": "...",
  "trace_id": "uuid-v4-string"
}
```

#### Scenario D: Forwarding Failure
If upstream (UniGuru Core) is unreachable or times out (5s).
**Status**: `502 Bad Gateway`
**Body**:
```json
{
  "allowed": true,
  "forwarded": false,
  "error": "Upstream service unavailable or error",
  "details": "connect ECONNREFUSED 127.0.0.1:8080",
  "trace_id": "uuid-v4-string",
  "timestamp": "..."
}
```

---

## 2. GET /health
Basic health check.

**Status**: `200 OK`
**Body**: `{"status": "ok", "service": "uniguru-admission-layer"}`
