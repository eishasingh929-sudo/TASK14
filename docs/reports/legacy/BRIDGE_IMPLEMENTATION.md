# Bridge Implementation

## Purpose
The UniGuru Bridge serves as the primary intelligence and safety middleware layer for the system. It ensures that all incoming user requests are processed by the deterministic `RuleEngine` before any further action is taken.

## Endpoint: `POST /chat`
The bridge exposes a single unified endpoint for chat interactions.

### Request Schema
```json
{
  "message": "string",
  "session_id": "string",
  "source": "string"
}
```

### Response Schema
```json
{
  "trace_id": "uuid",
  "decision": {
    "request_id": "uuid",
    "decision": "allow|block|answer|forward",
    "reason": "string",
    "response_content": "string",
    "rule_triggered": "string",
    "total_latency_ms": "number",
    "metadata": "object",
    "trace": "array"
  },
  "latency_ms": "number"
}
```

## System Flow
The current implementation follows Phase 1 of the middleware bridge:
1. **User Request**: Client sends a JSON payload to the Bridge.
2. **Bridge Processing**: Bridge receives the request, generates a `trace_id`.
3. **Rule Engine**: Bridge calls the `RuleEngine` from `core.engine`.
4. **Deterministic Evaluation**: The engine evaluates Governance and Enforcement rules.
5. **Response**: The bridge returns the engine's decision and trace information directly to the user.

## Note on Legacy System
Currently, the "FORWARD" decision does not trigger a call to the legacy Node.js system. Connection to the legacy production backend is scheduled for **Day 3**.
