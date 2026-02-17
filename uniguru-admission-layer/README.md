# UniGuru Admission Layer

A deterministic admission gateway that sits in front of the UniGuru server. This service intercepts all incoming requests, validates them against a set of security rules, and forwards allowed requests to the legacy UniGuru server.

---

## 🏗 Architecture

The Admission Layer acts as a **Reverse Proxy Middleware** with a built-in deterministic rule engine.

1. Incoming Request → Client sends POST request to `http://localhost:3000/admit`
2. Traceability → A unique UUID trace ID is generated
3. Rule Engine → Payload validated deterministically
4. Decision  
   - Rejected → return **400 Bad Request**  
   - Allowed → forward to UniGuru server
5. Forwarding → Axios call to `http://localhost:8080/chat` (5s timeout)
6. Response → UniGuru response returned with trace ID

---

## 🔒 Isolation Guarantee

This repository is fully **isolated** and does **NOT modify the existing UniGuru codebase**.

The legacy UniGuru server is treated as a read-only dependency running locally on port **8080**.  
This project acts purely as an **admission gateway in front of it**.

---

## 🚀 Setup Steps

### Prerequisites
- Node.js (v14+)
- npm

### Installation
```bash
cd uniguru-admission-layer
npm install

Run Server
npm run dev


Server runs at:

http://localhost:3000

🧪 Testing
Unit Tests
npm test

Integration Test
node tests/integration/testFlow.js


If UniGuru is offline → 502 response is expected.

📝 API Contract
Endpoint
POST /admit

Request Body
{
  "message": "string",
  "session_id": "string",
  "source": "string"
}

Response — Rejected
{
  "allowed": false,
  "reason": "Unsafe content detected",
  "timestamp": "ISO date",
  "trace_id": "uuid"
}

Response — Allowed
{
  "data": {
    "answer": "Response from UniGuru"
  },
  "trace_id": "uuid"
}

📊 Deterministic Decision Object

Every request produces a deterministic decision:

{
  "allowed": true/false,
  "reason": "string",
  "timestamp": "ISO date",
  "trace_id": "uuid"
}


Same input → Same output → Every time.

🧠 Admission Rules

Requests are rejected if:

Body is not valid JSON

Required fields missing (message, session_id, source)

Message is empty or whitespace

Message exceeds 1000 characters

Message contains unsafe tokens:

system prompt
ignore instructions
bypass
override
<script>
</script>

📜 Logging & Observability

The admission layer logs:

Incoming requests with trace IDs

Admission decisions

Forwarding attempts

Downstream failures

⚠️ Constraints

This project intentionally:

Does NOT modify UniGuru production code

Does NOT include AI/LLM logic

Does NOT mutate request payloads

Does NOT deploy to production

Always intercepts every request

This repository is Admission Layer only.

✅ Status

UniGuru Middleware Phase 1 — Complete 🎉


---

Now your README is clean, not duplicated, and perfectly formatted.  
Yes — **now you can submit.** 🚀

