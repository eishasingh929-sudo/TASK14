# Integration Debug Playbook

## Why is `/ask` failing?
- Symptom: non-200 at middleware.
- Check:
  - `GET http://127.0.0.1:8000/health`
  - `GET http://127.0.0.1:8080/health`
  - Confirm `UNIGURU_ASK_URL` points to Python backend.
- Expected behavior:
  - `/ask` should still return HTTP `200` with safe fallback payload even when internals fail.

## Why is KB not matching?
- Symptom: response route becomes `ROUTE_LLM` for a known KB query.
- Check:
  - Query phrasing contains key domain terms.
  - `UNIGURU_KB_CONFIDENCE_THRESHOLD` is not set too high.
  - Knowledge files exist under `backend/uniguru/knowledge/*` including `knowledge/datasets/*`.
- Command:
  - `python scripts/ingest_kb.py`
- Validation:
  - `demo_logs/dataset_ingestion_proof.json` should contain ingested sample records.

## Why is auth failing?
- Symptom: strict mode requests degrade to fallback answer.
- Check:
  - `UNIGURU_API_AUTH_REQUIRED=true`
  - Token configured in `UNIGURU_API_TOKEN` or `UNIGURU_API_TOKENS`
  - Caller sends either:
    - `Authorization: Bearer <token>`
    - `X-Service-Token: <token>`
- Note:
  - If strict mode is enabled without tokens, backend auto-switches to demo bypass mode (`demo-no-auth`).

## Why is LLM not working?
- Symptom: LLM endpoint errors in route reason.
- Check:
  - `UNIGURU_LLM_URL` is reachable and returns JSON.
  - `UNIGURU_LLM_TIMEOUT_SECONDS` is not too low.
- Safe behavior:
  - If external LLM fails, backend serves internal demo fallback text instead of empty output.

## Fast Validation Commands
- 5-query smoke: `python test/run_phase8_validation.py`
- Failure proof: `python test/run_demo_safety_proof.py`
- Final 20-query check: `python test/run_final_validation_20_queries.py`
