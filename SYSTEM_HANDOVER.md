# UniGuru System Handover

## How It Is Deployed
- Python FastAPI service listens on `8000` and exposes `/ask`, `/health`, `/ready`, `/metrics`.
- Node middleware listens on `3000` and exposes `/api/v1/chat/query` for the external UI.
- Additional integration routes:
  - `/api/v1/gurukul/query`
  - `/api/v1/samachar/query`
- Docker Compose is the preferred deployment path. Direct VM deployment uses `gunicorn` with `uvicorn.workers.UvicornWorker`.

## How The API Works
- NIC UI calls `POST /api/v1/chat/query` on the Node service.
- Node adds caller context and forwards the request to `POST /ask`.
- FastAPI routes the query and returns a structured answer.

## How Routing Works
- `ROUTE_UNIGURU`: deterministic KB path for covered domains.
- `ROUTE_LLM`: open-chat or fallback language-model path.
- `ROUTE_WORKFLOW`: workflow/task-like commands.
- `ROUTE_SYSTEM`: unsafe system-command requests are blocked.

## How Fallback Works
- If KB cannot answer, routing can move to `ROUTE_LLM`.
- If the LLM fails, UniGuru returns a safe non-empty continuity response instead of crashing.
- If Node cannot reach `/ask`, Node returns its own safe fallback payload.

## Auth And Caller Rules
- `UNIGURU_API_AUTH_REQUIRED=true` enforces bearer or service-token auth on `/ask`.
- Allowed callers are controlled by `UNIGURU_ALLOWED_CALLERS`.
- Invalid token -> `401`
- Unknown caller -> `403`

## How To Restart
- Docker:
```bash
docker compose up -d --build --force-recreate
```
- Direct VM:
```powershell
gunicorn uniguru.service.api:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 4 --timeout 120
npm --prefix node-backend start
```

## How To Check Health
- Backend: `GET http://<HOST_OR_IP>:8000/health`
- Node: `GET http://<HOST_OR_IP>:3000/health`
- Restart proof artifact: `demo_logs/live_restart_proof.json`

## Demo-Ready Endpoints
- `POST http://<HOST_OR_IP>:8000/ask`
- `POST http://<HOST_OR_IP>:3000/api/v1/chat/query`

## Key Proof Files
- `demo_logs/final_validation_live.json`
- `demo_logs/live_restart_proof.json`
- `demo_logs/live_integration_proof.json`
- `demo_logs/llm_fallback_proof.json`
- `docs/reports/FINAL_VALIDATION_LIVE.md`
- `docs/reports/LIVE_RESTART_PROOF.md`
