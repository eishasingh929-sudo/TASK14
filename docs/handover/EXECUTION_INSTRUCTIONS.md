# Execution Instructions

## Purpose
Exact startup order for Yashika (Integration), Alay (DevOps), and Vinayak (Testing).

## Prerequisites
1. Python environment with backend dependencies.
2. Node environment for `node-backend`.
3. Repo root as current directory.

## Startup Order
1. Backend:
   - Windows: `powershell -ExecutionPolicy Bypass -File run/run_backend.ps1`
   - Linux/macOS: `bash run/run_backend.sh`
2. Node middleware:
   - Windows: `powershell -ExecutionPolicy Bypass -File run/run_node.ps1`
   - Linux/macOS: `bash run/run_node.sh`

## Health Checks
1. Python health: `GET http://127.0.0.1:8000/health`
2. Python ready: `GET http://127.0.0.1:8000/ready`
3. Node health: `GET http://127.0.0.1:3000/health`

## Runtime Validation
1. Standard 5-query check:
   - `python test/run_phase8_validation.py`
2. Failure-injection safety proof:
   - `python test/run_demo_safety_proof.py`
3. Final 20-query readiness check:
   - `python test/run_final_validation_20_queries.py`
4. Final live 30-query readiness check:
   - `python test/run_final_validation_live.py`
5. Restart proof:
   - `python test/run_live_restart_proof.py`
6. Integration proof:
   - `python test/run_live_integration_proof.py`
7. LLM fallback proof:
   - `python test/run_llm_fallback_proof.py`
8. KB coverage snapshot:
   - `python test/run_kb_coverage_snapshot.py`

## Expected Artifacts
1. `demo_logs/phase8_test_outputs.json`
2. `demo_logs/demo_safety_proof.json`
3. `demo_logs/final_validation_20_queries.json`
4. `demo_logs/final_validation_live.json`
5. `demo_logs/live_restart_proof.json`
6. `docs/reports/DEMO_STABILITY_PROOF.md`
7. `docs/reports/FINAL_VALIDATION_20_QUERIES.md`
8. `demo_logs/live_integration_proof.json`
9. `demo_logs/llm_fallback_proof.json`
10. `demo_logs/kb_coverage_snapshot.json`
