# UniGuru Canonical Repository

## Overview
This repository represents the canonical, production-aligned UniGuru structure.
It consolidates all previously approved satellite repositories into a single
source of truth while preserving all sovereign boundaries, safety guarantees,
and runtime behavior.

No new features, agents, tools, automation, or execution paths were introduced
as part of this consolidation.

---

## Objective
The objective of this repository is to:
- Preserve all approved UniGuru work
- Maintain strict boundary separation
- Provide exactly one canonical source of truth
- Enable controlled live integration and demo readiness

This work is strictly a consolidation and verification effort.

---

## Scope of Consolidation
The following categories of work have been unified:

1. Core contracts and boundaries
2. Behavior and safety specifications
3. Signal definitions and adapters
4. Karma / Prana documentation (non-runtime)
5. Quantum Knowledge Base (read-only)
6. Documentation and verification artifacts

---

## Repository Structure

uniguru/
├── core/ # Core runtime logic (unchanged)
├── enforcement/ # Enforcement interfaces (unchanged)
├── behavior/ # Declarative behavior rules and demo mappings
├── signals/ # Signal definitions and adapters
├── contracts/ # Request/response and context contracts
├── safety/ # Safety invariants, audits, and tests
├── integration/ # Integration and demo readiness documentation
├── docs/ # Non-runtime explanatory documentation
├── Quantum_KB/ # Read-only quantum knowledge base
├── MIGRATION_MAP.md
├── BOUNDARY_MAP.md
├── SAFETY_VERIFICATION.md
├── INTEGRATION_READINESS.md
└── README.md

---

## Boundary Guarantees

- **Runtime logic** exists only in `core/`, `enforcement/`, and `signals/`
- **Behavior** is declarative and demo-scoped
- **Safety** artifacts are non-enforcing and documentation-only
- **Quantum_KB** is strictly read-only and non-executable
- **Documentation** folders have no runtime coupling

No boundary violations were introduced.

---

## Quantum Knowledge Base Governance
The `Quantum_KB/` directory contains only approved, read-only knowledge content.
It includes foundational and advanced quantum topics, including
Nielsen & Chuang–derived material.

Rules enforced:
- No `.py` files
- No imports or execution
- No runtime references
- Documentation-only usage

This design preserves RAG safety and prevents authority leakage.

---

## Migration and Traceability
All files moved into this repository are explicitly documented in
`MIGRATION_MAP.md`, including:
- Original location
- New canonical location
- Reason for placement

No content was deleted without explanation.
Any deprecated or duplicate material is explicitly marked.

---

## Safety Verification
Safety preservation is documented in `SAFETY_VERIFICATION.md`, confirming:
- No new execution paths
- No authority changes
- No enforcement logic modification
- No behavior drift

---

## Integration Readiness
`INTEGRATION_READINESS.md` summarizes:
- What is now unified and ready
- What is intentionally deferred

This repository is suitable for controlled live integration and demo use.

---

## Non-Goals
This consolidation does NOT:
- Add new features
- Refactor runtime logic
- Introduce agents or tools
- Add automation or background jobs
- Change enforcement behavior

---

## Status
✅ Canonical structure established  
✅ All approved work preserved  
✅ Boundaries maintained  
✅ Safety verified  

This repository represents the authoritative UniGuru baseline.
