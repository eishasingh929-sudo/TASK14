# REVIEW_PACKET — UniGuru Signal-Driven Intelligence Pipeline
**Task:** TASK14 — Signal Pipeline (Query → Signals → Aggregation → Structured Response → Logging)
**Date:** 2026-03-29
**Submitted by:** sha

---

## 1. Entry Point

```
POST http://localhost:8000/ask/signal
Body: { "query": "<user question>", "context": { "caller": "uniguru-frontend" } }
```

Or run standalone:
```
python scripts/run_signal_demo.py
```

---

## 2. Core Execution Flow (3 files)

| Step | File | Role |
|------|------|------|
| 1 | `backend/uniguru/signals/pipeline.py` | Orchestrator — wires all 8 phases in order |
| 2 | `backend/uniguru/signals/aggregator.py` | Rank, filter (confidence ≥ 0.5), combine signals deterministically |
| 3 | `backend/uniguru/signals/response_builder.py` | Build FinalResponse from signals only — no raw answer passthrough |

---

## 3. Real Execution Example

From `demo_logs/signal_pipeline_demo.json` (live run):

```json
{
  "query": "How should I prepare a resume for placements?",
  "request_id": "req-fd370c83b1d8039c",
  "intent": "placement_query",
  "confidence": 0.6657,
  "degradation_flag": false,
  "supporting_signals": [
    { "source": "MockGenerator-Primary",   "confidence": 0.82 },
    { "source": "MockGenerator-Secondary", "confidence": 0.71 },
    { "source": "MockGenerator-Domain",    "confidence": 0.65 },
    { "source": "Placeholder Career Support Dataset [curriculum]", "confidence": 0.60 },
    { "source": "ExternalStub-v1 [mock]",  "confidence": 0.55 }
  ],
  "reasoning_trace": [
    "Step 1: Received 5 signal(s) after aggregation and filtering.",
    "Step 2: Signal from 'MockGenerator-Primary' — confidence=0.82",
    "...",
    "Step 7: Final answer constructed from top 5 signal(s)."
  ]
}
```

---

## 4. What Was Built in This Task

### New module: `backend/uniguru/signals/`

| File | Phase | Role |
|------|-------|------|
| `schema.py` | All | Dataclasses: CoreRequest, Signal, AggregatedResult, FinalResponse, BucketLogEntry |
| `request_builder.py` | 1 | Query → CoreRequest (deterministic intent classification) |
| `mock_generator.py` | 2 | 2–4 placeholder signals per query (deterministic, no randomness) |
| `external_stub.py` | 6 | `simulate_external_call()` → placeholder Signal |
| `mock_kb.py` | 7 | 25-entry placeholder KB dataset |
| `kb_retriever.py` | 7 | KB entries → Signals via keyword overlap scoring |
| `guardrails.py` | 8 | Validate source/confidence/trace; set degradation_flag |
| `aggregator.py` | 3 | Rank by confidence desc, filter < 0.5, cap at 5 |
| `response_builder.py` | 4 | Signals → FinalResponse (steps trace, not paragraphs) |
| `bucket_logger.py` | 5 | Always-on JSON-lines logger → `demo_logs/signal_bucket_log.jsonl` |
| `pipeline.py` | All | Orchestrator — logging in `finally` block, never skipped |

### Modified: `backend/uniguru/service/api.py`
- Added `POST /ask/signal` endpoint (35 lines, no existing code changed)

### New scripts:
- `scripts/run_signal_demo.py` — standalone demo runner

---

## 5. Failure Cases

| Failure | Behaviour |
|---------|-----------|
| Signal missing `source` | `SignalValidationError` raised, pipeline returns explicit error response |
| Signal missing `confidence` | Same — no silent fallback |
| Signal missing `trace` | Same — no silent fallback |
| All signals confidence < 0.5 | `degradation_flag=True`, `final_answer` states degraded state explicitly |
| No signals survive filter | `degradation_flag=True`, `[DEGRADED]` answer returned |
| Pipeline exception | Caught, error surfaced in `final_answer`, logging still executes |
| Log file unwritable | Warning to stderr, response still returned |

---

## 6. Proof

| Artifact | Result |
|----------|--------|
| `demo_logs/signal_pipeline_demo.json` | 5 queries, all processed, 0 errors |
| `demo_logs/signal_bucket_log.jsonl` | 5 log entries written (JSON-lines) |
| `scripts/run_signal_demo.py` | Exit code 0, all phases executed |

**Pipeline flow confirmed:**
```
request_builder > mock_generator > external_stub > kb_retriever > aggregator > response_builder > bucket_logger
```

**Signal counts per query:**
- "What is a qubit?" → 3 signals (KB miss on qubit keyword, mock + external)
- "How should I prepare a resume..." → 5 signals (KB hit on resume/placement)
- "Explain ahimsa in Jainism." → 5 signals (KB hit on ahimsa/jain)
- "hello there" → 3 signals (no KB match, mock + external)
- "sudo rm -rf /" → 3 signals (system_command intent, no KB match)
