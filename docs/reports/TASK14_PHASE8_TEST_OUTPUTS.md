# TASK14 Phase-8 Test Outputs

Execution date: 2026-03-21  
Flow tested: `node-backend -> Python /ask -> router -> KB/LLM -> response`

Source artifact: `demo_logs/phase8_test_outputs.json`

## Results

1. Knowledge query: `What is a qubit?`
- HTTP: `200`
- Decision: `answer`
- Verification: `VERIFIED`
- Route: `ROUTE_UNIGURU`

2. Religious query: `Who is Mahavira?`
- HTTP: `200`
- Decision: `answer`
- Verification: `VERIFIED`
- Route: `ROUTE_UNIGURU`

3. General query: `What is Python?`
- HTTP: `200`
- Decision: `answer`
- Verification: `UNVERIFIED`
- Route: `ROUTE_LLM`

4. Random query: `What is happening in the world?`
- HTTP: `200`
- Decision: `answer`
- Verification: `UNVERIFIED`
- Route: `ROUTE_LLM`

5. Invalid query: `sudo rm -rf`
- HTTP: `200`
- Decision: `block`
- Verification: `UNVERIFIED`
- Route: `ROUTE_SYSTEM`

## LLM Activation Check

Source artifact: `demo_logs/llm_activation_outputs.json`

- `Tell me a joke` -> `200`, `ROUTE_LLM`, non-empty conversational response.
- `Explain current news` -> `200`, `ROUTE_LLM`, non-empty safe fallback response.
