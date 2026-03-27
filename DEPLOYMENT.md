# UniGuru Deployment

## Target
- Python API: `http://<HOST_OR_IP>:8000/ask`
- Node middleware: `http://<HOST_OR_IP>:3000/api/v1/chat/query`
- Gurukul integration: `http://<HOST_OR_IP>:3000/api/v1/gurukul/query`
- Samachar integration: `http://<HOST_OR_IP>:3000/api/v1/samachar/query`
- Health checks:
  - `http://<HOST_OR_IP>:8000/health`
  - `http://<HOST_OR_IP>:3000/health`

## Exact Requirements For Alay
- Open inbound ports `8000` and `3000` on the demo host if NIC needs direct port access.
- If a reverse proxy or domain is used, route:
  - `/ask` -> `127.0.0.1:8000`
  - `/api/v1/` -> `127.0.0.1:3000`
- Install:
  - Python `3.11+`
  - Node `20+`
  - Docker + Docker Compose if using the container path
  - Optional local Ollama endpoint for `gpt-oss:120b-cloud`

## Required Env
- `UNIGURU_API_TOKEN`
- `UNIGURU_LLM_URL`
- `UNIGURU_API_AUTH_REQUIRED`
- `UNIGURU_ASK_URL`

## Recommended Env File
```env
UNIGURU_HOST=0.0.0.0
UNIGURU_PORT=8000
NODE_BACKEND_PORT=3000
UNIGURU_ASK_URL=http://127.0.0.1:8000/ask
UNIGURU_API_AUTH_REQUIRED=true
UNIGURU_API_TOKEN=replace-with-strong-token
UNIGURU_API_TOKENS=
UNIGURU_ALLOWED_CALLERS=bhiv-assistant,gurukul-platform,samachar-platform,internal-testing,uniguru-frontend
UNIGURU_LLM_URL=http://127.0.0.1:11434/api/generate
UNIGURU_LLM_MODEL=gpt-oss:120b-cloud
UNIGURU_LLM_TIMEOUT_SECONDS=20
UNIGURU_REQUEST_TIMEOUT_MS=15000
UNIGURU_ROUTER_QUEUE_LIMIT=200
UNIGURU_ROUTER_LATENCY_THRESHOLD_MS=1200
UNIGURU_ROUTER_CIRCUIT_OPEN_SECONDS=30
UNIGURU_ROUTER_UNVERIFIED_FALLBACK=true
```

## Docker Path
1. Put production values into `.env.production`.
2. Start the stack:
```bash
docker compose up -d --build
```
3. Verify:
```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:3000/health
curl -X POST http://127.0.0.1:3000/api/v1/chat/query ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"What is a qubit?\",\"context\":{\"caller\":\"bhiv-assistant\"}}"
```

## Manual Path
1. Backend:
```powershell
powershell -ExecutionPolicy Bypass -File run/run_backend.ps1
```
2. Node:
```powershell
powershell -ExecutionPolicy Bypass -File run/run_node.ps1
```

## Validation Commands
- 20-query regression:
```bash
python test/run_final_validation_20_queries.py
```
- 30-query live validation:
```bash
python test/run_final_validation_live.py
```
- Restart proof:
```bash
python test/run_live_restart_proof.py
```

## Output Artifacts
- `demo_logs/final_validation_live.json`
- `demo_logs/live_restart_proof.json`
- `demo_logs/live_integration_proof.json`
- `demo_logs/llm_fallback_proof.json`
- `demo_logs/kb_coverage_snapshot.json`
- `docs/reports/FINAL_VALIDATION_LIVE.md`
- `docs/reports/LIVE_RESTART_PROOF.md`

## Operational Notes
- `UNIGURU_API_AUTH_REQUIRED=true` now returns real `401` for missing/invalid tokens.
- Unknown callers now return real `403`. Allowed callers must match `UNIGURU_ALLOWED_CALLERS`.
- `/health` stays available for monitoring even if the LLM is degraded.
- `/ready` becomes `degraded` when the configured LLM is unreachable or the requested model is not loaded.

## Important Limitation
This workspace can make the stack network-bind and deployment-ready, but it cannot create the final public NIC demo URL by itself. Alay still has to run the stack on the target host or VM and expose that host on the network.
