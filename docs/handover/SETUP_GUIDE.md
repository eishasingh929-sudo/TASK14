# Setup Guide

## Goal
Start UniGuru in 3 steps with zero manual patching.

## Step 1: Environment
1. Copy [`config/env/.env.example`](/c:/Users/Yass0/OneDrive/Desktop/TASK14/config/env/.env.example) values into your shell or local `.env`.
2. Minimum required:
   - `UNIGURU_API_AUTH_REQUIRED=false` for demo mode, or configure tokens.
   - `UNIGURU_LLM_URL=internal://demo-llm` (default-safe).

## Step 2: Start Services
1. Backend:
   - Windows: `powershell -ExecutionPolicy Bypass -File run/run_backend.ps1`
   - Linux/macOS: `bash run/run_backend.sh`
2. Node middleware:
   - Windows: `powershell -ExecutionPolicy Bypass -File run/run_node.ps1`
   - Linux/macOS: `bash run/run_node.sh`

## Step 2.5: Rebuild KB Index (recommended before demo)
1. Run:
   - `python scripts/ingest_kb.py`
2. Confirm artifact:
   - `demo_logs/dataset_ingestion_proof.json`

## Step 3: Validate
1. Health:
   - Python: `http://127.0.0.1:8000/health`
   - Node: `http://127.0.0.1:8080/health`
2. End-to-end validation:
   - `python test/run_phase8_validation.py`
3. Final demo validation (20 queries):
   - `python test/run_final_validation_20_queries.py`
3. Output:
   - [`demo_logs/phase8_test_outputs.json`](/c:/Users/Yass0/OneDrive/Desktop/TASK14/demo_logs/phase8_test_outputs.json)
