# EXECUTION_CONTRACT.md

## Purpose

This document defines the **end-to-end execution contract** of Unified UniGuru.

It exists so that a new engineer can understand exactly:
- Where requests enter
- How they are processed
- What decisions are possible
- How responses are returned

This is the formal runtime contract of the system.

---

## 1. Public Entry Point

All external requests MUST enter through the Gateway:

POST /admit

Location:
gateway/app.py

No client is allowed to call the legacy `/chat` endpoint directly.

This guarantees governance and safety.

---

## 2. Request Contract

Every request must follow this JSON schema:

```json
{
  "message": "string",
  "session_id": "string",
  "source": "string"
}
Validation performed at the gateway:

JSON must be valid

Required fields must exist

Payload size must be within limits

Invalid requests are rejected immediately.

3. Execution Pipeline

Every request follows this pipeline:

Client
  ↓
Gateway (/admit)
  ↓
RLM Rule Engine
  ↓
Decision Gate
  ↓
[BLOCK | ANSWER | FORWARD]


No bypass paths exist.

4. Decision Contract

The Rule Engine must produce one terminal decision.

Decision	Meaning
BLOCK	Reject request
ANSWER	Deterministic response
FORWARD	Send to legacy Node system

A request cannot produce multiple decisions.

5. BLOCK Flow

When a request is blocked:

Processing stops immediately

No retrieval occurs

No legacy call occurs

Response format:

{
  "trace_id": "uuid",
  "allowed": false,
  "reason": "string"
}

6. DIRECT ANSWER Flow

When a deterministic answer is produced:

Retrieval engine is used

Legacy system is NOT called

Response format:

{
  "trace_id": "uuid",
  "data": {
    "answer": "string"
  }
}

7. FORWARD Flow

When a request is safe but not handled deterministically:

Gateway calls the legacy system:

POST http://localhost:8080/chat


Important rules:

Payload must not be modified

Timeout must be enforced

Failures must return 502 safely

8. Legacy Response Contract

Expected response from legacy system:

{
  "answer": "string",
  "source": "string",
  "confidence": "number"
}


Gateway attaches trace_id before returning to client.

9. Response Contract (Final)

Every response from UniGuru must include:

{
  "trace_id": "uuid"
}


This ensures full traceability.

10. Observability Requirements

Each request must log:

Request received

Rule decisions

Retrieval execution (if used)

Forwarding events (if used)

Final response status

Logs must be reproducible using the trace_id.

11. Execution Guarantee

The following must always be true:

No request bypasses the gateway

No request bypasses the rule engine

Unsafe requests never reach the legacy system

Every request produces a deterministic decision

Summary

Unified UniGuru now operates under a strict execution contract:

Request → Governance → Reasoning → Retrieval → Generation → Response