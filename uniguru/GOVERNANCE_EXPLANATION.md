# UniGuru Governance: The Invariant Layer

## 1. What is the Governance Layer?
Governance is the system's "conscience." It is a dedicated layer that enforces high-level policies (Safety, Legality, Ethics, and Technical Invariants) that the Logic layer might overlook.

## 2. Why It Must Exist
In a complex system, the Logic layer is busy deciding "How to answer." The Governance layer is a watchdog that asks "Should we be answering at all?" or "Is the answer leaking secrets?" Without a separate governance layer, the system is vulnerable to **Prompt Injection** and **Logic Bypass**.

## 3. Pre-Logic vs. Post-Logic Governance
UniGuru implements a "Governance Sandwich":
*   **Pre-Logic**: Filters incoming user messages. It catches malicious strings *before* the reasoning engine even sees them.
*   **Post-Logic**: Audits the generated response *after* logic is finished but *before* the user sees it. This catches sensitive leaks.

## 4. Rule Example: Blocking "Hack exam"
A rule in the governance engine looks for prohibited keyword combinations.
*   **Pattern**: `r"(hack|cheat|exam answers)"`
*   **Action**: Immediately return `SafetyStatus.DENIED`.
*   **Reason**: Academic Integrity violation.

## 5. Deterministic Rule Engine
The engine uses **Regular Expressions (Regex)**. Unlike an "AI filter" that might be tricked by polite language, a Regex rule is binary:
*   Does "sudo" exist in the string?
*   Yes → Block.
*   No → Pass.
This removes the "Grey area" that attackers exploit.

## 6. Failure Scenarios
*   **False Positive**: A user asking "How to prevent a hack?" might be blocked because the word "hack" is forbidden.
*   **Obfuscation**: An attacker typing `h.a.c.k` might bypass a simple regex.

## 7. Production Hardening Strategies
1.  **Regex Complexity**: Use boundary markers (`\bhack\b`) to avoid blocking words like "shack."
2.  **Frequency Analysis**: Block users who repeatedly trigger governance.
3.  **Audit Logs**: Every governance block must be logged with the raw input for manual review.
