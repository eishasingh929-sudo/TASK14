# CANONICAL_STRUCTURE_MAP.md

## Purpose

This document defines the **final canonical repository structure** of Unified UniGuru.

This document exists to resolve the previous violation where multiple repositories and satellite projects existed.

From this point forward, UniGuru exists as **one product in one repository**.

---

## Canonical Repository Root

/uniguru

This repository is now the **single source of truth** for all UniGuru components.

No additional repositories are active.

---

## Final Repository Structure

uniguru/
│
├── core/ # RLM v1 deterministic reasoning engine
│ ├── engine.py
│ ├── retriever.py
│ └── rules/
│
├── gateway/ # Middleware admission & bridge server
│ └── app.py
│
├── legacy/ # Legacy Node/Express RAG service (downstream)
│ ├── server.js
│ └── package.json
│
├── knowledge/ # Deterministic Knowledge Base
│ └── Quantum_KB/
│
├── tests/ # Unit + integration + regression tests
│ ├── rule_harness.py
│ └── integration_test.py
│
├── docs/ # Architecture & handover documentation
│
├── scripts/ # Audit & maintenance utilities
│
└── README.md

---

## Component Responsibilities

### core/
Deterministic reasoning layer (RLM v1).

Responsibilities:
- Rule Engine execution
- Rule classes and evaluation
- Deterministic retrieval
- Decision trace generation

This is the **governance and reasoning core**.

---

### gateway/
Middleware bridge and public entry point.

Responsibilities:
- Admission endpoint
- Request validation
- Execution orchestration
- Forwarding to legacy system

This is the **external interface** of Unified UniGuru.

---

### legacy/
Existing Node/Express UniGuru RAG system.

Responsibilities:
- Retrieval augmented generation
- LLM communication
- Conversational response generation

This service is treated as a **downstream dependency** and remains unchanged.

---

### knowledge/
Deterministic knowledge source used by the retrieval engine.

Contains the Quantum_KB corpus.

---

### tests/
All system tests are centralized here.

No tests exist outside this directory.

---

### docs/
Contains all architecture, specification, and handover documentation required for new engineers.

---

### scripts/
Utility scripts for auditing, maintenance, and consolidation.

---

## Execution Boundaries

1. Public Entry → `gateway/app.py`
2. Decision Engine → `core/engine.py`
3. Generative Fallback → `legacy/server.js`

Execution flow:

Request → Gateway → RLM Engine →  
BLOCK / ANSWER → Response  
FORWARD → Legacy → Response

---

## Repository Rules

From this point onward:

1. UniGuru exists in **one canonical repository**
2. No new repositories may be created
3. Satellite repositories are considered archived
4. All future work must occur inside this structure

---

## Summary

The UniGuru ecosystem has been consolidated into a single, structured repository.

This resolves the multi-repository violation and establishes a permanent canonical structure.
