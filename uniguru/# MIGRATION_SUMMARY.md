# MIGRATION_SUMMARY.md

## Purpose
This document provides the final handover map of the UniGuru repository.

It explains:
- Final folder structure
- Where each responsibility lives
- How new developers should navigate the system

This is the **primary onboarding guide** for future contributors.

---

## Final Repository Structure

uniguru/
│
├── bridge/
│ └── server.py
│
├── core/
│ ├── engine.py
│ ├── governance.py
│ └── core.py
│
├── governance/
│ ├── delegation.py
│ ├── authority.py
│ ├── emotional.py
│ └── ambiguity.py
│
├── enforcement/
│ └── safety.py
│
├── retrieval/
│ └── retriever.py
│
├── Quantum_KB/
│ ├── quantum_entanglement.md
│ ├── quantum_superposition.md
│ ├── quantum_computing_basics.md
│ ├── qubits.md
│ └── quantum_measurement.md
│
└── docs/
├── EXECUTION_CHAIN_DOCUMENT.md
├── STABILITY_HARDENING_REPORT.md
├── RULE_MATRIX.md
├── RETRIEVAL_VALIDATION.md
├── FULL_TEST_RESULTS.md
├── REPO_CONSOLIDATION_REPORT.md
└── MIGRATION_SUMMARY.md

---

## Responsibility Map

### API / Bridge Layer
**Location**
uniguru/bridge/server.py

Responsibilities:
- Receives user requests
- Generates trace_id
- Calls RuleEngine
- Returns final response
- Forwards to legacy backend when required

---

### Core Logic Layer
**Location**
uniguru/core/

Files:
- `engine.py` → RuleEngine (decision pipeline)
- `governance.py` → Output safety audit
- `core.py` → Final enforcement authority

This folder represents the **brain of UniGuru**.

---

### Governance Rules Layer
**Location**
uniguru/governance/

Rules:
- delegation.py → DelegationRule
- authority.py → AuthorityRule
- emotional.py → EmotionalRule
- ambiguity.py → AmbiguityRule

These files define **system behaviour rules**.

---

### Enforcement Layer
**Location**
uniguru/enforcement/safety.py


Responsibility:
- Detect unsafe or prohibited queries
- Trigger BLOCK actions

---

### Retrieval Layer
**Location**
uniguru/retrieval/retriever.py

Responsibilities:
- Load Quantum_KB
- Match queries to knowledge files
- Return grounded responses

---

### Knowledge Base
**Location**
uniguru/Quantum_KB/

Contains deterministic knowledge files used by the retrieval system.

---

### Documentation
**Location**
docs/

Contains the full architecture and validation documentation pack.

---

## How New Developers Should Navigate

1. Start with documentation in `/docs`
2. Understand execution flow via EXECUTION_CHAIN_DOCUMENT.md
3. Review behaviour rules in RULE_MATRIX.md
4. Explore RuleEngine in `core/engine.py`
5. Test retrieval in `retrieval/retriever.py`

---

## Final Status

UniGuru is now:
- Fully consolidated
- Clearly structured
- Deterministic
- Handover-ready

Future development should follow this structure.



