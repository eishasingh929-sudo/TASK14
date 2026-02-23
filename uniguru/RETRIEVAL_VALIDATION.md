# UniGuru Retrieval Hardening & Validation

This document validates the deterministic knowledge retrieval system of UniGuru.

## 1. Keyword → KB File Mapping

The following mapping is established at runtime. Every file in `Quantum_KB/` is indexed by its sanitized filename.

| Keyword | KB Source File | Validation Status |
| :--- | :--- | :--- |
| qubit | qubit.md | Validated |
| density matrix | density_matrix.md | Validated |
| quantum gate | quantum_gate.md | Validated |
| superposition | superposition.md | Validated |
| entanglement | entanglement.md | Validated |

## 2. Validation Checks

### File Existence Check
- **Constraint**: `retriever.py` must check `os.path.isfile(full_path)` before indexing.
- **Failover**: Logs `[RETR-VALIDATION] FAILED` if a directory is mistaken for a file or if permissions are missing.

### Integrity Check
- **Constraint**: Files with 0 bytes are skipped to prevent "Empty Grounding" hallucinations.
- **Failover**: Logs `[RETR-VALIDATION] WARNING: file is empty`.

### Match Confidence
- **Logic**: `Confidence = (Length of Keyword) / (Length of Total Query)`.
- **Purpose**: Provides auditability on why a specific KB entry was chosen.

## 3. Fallback & Failure Modes

| Mode | Trigger | Behavior |
| :--- | :--- | :--- |
| **KB_MISS** | No keyword match found | System logs `[RETR-MISS]` and invokes `ForwardRule` (Tier 4). |
| **EMPTY_INDEX** | `Quantum_KB` folder missing or empty | System logs `CRITICAL ERROR` and defaults to safe generic advisor logic. |
| **MALFORMED_MD** | File encoding issues | System catches exception per-file, logs error, and continues indexing others. |

## 4. Verification Logs (Example)
```text
[RETR-LOAD] Successfully indexed: qubit.md (Size: 1240 bytes)
[RETR-LOAD] Successfully indexed: entanglement.md (Size: 2150 bytes)
...
[RETR-MATCH] Query matched keyword: 'qubit' (Confidence: 0.35)
```
