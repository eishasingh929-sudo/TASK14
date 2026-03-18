# BRIDGE_CONNECTION_REPORT

Date: 2026-02-25

## Bridge Target Update
- Updated bridge forwarding target from:
  - `http://127.0.0.1:8080/chat`
- To:
  - `http://localhost:8000/api/v1/chat/new`
- Implemented as env-overridable setting:
  - `UNIGURU_BACKEND_URL` (default: `http://localhost:8000/api/v1/chat/new`)

## Request Flow Validation
Bridge ran on `http://127.0.0.1:8100` and backend test service on `http://127.0.0.1:8000`.

### Example 1: KB Answer (No Forward)
Request:
```json
{"message":"What is a qubit?","session_id":"s1","source":"demo"}
```
Observed bridge status:
```json
{"status":"answered","enforced":true}
```

### Example 2: Forwarded to UniGuru Backend
Request:
```json
{"message":"Tell me latest GDP projection","session_id":"s2","source":"demo"}
```
Observed bridge status and forwarded backend payload:
```json
{
  "status":"forwarded",
  "legacy_response":{
    "answer":"[backend] Tell me latest GDP projection",
    "session_id":"s2",
    "model":"mock-node"
  },
  "enforced":true
}
```

## Full Response Trace (Forward Case)
- SafetyRule: allow
- AuthorityRule: allow
- DelegationRule: allow
- EmotionalRule: allow
- AmbiguityRule: allow
- RetrievalRule: allow (no KB match)
- ForwardRule: forward
