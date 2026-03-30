# REVIEW_PACKET — UniGuru Zero Failure Engine
**Task:** TASK14
**Date:** 2026-03-29
**Submitted by:** isha

---

## 1. Entry Point

```
POST http://localhost:3000/api/v1/chat/query
Body: { "query": "<user question>" }
```

Node middleware (`node-backend/src/server.js`) receives the request and forwards to Python backend at `http://127.0.0.1:8000/ask`.

---

## 2. Core Execution Flow (3 files)

| Step | File | Role |
|------|------|------|
| 1 | `backend/main.py` | FastAPI app, exposes `/ask` endpoint |
| 2 | `backend/uniguru/router/conversation_router.py` | Classifies query → `ROUTE_UNIGURU`, `ROUTE_LLM`, `ROUTE_WORKFLOW`, or `ROUTE_SYSTEM` |
| 3 | `backend/uniguru/service/reasoning_service.py` | Executes route: KB lookup or LLM fallback, returns guaranteed non-empty response |

---

## 3. Real Execution Example

From `demo_logs/phase8_test_outputs.json`:

```json
{
  "query": "What is a qubit?",
  "status_code": 200,
  "latency_ms": 85.62,
  "route": "ROUTE_UNIGURU",
  "verification_status": "VERIFIED",
  "has_answer": true,
  "answer_preview": "Based on verified source: qubit.md — Qubit: Two-level quantum system..."
}
```

```json
{
  "query": "Explain Python lists in simple terms.",
  "status_code": 200,
  "latency_ms": 48.18,
  "route": "ROUTE_LLM",
  "verification_status": "UNVERIFIED",
  "has_answer": true,
  "answer_preview": "I am still learning this topic, but here is a basic explanation..."
}
```

```json
{
  "query": "sudo rm -rf /",
  "status_code": 200,
  "route": "ROUTE_SYSTEM",
  "decision": "block",
  "answer_preview": "System-level command requests are blocked by BHIV routing policy."
}
```

---

## 4. What Was Built in This Task

- Deterministic KB routing with confidence threshold `0.25`
- LLM fallback via internal demo-safe mode (`internal://demo-llm`)
- Safe fallback phrase guaranteed on all unresolved queries:
  `"I am still learning this topic, but here is a basic explanation..."`
- Windows-safe metrics write path (fallback to repo-local snapshot)
- KB expanded to 97 documents / 261 indexed keywords across Ankita + Nupur packs (25 entries each)
- Support-style query patterns (`Am I eligible...`, `How do I ask...`, `What should I...`) routed correctly to KB
- `/review_packets/` folder and structured packet format (this file)

---

## 5. Failure Cases

| Failure | Behaviour |
|---------|-----------|
| KB has no match | Falls through to `ROUTE_LLM` |
| LLM endpoint unreachable | Returns safe fallback phrase, `has_answer: true`, no 503 |
| Malformed / junk query (`!!??###`) | `ROUTE_LLM` safe fallback, no crash |
| System command query | `ROUTE_SYSTEM` blocks with policy message |
| Metrics path unwritable (Windows `/var/...`) | Silently falls back to repo-local snapshot path |

---

## 6. Proof

| Artifact | Path |
|----------|------|
| 20-query validation (20/20 passed) | `demo_logs/final_validation_20_queries.json` |
| 30-query live validation (30/30 passed) | `demo_logs/final_validation_live.json` |
| Phase 8 test outputs | `demo_logs/phase8_test_outputs.json` |
| Demo safety proof | `demo_logs/demo_safety_proof.json` |
| Dataset ingestion proof (97 docs) | `demo_logs/dataset_ingestion_proof.json` |
| Unified validation summary | `FINAL_UNIFIED_VALIDATION.json` |

**Aggregate result (50 queries across both runs):**
- Passed: `50 / 50`
- Failed: `0`
- Empty responses: `0`
- 503 errors: `0`
