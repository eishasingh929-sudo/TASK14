# KB_COVERAGE_REPORT.md

## Purpose

This document audits the deterministic Knowledge Base (Quantum_KB) and evaluates
how much of the content is currently reachable by the Retrieval Engine.

This fixes the previously identified gap:
"Retrieval validation with real KB structure confirmation".

---

## 1. Knowledge Base Location

knowledge/Quantum_KB/

This directory contains the deterministic knowledge used by the Retrieval Engine.

---

## 2. Currently Reachable Files (Mapped)

The current retriever uses a static keyword map.

Mapped files:

| Keyword | File | Status |
|---|---|---|
| qubit | qubit.md | Reachable |
| superposition | superposition.md | Reachable |
| entanglement | entanglement.md | Reachable |
| shor | shor_algorithm.md | Reachable |
| grover | grover_algorithm.md | Reachable |
| density matrix | density_matrix.md | Reachable |

Total reachable files: **6**

---

## 3. Knowledge Base Directory Scan

Detected subdirectories:

- Quantum_Algorithms
- Quantum_Applications
- Quantum_Biology
- Quantum_Chemistry
- Quantum_Computing
- Quantum_Hardware
- Quantum_Mathematics
- Quantum_Physics
- Quantum_Software

These directories contain additional knowledge that is currently **not indexed**.

---

## 4. Coverage Gap Analysis

### Current Retrieval Coverage
- Root-level files only
- Hardcoded keyword mapping
- No recursive discovery

### Missing Coverage
- All subdirectory files are unreachable
- KB_INDEX.md is not used
- No dynamic keyword generation

This means a large portion of the knowledge base is currently unused.

---

## 5. Risk Assessment

Impact of limited coverage:

- Retrieval answers are restricted to a small subset of KB.
- Queries related to subdomains cannot be answered deterministically.
- Over-reliance on forwarding to legacy generative system.

This gap has now been formally documented.

---

## 6. Required Upgrade (Phase 3)

The Retrieval Engine must be upgraded to:

1. Recursively scan the Knowledge Base.
2. Automatically build the keyword-to-file map.
3. Support hierarchical retrieval:
   - Foundations → Domain → General.
4. Log uncovered or unmapped files during startup.

This upgrade will significantly improve deterministic coverage.

---

## 7. Summary

Current State:
- Deterministic retrieval works.
- Coverage is limited.

Future Requirement:
- Expand retrieval to cover the full Knowledge Base.

The retrieval coverage gap is now fully documented.
