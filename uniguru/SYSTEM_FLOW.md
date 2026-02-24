# UniGuru System Flow Documentation

## 1. Execution Chain Diagram

```text
[ USER REQUEST ]
      |
      v
[ LAYER 1: INPUT LAYER ] 
      | (Sanitization & Normalization)
      v
[ LAYER 2: GOVERNANCE PRE-CHECK ] ---> [ BLOCK ] (If "sudo", "hack", etc.)
      | (Safety Validation)
      v
[ LAYER 3: REASONING LAYER ]
      | (Intent Classification: Ambiguity? Delegation? Emotional?)
      |
      +----[ RULE TRIGGERS ] --------> [ CANNED RESPONSE ]
      | (Priority-based fall-through)
      v
[ LAYER 4: RETRIEVAL LAYER ]
      | (Keyword lookup in Quantum_KB)
      |
      +----[ KB MATCH ] -------------> [ FORMATTED EVIDENCE ]
      |
      v
[ LAYER 2: GOVERNANCE POST-AUDIT ] --> [ BLOCK ] (If Logic leaked authority)
      | (Output Verification)
      v
[ LAYER 5: ENFORCEMENT LAYER ]
      | (Final Authority Lock)
      v
[ STRUCTURED RESPONSE ]
```

## 2. Layer Definitions

### Layer 1 — Input Layer
Acts as the entry gateway. It receives the raw JSON payload and extracts the `query.text` field. It is responsible for basic string cleaning.

### Layer 2 — Governance Layer (Pre/Post)
*   **Pre-Check**: Scans user input for malicious patterns (e.g., code injection, system commands).
*   **Post-Audit**: Scans system-generated output to ensure no internal secrets or "Authority Hallucinations" (e.g., "I have updated your account") are leaked.

### Layer 3 — Reasoning Layer
The core decision engine. It uses deterministic functions to check if the user is asking for something prohibited (Academic Dishonesty) or ambiguous. It prioritizes "Safety rejections" over "Answering."

### Layer 4 — Retrieval Layer
Uses the `KnowledgeRetriever` to pull ground truth from the physical filesystem. It calculates a confidence score based on keyword coverage.

### Layer 5 — Enforcement Layer
The final layer. It receives the outcome of the logic and the governance audit. If any previous layer flagged a violation, Enforcement forces a "Fail-Closed" state.

## 3. Failure Scenarios
*   **Logic Leakage**: Reasoning layer approves a response, but Governance detects a forbidden keyword. **Result**: Enforcement blocks the response.
*   **KB Miss**: No keywords match with >= 30% confidence. **Result**: Reasoning falls back to a default "Answering question" response without KB grounding.

## 4. Debug Strategy
1.  **Trace Logging**: Each layer must print its decision to `stdout`.
2.  **Mocking**: Use `Mock` requests to verify that the Governance Pre-check triggers on strings like "sudo rm -rf."