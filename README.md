# UniGuru

UniGuru is a demo-safe AI backend stack with deterministic KB routing, LLM fallback, and guaranteed response behavior.

## 3-Step Startup

1. Configure environment values from [`config/env/.env.example`](/c:/Users/Yass0/OneDrive/Desktop/TASK14/config/env/.env.example).
2. Start backend:
   - Windows: `powershell -ExecutionPolicy Bypass -File run/run_backend.ps1`
   - Linux/macOS: `bash run/run_backend.sh`
3. Start node middleware:
   - Windows: `powershell -ExecutionPolicy Bypass -File run/run_node.ps1`
   - Linux/macOS: `bash run/run_node.sh`
   - Default Node port: `3000`

## Validate End-to-End

Run:

`python test/run_phase8_validation.py`

Output:

[`demo_logs/phase8_test_outputs.json`](/c:/Users/Yass0/OneDrive/Desktop/TASK14/demo_logs/phase8_test_outputs.json)

Additional failure-injection proof:

`python test/run_demo_safety_proof.py`

Output:

[`demo_logs/demo_safety_proof.json`](/c:/Users/Yass0/OneDrive/Desktop/TASK14/demo_logs/demo_safety_proof.json)

Final 20-query readiness check:

`python test/run_final_validation_20_queries.py`

Output:

[`demo_logs/final_validation_20_queries.json`](/c:/Users/Yass0/OneDrive/Desktop/TASK14/demo_logs/final_validation_20_queries.json)

Final live 30-query check:

`python test/run_final_validation_live.py`

Output:

[`demo_logs/final_validation_live.json`](/c:/Users/Yass0/OneDrive/Desktop/TASK14/demo_logs/final_validation_live.json)

Restart proof:

`python test/run_live_restart_proof.py`

Output:

[`demo_logs/live_restart_proof.json`](/c:/Users/Yass0/OneDrive/Desktop/TASK14/demo_logs/live_restart_proof.json)

Dataset ingestion proof:

`python scripts/ingest_kb.py`

Output:

[`demo_logs/dataset_ingestion_proof.json`](/c:/Users/Yass0/OneDrive/Desktop/TASK14/demo_logs/dataset_ingestion_proof.json)

## Canonical Flow

`UI -> Node (:3000 /api/v1/chat/query) -> Python (:8000 /ask) -> ConversationRouter -> KB or ROUTE_LLM -> Safe fallback`

Additional integration routes:

- `POST /api/v1/gurukul/query`
- `POST /api/v1/samachar/query`

Safe fallback phrase:

`I am still learning this topic, but here is a basic explanation...`

## Repository Map

- `backend/`: Python FastAPI + UniGuru engine
  - `uniguru/router/`, `uniguru/service/`, `uniguru/core/`, `uniguru/integrations/`
- `node-backend/`: middleware
  - `src/routes/`, `src/services/`, `src/server.js`
- `frontend/`: client app
- `run/`: canonical startup scripts
- `test/`: executable validation scripts
- `tests/`: test index
- `config/`: environment and runtime settings
- `docs/architecture/`: system design docs
- `docs/handover/`: onboarding and failure guides
- `docs/reports/`: evidence and historical reports
