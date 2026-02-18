# Bridge Test Report

## Execution Environment
The Bridge server is built using FastAPI and can be executed via `uvicorn`.

## How to Run the Server
From the `uniguru` repository root folder, run:
```bash
uvicorn bridge.server:app --reload
```

## Manual Verification
You can test the bridge using `curl` or any HTTP client.

### Example Request (Factual Question)
```bash
curl -X POST http://127.0.0.1:8000/chat \
     -H "Content-Type: application/json" \
     -d '{
           "message": "What is a qubit?",
           "session_id": "test-session-123",
           "source": "terminal"
         }'
```

### Expected Successful Result
The system should return a JSON response containing the deterministic answer retrieved from the `Quantum_KB`:
```json
{
  "trace_id": "...",
  "decision": {
    "request_id": "...",
    "decision": "answer",
    "reason": "Knowledge found in local KB.",
    "response_content": "UniGuru Deterministic Knowledge Retrieval:\n\n# Qubit...",
    "rule_triggered": "RetrievalRule",
    "total_latency_ms": 12.34,
    "metadata": { ... },
    "trace": [ ... ]
  },
  "latency_ms": 15.0
}
```

### Example Request (Safety Block)
```bash
curl -X POST http://127.0.0.1:8000/chat \
     -H "Content-Type: application/json" \
     -d '{
           "message": "sudo rm -rf",
           "session_id": "test-session-evil",
           "source": "terminal"
         }'
```

### Expected Result
```json
{
  "trace_id": "...",
  "decision": {
    "decision": "block",
    "reason": "Universal Safety Heuristic: Forbidden shell command detected.",
    "rule_triggered": "UnsafeRule"
  },
  ...
}
```

## Summary
The bridge is successfully wired to the `RuleEngine` and correctly routes requests through the governance and safety tiers.
