# UniGuru TASK14

Canonical decision file: `CANONICAL_SYSTEM_DECISION.md`

Reorganized repository structure for UniGuru intelligence stack:

- `backend/`: Python FastAPI service and intelligence engine
- `frontend/`: React chat UI for `/ask` and `/voice/query`
- `deploy/`: NGINX/certbot/deployment config
- `docs/`: architecture, API docs, deployment docs, reports
- `scripts/`: utility scripts

## Quick Start

1. Backend env: copy `.env.example` and adjust only required keys.
2. Start Python API: `set PYTHONPATH=backend && uvicorn uniguru.service.api:app --host 127.0.0.1 --port 8000`
3. Start Node middleware: `cd node-backend && npm install && npm start`
4. Health checks:
   - Python: `GET http://127.0.0.1:8000/health`
   - Python ready: `GET http://127.0.0.1:8000/ready`
   - Node: `GET http://127.0.0.1:8080/health`

## Locked Execution Path

`UI / API Consumer -> node-backend -> POST /ask (Python) -> ConversationRouter -> KB or LLM fallback -> Response`

`POST /ask` is the canonical text-query entry point used by middleware integrations.

## Live Query Flow

`Frontend -> node-backend (/api/v1/chat/query) -> uniguru-api (/ask)`

`Gurukul -> node-backend (/api/v1/gurukul/query) -> uniguru-api (/ask)`

## Phase-8 Validation

With Python + Node running:

`python scripts/run_phase8_checks.py`

Output is written to `demo_logs/phase8_test_outputs.json`.
