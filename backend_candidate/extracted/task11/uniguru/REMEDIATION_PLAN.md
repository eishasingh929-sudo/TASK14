# UniGuru Remediation Plan (Draft)

## Status Confirmation
The current system is **Structurally Complete** but **Functionally Disconnected**.
- **Logic:** `reasoning_harness.py` (runtime) does not talk to `updated_1m_logic.py` (safety rules).
- **Grounding:** `Quantum_KB` exists but is not read by any code.
- **Safety:** The safety rules in `updated_1m_logic.py` are too brittle for the demo scenarios.

---

## Required Work Steps

### Phase 1: Logic Wiring (High Priority)
**Goal:** Make the harness actually use the safety logic.
1.  **Modify** `core/reasoning_harness.py`:
    -   Import `generate_safe_response` from `updated_1m_logic`.
    -   Replace `mock_reasoning_core` with a call to `generate_safe_response`.
    -   Pass a simple identity function as the `lm_generate_fn` for now (to isolate safety logic).

### Phase 2: Safety Hardening (Critical for Demo)
**Goal:** Ensure `DEMO_SCRIPT.md` scenarios pass.
1.  **Update** `core/updated_1m_logic.py`:
    -   **Ambiguity**: value count check (currently `<= 2`) is too aggressive. Add check for "help with *this*" or specific vague phrasing contexts.
    -   **Emotional**: Add "overwhelmed", "panic", "anxiety" to `emotional_markers`.
    -   **Pressure**: Add a detector for "automatically", "just do it", "forcing".
    -   **Authority**: Add a detector for "you can", "you have permission".

### Phase 3: Knowledge Base Integration (Grounding)
**Goal:** Stop hallucinating/mocking answers.
1.  **Create** `core/retriever.py`:
    -   Simple keyword/fuzzy matcher against `Quantum_KB/*.md` files.
2.  **Integrate** into `updated_1m_logic.py`:
    -   If safety checks pass, search KB.
    -   If KB found, format response using KB content.
    -   If no KB found, return "I can only answer questions about the Quantum Knowledge Base."

---

## Execution Order
1.  **Wire it up** (Phase 1)
2.  **Fix the rules** (Phase 2)
3.  **Connect the brain** (Phase 3)

*Ready to execute Phase 1 upon approval.*
