# KB Structure Audit

## 1. Directory Structure Check
**Base Path:** `c:\Users\Yass0\OneDrive\Desktop\TASK14\uniguru_core\Quantum_KB`

**Observed:**
- `density_matrix.md`
- `entanglement.md`
- `grover_algorithm.md`
- `KB_INDEX.md`
- `qubit.md`
- `README.md`
- `shor_algorithm.md`
- `superposition.md`
- Directories: `Quantum_Algorithms`, `Quantum_Applications`, `Quantum_Biology`, `Quantum_Chemistry`, `Quantum_Computing`, `Quantum_Hardware`, `Quantum_Mathematics`, `Quantum_Physics`, `Quantum_Software`.

## 2. Keyword Map Validator (`retriever.py`)

**Current `KEYWORD_MAP` Defined:**
- `"qubit"` -> `qubit.md` (Exists: YES)
- `"superposition"` -> `superposition.md` (Exists: YES)
- `"entanglement"` -> `entanglement.md` (Exists: YES)
- `"shor"` -> `shor_algorithm.md` (Exists: YES)
- `"grover"` -> `grover_algorithm.md` (Exists: YES)
- `"density matrix"` -> `density_matrix.md` (Exists: YES)

**Coverage Gap:**
- **Zero coverage** of subdirectories (`Quantum_Algorithms` etc.)
- **Static Mapping**: Only 6 concepts are retrievable.
- **Root Files**: All root `.md` files are mapped.
- **KB_INDEX.md**: Not mapped.

## 3. Discrepancy Findings
1.  **Orphaned Knowledge**: Huge amount of potential knowledge in subdirectories is completely inaccessible to the deterministic retriever.
2.  **Hardcoded Logic**: `retriever.py` relies on a hardcoded dictionary. Expansion requires code changes.
3.  **No Fallback**: If a term is in a subdirectory file, it will not be found.
4.  **No Logic**: The retrieval is pure string matching, no fuzzy logic or stemming.

## 4. Recommendations for Phase 3 (Retrieval Engine V2)
1.  **Dynamic Discovery**: Implement a recursive file scanner to build the valid file list at runtime (or build step).
2.  **Hierarchical Mapping**: `Domain -> Concept` structure (e.g. `Quantum_Algorithms/Shor`).
3.  **Determinism**: Maintain strict keyword matching but broaden scope to include subdirectory filenames/contents.
4.  **Logging**: Log missing files or unmapped directories during startup.
