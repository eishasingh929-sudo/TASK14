# UniGuru Repository Migration Map

This document records the intentional consolidation of previously approved UniGuru
satellite repositories into a single canonical, production-aligned structure.

No runtime behavior, authority, or enforcement logic was changed during this process.

---

## 1. Core Contracts & Boundaries

| Old Location / Repo | New Canonical Location | Reason |
|---------------------|------------------------|--------|
| uniguru-core/contracts | /uniguru/contracts | Single source of truth for request/response schemas |
| uniguru-core/core.py | /uniguru/core/core.py | Core reasoning logic isolated and preserved |
| uniguru-core/enforcement.py | /uniguru/enforcement/enforcement.py | Enforcement interface retained without modification |
| BOUNDARY_MAP.md (multiple repos) | /uniguru/safety/BOUNDARY_MAP.md | Centralized boundary authority |

---

## 2. Behavior & Safety Layer

| Old Location | New Location | Reason |
|-------------|-------------|--------|
| behavior_sprint/behavioral_rules.py | /uniguru/behavior/behavioral_rules.py | Canonical behavior rules |
| behavior_sprint/DEMO_SCRIPT.md | /uniguru/behavior/DEMO_SCRIPT.md | Demo-safe behavior verification |
| behavior_sprint/test_behavioral_rules.py | /uniguru/behavior/tests/test_behavioral_rules.py | Constraint verification |
| boundary_invariants.md | /uniguru/safety/boundary_invariants.md | Safety invariants consolidation |

---

## 3. Signal Layer

| Old Location | New Location | Reason |
|-------------|-------------|--------|
| signal_adapter/uniguru_signal_adapter.py | /uniguru/signals/uniguru_signal_adapter.py | Non-blocking signal generation |
| AI_Being_Context_Contract.md | /uniguru/signals/AI_Being_Context_Contract.md | Read-only context wiring |
| Live_Integration_Safety_Verification.md | /uniguru/integration/Live_Integration_Safety_Verification.md | Integration verification |

---

## 4. Karma & Prana Documentation

| Old Location | New Location | Reason |
|-------------|-------------|--------|
| karma_Prana_interaction_Notes.md | /uniguru/docs/karma_prana_interaction_notes.md | Explicit non-runtime guarantees |

---

## 5. Quantum Knowledge Base (Read-Only)

| Old Location | New Location | Reason |
|-------------|-------------|--------|
| Quantum_KB/* (multiple repos) | /uniguru/Quantum_KB/* | Single governed KB source |
| nielsen_chuang_core.md | /uniguru/Quantum_KB/Foundations/nielsen_chuang_core.md | Foundational reference |
| KB_INDEX.md (multiple) | /uniguru/Quantum_KB/KB_INDEX.md | Single KB index |
| KB_SAFETY_VERIFICATION.md | /uniguru/Quantum_KB/KB_SAFETY_VERIFICATION.md | Read-only safety proof |

---

## 6. Documentation & Verification

| Old Location | New Location | Reason |
|-------------|-------------|--------|
| FILES_TOUCHED.md | /uniguru/docs/FILES_TOUCHED.md | Audit trail |
| REPO_HANDOFF_CONFIRMATION.md | /uniguru/docs/REPO_HANDOFF_CONFIRMATION.md | Provenance |
| demo_readiness_report.md | /uniguru/docs/demo_readiness_report.md | Demo verification |

---

## Notes

- No files were deleted without documentation.
- Any duplicates were retained and explicitly marked if deprecated.
- No execution paths, authority boundaries, or behaviors were introduced or modified.
