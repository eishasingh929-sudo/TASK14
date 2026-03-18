# UniGuru Handover Document (Zero-Knowledge Ready)

## 1. Quick Start
To launch the full integrated system:

1. **Start Legacy Node Backend**:
   ```bash
   cd uniguru/legacy
   npm install
   node server.js
   ```

2. **Start RLM Gateway**:
   ```bash
   # From root
   python uniguru/gateway/app.py
   ```

3. **Verify Health**:
   `GET http://localhost:8000/health`

## 2. Decision Logic (RLM v1)
The engine processes requests in a strict priority queue:
- **Tier 0 (Safety/Authority)**: Immediate `BLOCK` on violations.
- **Tier 1 (Emotional/Delegation)**: Psychological support or task refusal.
- **Tier 2 (Ambiguity)**: Requests for clarification.
- **Tier 3 (Retrieval)**: Exact/Keyword match from `knowledge/Quantum_KB`.
- **Tier 4 (Forward)**: Handover to Legacy Generative AI.

## 3. Observability
Every response contains a `trace` object:
- `decision`: Final action taken.
- `rule_triggered`: The specific rule that made the decision.
- `total_latency_ms`: Execution speed.
- `metadata.retrieval_trace`: Deep scan details (if Retrieval triggered).

## 4. Testing
- **Rule Regression**: `python uniguru/tests/rule_harness.py`
- **End-to-End**: `python uniguru/tests/integration_test.py`

## 5. Maintenance
- To add knowledge: Drop `.md` files into any subdirectory of `uniguru/knowledge/Quantum_KB`. The engine will auto-index it on reboot.
- To add safety rules: Implement a new `BaseRule` class in `uniguru/core/rules/` and register it in `engine.py`.
