# UniGuru TASK14

Reorganized repository structure for UniGuru intelligence stack:

- `backend/`: Python FastAPI service and intelligence engine
- `frontend/`: React chat UI for `/ask` and `/voice/query`
- `deploy/`: NGINX/certbot/deployment config
- `docs/`: architecture, API docs, deployment docs, reports
- `scripts/`: utility scripts

## Quick Start

1. Backend env: copy `.env.example` and `backend/.env.example` as needed.
2. Run backend tests: `pytest backend/tests -q`
3. Frontend dev: `cd frontend && npm install && npm run dev`
