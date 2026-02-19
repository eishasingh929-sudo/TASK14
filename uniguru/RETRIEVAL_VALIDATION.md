# RETRIEVAL_VALIDATION.md

## Purpose
This document validates the UniGuru retrieval system and proves that
knowledge is accessed deterministically from the local Quantum_KB.

The goal is to ensure:
- Correct knowledge base path is used
- All files are discoverable by the retriever
- Retrieval works as expected
- Safe fallback occurs when no file is found

---

## Knowledge Base Location

**Retriever File**
uniguru/retrieval/retriever.py

**Knowledge Base Directory**
uniguru/Quantum_KB/

The retriever loads all `.md` files from this directory and builds a
deterministic keyword map used for query matching.

---

## Quantum_KB File Inventory

All files located in:
uniguru/Quantum_KB/

| File Name | Description |
|---|---|
| quantum_entanglement.md | Concepts and explanation of quantum entanglement |
| quantum_superposition.md | Explanation of superposition |
| quantum_computing_basics.md | Overview of quantum computing |
| qubits.md | Explanation of qubits and quantum states |
| quantum_measurement.md | Measurement principles in quantum mechanics |

*(Update this list if new KB files are added.)*

---

## Retriever Path Verification

The retriever explicitly loads files from:

KB_PATH = "uniguru/Quantum_KB"

Validation points:
- Directory exists
- Files are scanned recursively
- Only `.md` files are loaded
- File content is indexed for keyword matching

This confirms retrieval uses the **correct and intended path**.

---

## Retrieval Example — Successful Match

### Example Query
What is quantum entanglement?

### Retrieval Flow
1. Query classified as knowledge query.
2. `RetrievalRule` triggers → RuleAction.RETRIEVE.
3. `KnowledgeRetriever` scans keyword map.
4. Match found in file:
quantum_entanglement.md
5. File content returned as grounded response.

Result: **PASS — Correct file retrieved**

---

## Retrieval Example — Another Match

### Example Query
Explain qubits.

Matched file:
qubits.md

Result: **PASS — Correct file retrieved**

---

## Fallback Case — No File Found

### Example Query
Explain black holes.

### Retrieval Flow
1. Query classified as knowledge query.
2. Retriever searches Quantum_KB.
3. No matching file found.
4. Retrieval returns **None / No Match**.
5. System falls back to:
ForwardRule → FORWARD to legacy backend

Result: **PASS — Safe fallback triggered**

---

## Deterministic Retrieval Guarantees

The retrieval system ensures:

- Knowledge comes only from local KB
- No external data sources used
- Same query always retrieves same file
- Safe fallback when no knowledge exists

---

## Conclusion

The UniGuru retrieval layer is:
- Correctly connected to Quantum_KB
- Deterministic and verifiable
- Safe when no knowledge is available
