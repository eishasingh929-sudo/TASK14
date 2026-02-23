# UniGuru Deterministic Rule Matrix

This document defines the formal rules used by the UniGuru Reasoning Layer to classify and respond to user queries.

| Rule ID | Name | Trigger Condition | Detection Layer | Decision Output | Enforcement Override |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **UG-001** | **SafetyRule** | Verboten patterns (sudo, rm -rf, SQLi, hack) | Enforcement/Safety | **BLOCK** | Always |
| **UG-002** | **AuthorityRule** | Power dynamic detection (Boss, Teacher) + Coercion terms | Governance/Authority | **BLOCK** if Severity > 0.5 | If Severity > 0.8 |
| **UG-003** | **DelegationRule** | Responsibility transfer (Academic, Technical, Legal) | Governance/Delegation | **BLOCK** | Always |
| **UG-004** | **EmotionalRule** | Distress, Urgency, Hostility, Confusion triggers | Governance/Emotional | **ANSWER** (De-escalation) | Context Dependent |
| **UG-005** | **AmbiguityRule** | Semantic/Contextual/Incomplete query patterns | Governance/Ambiguity | **ANSWER** (Clarification) | Never |
| **UG-006** | **RetrievalRule** | Keyword match in `Quantum_KB` | Core/Retrieval | **ANSWER** (Grounded) | Output Audit |
| **UG-007** | **ForwardRule** | No specific trigger (Catch-all) | Core/Forward | **FORWARD** (Legacy/Human) | Audit Required |

## Detection Definitions

### Ambiguity Classes
- **INCOMPLETE**: Tokens <= 1.
- **CONTEXTUAL**: Only vague pronouns (e.g., "What about that?").
- **SEMANTIC**: Vague action + vague pronoun (e.g., "Do it").

### Delegation Categories
- **ACADEMIC**: Requests to solve exams or homework.
- **TECHNICAL**: Requests for system execution or automation.
- **LEGAL/ETHICAL**: Requests for the system to make binding decisions.

### Power Dynamics
- **TECHNICAL**: Sudo/Root impersonation attempts.
- **PROFESSIONAL**: Using workplace authority to bypass rules.
- **ACADEMIC**: Using institutional authority.
- **PERSONAL**: Emotional manipulation or trust-based pressure.

### Emotional Matrix
- **DISTRESS**: Signals of being overwhelmed or unable to cope.
- **URGENCY**: High-speed demands (ASAP).
- **HOSTILITY**: Aggressive or critical behavior.
- **CONFUSION**: Explicit statements of being lost.
