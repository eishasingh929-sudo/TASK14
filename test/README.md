# Test Scripts

- `python test/run_phase8_validation.py`
  - Starts backend + node middleware
  - Runs 5 validation queries
  - Saves output to `demo_logs/phase8_test_outputs.json`
- `python test/run_final_validation_live.py`
  - Runs the live 30-query validation set
  - Saves output to `demo_logs/final_validation_live.json`
- `python test/run_live_integration_proof.py`
  - Proves external UI, Gurukul, Samachar, and direct `/ask` integrations
  - Saves output to `demo_logs/live_integration_proof.json`
- `python test/run_llm_fallback_proof.py`
  - Proves non-empty fallback behavior when the configured LLM is unavailable
  - Saves output to `demo_logs/llm_fallback_proof.json`
- `python test/run_kb_coverage_snapshot.py`
  - Summarizes dataset depth and highlights shallow domains
  - Saves output to `demo_logs/kb_coverage_snapshot.json`
