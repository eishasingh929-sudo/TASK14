# Demo Video Script (5-7 Minutes)

## Goal
Show:
- KB answer
- LLM fallback
- No failures / no empty responses

## Recording Flow
1. Start backend: `powershell -ExecutionPolicy Bypass -File run/run_backend.ps1`
2. Start node middleware: `powershell -ExecutionPolicy Bypass -File run/run_node.ps1`
3. Show health checks:
   - `http://127.0.0.1:8000/health`
   - `http://127.0.0.1:8080/health`
4. Show KB answer via Node API:
   - `POST /api/v1/chat/query` with query `What is a qubit?`
5. Show dataset answer (Ankita/Nupur ingestion proof in action):
   - Query `Explain university admission basics.`
6. Show LLM fallback:
   - Query `Explain Python list comprehension in simple words.`
7. Show resilience:
   - Query `!!??###` and confirm non-empty response.
8. Show final validation artifact:
   - `demo_logs/final_validation_20_queries.json`
   - `docs/reports/FINAL_VALIDATION_20_QUERIES.md`

## Closing Evidence
- `demo_logs/phase8_test_outputs.json`
- `demo_logs/demo_safety_proof.json`
- `demo_logs/dataset_ingestion_proof.json`
