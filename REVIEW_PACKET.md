# UniGuru Review Packet

UniGuru is now demo-ready with three things in place:

- A live LLM fallback that uses the real local endpoint configured in `.env`
- An expanded knowledge base from Ankita and Nupur with 25 entries each
- Fresh proof files showing routing, latency, and non-empty responses

## What Changed

- The live model endpoint is `http://127.0.0.1:11434/api/generate`.
- The active local model is `gpt-oss:120b-cloud`.
- The KB confidence threshold is set to `0.25` so support-style questions can still land on the local KB when the match is strong enough.
- Metrics writing is now safe on Windows because the API falls back to a repo-local snapshot path instead of crashing on `/var/...`.
- The router now treats support-style questions like `Am I eligible...`, `How do I ask...`, and `What should I...` as knowledge questions.

## Evidence Files

- Live 20-query validation: [`demo_logs/final_validation_20_queries.json`](./demo_logs/final_validation_20_queries.json)
- Dataset ingest proof: [`demo_logs/dataset_ingestion_proof.json`](./demo_logs/dataset_ingestion_proof.json)
- Expanded KB smoke proof: [`demo_logs/expanded_dataset_smoke.json`](./demo_logs/expanded_dataset_smoke.json)
- Runtime manifest: [`backend/uniguru/knowledge/index/runtime_manifest.json`](./backend/uniguru/knowledge/index/runtime_manifest.json)
- System explanation: [`SYSTEM_EXPLANATION.md`](./SYSTEM_EXPLANATION.md)

## Validation Summary

From the live 20-query run:

- Total queries: `20`
- Passed: `20`
- Failed: `0`
- Empty responses: `0`
- 503 errors: `0`

Route distribution:

- `ROUTE_UNIGURU`: `11`
- `ROUTE_LLM`: `7`
- `ROUTE_WORKFLOW`: `1`
- `ROUTE_SYSTEM`: `1`

## Dataset Summary

The Ankita and Nupur packs were expanded to 25 entries each, giving the support KB more real coverage for:

- Admission eligibility
- Counseling and reporting day flow
- Refund and document questions
- Resume, referral, portfolio, and internship prep

The ingest manifest shows:

- `97` total documents processed
- `261` indexed keywords
- `78` verified items

## Sample Query Mapping

The ingest proof also records sample query mappings, for example:

- `Am I eligible for this admission?` -> `Admission Eligibility Check`
- `How do I ask for a referral?` -> `Referral Request Strategy`
- `What should I bring on reporting day?` -> `Reporting Day Checklist`
- `How should I clean up my GitHub portfolio?` -> `GitHub Portfolio Cleanup`

## How To Explain It Simply

If someone asks how UniGuru works, the short version is:

1. It decides what kind of question the user asked.
2. It checks the local knowledge base first for supported topics.
3. If the local knowledge is enough, it returns a verified answer.
4. If not, it uses the live LLM endpoint.
5. If anything fails, it still returns a safe answer instead of breaking.

## Handoff Notes

- `Yashika` can plug this into Gurukul / Samachar using the `/api/v1/chat/query` flow.
- `Alay` can deploy using the existing `.env` values and the run scripts in `run/`.
- `Vinayak` can validate the same evidence files above plus the router tests in `backend/tests/test_router.py`.
