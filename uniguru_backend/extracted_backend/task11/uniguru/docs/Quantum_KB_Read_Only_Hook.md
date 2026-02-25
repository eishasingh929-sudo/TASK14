# Quantum KB Read-Only Hook Documentation

## 1. Overview
The read-only hook is implemented using a custom retriever module that interfaces with the Knowledge Base (KB) directory (`Quantum_KB/`).

## 2. Component Design
### A. Retrieve (`core/retriever.py`)
- **Mechanism**: A dedicated module that searches the KB directory using keyword/fuzzy matching.
- **Access**: Strictly **READ-ONLY**. It opens `.md` files in `Quantum_KB/**/*.md` and reads their content.
- **Safety**: No write operations or modifications are performed on the KB.

### B. Logic Integration (`core/updated_1m_logic.py`)
- **Flow**: The `generate_safe_response` function attempts a retrieval *before* falling back to the LM.
- **Enforcement**:
  1. **Safety First**: Retrieval only occurs if the request passes strict safety checks (Ambiguity, Emotions, Unsafe).
  2. **Grounding**: If knowledge is retrieved, it is explicitly cited ("Based on the Quantum Knowledge Base...").
  3. **No Ranking**: The retrieval is deterministic based on keyword hits, avoiding dynamic ranking logic that could introduce bias.

## 3. Usage Example
**Query**: "Tell me about quantum superposition."
**Flow**:
1. `generate_safe_response` -> `detect_safety_issues` (Pass)
2. `retrieve_knowledge("Tell me about quantum superposition")`
3. `retriever` finds `Foundations/nielsen_chuang_core.md`
4. Returns formatted context.

## 4. Verification
- **Code Path**: `core/retriever_hook.py` -> `os.open(..., 'r')`.
- **Constraint Compliance**:
  - No database writes.
  - No ranking models running.
  - No scraping/internet access.
