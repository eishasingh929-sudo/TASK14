# SYSTEM_ENTRYPOINT.md

## Purpose

This document defines the **single entry point** of the Unified UniGuru system and explains how requests enter and move through the system.

This ensures any new developer can run and understand the system from zero knowledge.

---

## Public System Entry Point

The Unified UniGuru system exposes **one public HTTP endpoint**:

POST /chat

This endpoint is implemented in:

bridge/server.py

The bridge server is the only component that accepts external requests.

No other component should be directly exposed.

---

## Why a Single Entry Point Exists

The legacy UniGuru system previously received user requests directly.

Now, all requests must pass through the UniGuru reasoning middleware first to ensure:

- Governance enforcement
- Safety validation
- Deterministic reasoning
- Knowledge retrieval
- Trace logging

This guarantees that no unsafe or uncontrolled request can reach the legacy system.

---

## Request Lifecycle

### Step 1 — User Request

A client sends a request:

```json
POST /chat

{
  "message": "User question",
  "session_id": "string",
  "source": "web"
}
This request reaches the Bridge Server.
Step 2 — Bridge Server Processing

File:

bridge/server.py


Responsibilities:

Receive request

Validate JSON structure

Generate trace_id

Send request to Rule Engine

Step 3 — Rule Engine Execution

File:

core/engine.py


The rule engine evaluates the request using the following layers:

Enforcement (UnsafeRule)

Governance Rules:

AuthorityRule

DelegationRule

EmotionalRule

AmbiguityRule

RetrievalRule

ForwardRule

The engine returns a decision:

Decision	Meaning
BLOCK	Reject request
ANSWER	Respond using KB
FORWARD	Send to legacy UniGuru
Step 4 — Decision Handling
If BLOCK

Bridge returns rejection response immediately.

If ANSWER

Bridge calls Retrieval Engine and returns deterministic answer.

If FORWARD

Bridge forwards request to Legacy UniGuru.

Step 5 — Legacy UniGuru Call

Endpoint (local):

http://localhost:8080/chat


The legacy system:

Runs RAG pipeline

Calls LLM

Generates response

Bridge receives the response and sends it back to the user.

Final Response Format

All responses include a trace ID:

{
  "trace_id": "uuid",
  "data": {
    "answer": "Final response"
  }
}


This guarantees full observability.

Summary

There is now one official entrypoint to UniGuru:

User → Bridge → Rule Engine → Retrieval / Legacy → Response

The system is now ready for middleware integration.