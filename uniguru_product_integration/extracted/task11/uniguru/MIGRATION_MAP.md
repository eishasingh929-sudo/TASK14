# MIGRATION_MAP.md

This document records all files consolidated into the canonical UniGuru repository.
No file content was modified — placement only.

---

## Core

contract.py → core/contract.py → Core contract definition  
governance.py → core/governance.py → Governance logic  
core.py → core/core.py → Core runtime  
update_lm_logic.py → core/update_lm_logic.py → LM update logic  
reasoning_harness.py → core/reasoning_harness.py → Reasoning harness  

---

## Enforcement

enforcement.py → enforcement/enforcement.py → Enforcement logic  
Uniguru-guard.yml → enforcement/Uniguru-guard.yml → Guard configuration  

---

## Behavior

behavioral_rules.py → behavior/behavioral_rules.py → Behavioral rules  
DEMO_SCRIPT.md → behavior/DEMO_SCRIPT.md → Demo behavior mapping  

---

## Signals

uniguru_signal_adapter.py → signals/uniguru_signal_adapter.py → Signal adapter  
UniGuru_Asls_System_Flow.md → signals/UniGuru_Asls_System_Flow.md → System flow  

---

## Safety

boundary_invariants.md → safety/boundary_invariants.md → Safety invariants  
failure_taxonomy.md → safety/failure_taxonomy.md → Failure taxonomy  
lm_robustness_audit.md → safety/lm_robustness_audit.md → Robustness audit  
end_to_end_test_notes.md → safety/end_to_end_test_notes.md → Test notes  

---

## Documentation

sovereign_boundary_notes.md → docs/sovereign_boundary_notes.md → Boundary notes  
karma_Prana_interaction_Notes.md → docs/karma_Prana_interaction_Notes.md → Non-runtime notes  

---

## Quantum Knowledge Base

Quantum_KB/* → Quantum_KB/* → Read-only knowledge base

---

Verification:
- No runtime behavior changed
- No enforcement logic modified
- No execution paths added

