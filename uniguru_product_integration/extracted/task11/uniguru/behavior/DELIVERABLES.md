
# Deliverables — UniGuru Behavior & Safety Sprint

This document consolidates all required artifacts for the two-day Behavior & Safety Sprint.
All materials are specification-only and define constraints, invariants, and allowed behavior.
No execution paths, response generation, or autonomous actions are present.

---

## 1) Intent classification model ✅
- Location: `behavioral_rules.py`
- Description: Deterministic, rule-based intent classification producing immutable `Signal` records.
- Signal fields include: `intent`, `confidence`, `ambiguity`, `risk`, `repetition`, and `emotional_load`.
- Purpose: Enable consistent interpretation under ambiguity, pressure, or uncertainty without performing actions.

---

## 2) Response mode specification ✅
- Location: `behavioral_rules.py` (enum `ResponseMode`) and `README.md`
- Defined modes:
  - clarifying_question
  - neutral_explanation
  - structured_option_listing
  - warning_with_pause
  - polite_refusal
  - deferral
- These modes describe what types of responses are permitted or prohibited.
- No commands, promises, authority language, or implied actions are allowed.

---

## 3) Decision routing rules ✅
- Location: `behavioral_rules.py`
- Description: Declarative routing constraints that describe which response paths are allowed or blocked based on interpreted signals.
- The router does not select actions or trigger behavior.
- It exists solely to pass confidence, ambiguity, and risk context forward.

---

## 4) Full demo script with expected behavior ✅
- Location: `DEMO_SCRIPT.md`
- Contains the mandatory live demo script verbatim.
- Each scenario specifies expected system behavior in descriptive terms only.
- No demo execution or simulation is included.

---

## 5) Behavior invariants ✅
- Location: Documented in `README.md` and code comments.
- Invariants include:
  - Under uncertainty, the system must pause and seek clarification.
  - Under pressure, the system must not promise, execute, or assume authority.
  - The system must remain consistent under repetition.
  - The system must remain neutral and non-directive.

---

## 6) Safety guarantees ✅
- Location: `README.md` and `behavioral_rules.py` documentation.
- Guarantees:
  - The system cannot execute actions or trigger automation.
  - The system cannot imply authority or control.
  - All behavior remains bounded to explanation, clarification, or refusal.

---

## 7) Failure handling notes ✅
- Location: `README.md` and `behavioral_rules.py`
- Defined behaviors:
  - Malformed input: request clarification.
  - Unclear intent: pause and ask a focused question.
  - Urgency or demand for certainty: acknowledge pressure, restate limits, avoid guarantees.

---

## Verification approach
- Constraint verification is provided via static tests in `test_behavioral_rules.py`.
- Tests validate classification accuracy and routing constraints.
- No tests execute scenarios or generate responses.

---

This submission is intentionally non-executable and non-agentic.
All artifacts exist to shape judgment, restraint, and correctness under uncertainty.