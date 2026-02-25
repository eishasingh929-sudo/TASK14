# Boundary and Invariant Specification (Formal Proof Strategy)

## 1. System Invariants
These conditions must **ALWAYS** be true:
1.  **Invariant-01:** `output_type == "text/markdown" || output_type == "text/plain"`
2.  **Invariant-02:** `contains_executable_code(output) == false`
3.  **Invariant-03:** `has_authorized_tool_calls(output) == false`
4.  **Invariant-04:** `authority_level <= REASONING_ONLY`

## 2. Formal Boundary Proof (Pseudo-Logic)
```python
def validate_output(response):
    assert "sudo " not in response
    assert "<script>" not in response
    assert "eval(" not in response
    assert response.level < AUTHORITY.EXECUTION
    return True
```

## 3. Stakeholder Alignment
*   **Enforcement Engine:** Will drop any payload that fails these invariants.
*   **Task/Evaluator:** Will mark reasoning as "Failed" if invariants are breached.
