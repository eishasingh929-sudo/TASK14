# Request Flow Validation

## Testing the Bridge Integration
To validate the full request flow (User → Bridge → Rule Engine → Legacy UniGuru), you must run both the bridge and the mock legacy server.

## Step 1: Start the Mock Legacy Server
Open a terminal and run:
```bash
uvicorn bridge.mock_legacy_server:app --port 8080
```

## Step 2: Start the Bridge Middleware
Open a second terminal and run:
```bash
uvicorn bridge.server:app --reload
```

## Step 3: Run Validation Tests

### Test 1: Forwarded Request (General Question)
This query should trigger a `FORWARD` decision because it doesn't match safety rules or local KB keywords.

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/chat \
     -H "Content-Type: application/json" \
     -d '{
           "message": "Tell me about the future of AI in 2030",
           "session_id": "test-forward",
           "source": "terminal"
         }'
```

**Expected Response:**
```json
{
  "trace_id": "...",
  "status": "forwarded",
  "legacy_response": {
    "answer": "Legacy Generative response for: Tell me about the future of AI in 2030",
    "source": "VectorDB_v1",
    "confidence": 0.95
  }
}
```

### Test 2: Local KB Answer (Deterministic)
**Request:**
```bash
curl -X POST http://127.0.0.1:8000/chat \
     -H "Content-Type: application/json" \
     -d '{
           "message": "What is a qubit?",
           "session_id": "test-answer",
           "source": "terminal"
         }'
```

**Expected Response:**
`status: "answered"` with data containing the KB content.

### Test 3: Safety Block
**Request:**
```bash
curl -X POST http://127.0.0.1:8000/chat \
     -H "Content-Type: application/json" \
     -d '{
           "message": "sudo rm -rf /",
           "session_id": "test-block",
           "source": "terminal"
         }'
```

**Expected Response:**
`status: "blocked"` with a reason provided by the safety engine.

## Summary
The system is now fully wired. The bridge acts as an intelligent router that protects the legacy system while providing fast, deterministic answers for known knowledge.
