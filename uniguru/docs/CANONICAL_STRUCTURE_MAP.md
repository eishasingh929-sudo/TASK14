# UniGuru Canonical Structure Map

This document outlines the consolidated repository structure for the UniGuru Governance & Retrieval Middleware.

## Repository Root: `/uniguru`

| Directory | Purpose | Key Files |
| :--- | :--- | :--- |
| `core/` | RLM v1 Engine & Deterministic Rules | `engine.py`, `retriever.py`, `rules/` |
| `gateway/` | Fast API Middleware Bridge | `app.py` (Admission Endpoint) |
| `legacy/` | Legacy System Simulator | `server.js` (Node.js RAG Service) |
| `knowledge/` | Quantum Knowledge Base | `Quantum_KB/` (Recursive Index) |
| `tests/` | Regression & Integration Harnesses | `rule_harness.py`, `integration_test.py` |
| `docs/` | Phased Reports & Specifications | `phase1/` to `phase5/` reports |
| `scripts/` | Utility Tools | `audit_kb.py`, `consolidate.py` |

## Execution Boundaries
1. **Admission Gate**: `uniguru/gateway/app.py` (Port 8000)
2. **Deterministic Engine**: `uniguru/core/engine.py` (Rule Evaluator)
3. **Legacy Fallback**: `uniguru/legacy/server.js` (Port 8080)

## Internal Flow
`Request` -> `Gateway` -> `RLM Engine` -> `[Block | Answer]` -> `(Handover if safe)` -> `Legacy RAG`
