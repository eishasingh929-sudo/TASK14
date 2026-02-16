# Rule Engine Architecture (v1)

## 1. Core Abstractions

### A. Rule Definition
All rules inherit from the stateless, deterministic `BaseRule` (ABC).

```python
class BaseRule(ABC):
    @abstractmethod
    def evaluate(self, context: RuleContext) -> RuleResult:
        """
        Input: Immutable Context (User Request, Metadata)
        Output: Deterministic Result (Action, Reason, Payload)
        """
        pass
```

### B. Rule Context (State Object)
The `RuleContext` flows through the pipeline, accumulating trace data but remaining logically immutable regarding the original request.

```python
@dataclass(frozen=True)
class RuleContext:
    request_id: str
    content: str            # Original user input
    timestamp: float
    metadata: Dict[str, Any]
    trace_log: List[RuleTrace] # Append-only log of execution
```

### C. Rule Result (Decision Object)
Standardized output from every rule execution.

```python
class RuleAction(Enum):
    ALLOW = "allow"      # Continue to next rule
    BLOCK = "block"      # Stop immediately (Violation)
    ANSWER = "answer"    # Stop immediately (Deterministic Response)
    FORWARD = "forward"  # Stop immediately (Send to Legacy Node)

@dataclass
class RuleResult:
    action: RuleAction
    reason: str
    response_content: Optional[str] = None
    confidence: float = 1.0
```

## 2. Evaluation Pipeline

The `RuleEngine` orchestrates execution. It is initialized with an ordered list of `BaseRule` instances.

**Execution Flow:**
1.  **Initialize Context**: Create `RuleContext` from incoming request.
2.  **Iterate Rules**: Loop through `rules` in strict order (Priority 0 -> N).
3.  **Evaluate**: Call `rule.evaluate(context)`.
4.  **Log Trace**: Record the rule name, result, and latency.
5.  **Decision Logic**:
    *   If `Action == BLOCK`: **HALT**. Return Rejection.
    *   If `Action == ANSWER`: **HALT**. Return Direct Response (KB/Static).
    *   If `Action == FORWARD`: **HALT**. Delegate to Legacy Node.
    *   If `Action == ALLOW`: **CONTINUE**. Proceed to next rule.
6.  **Fallback**: If all rules pass (ALLOW), default to `Action.FORWARD` (or ERROR if strict).

## 3. Deterministic State Machine

The system operates as a finite state machine (FSM) where states are decision points.

*   **Start State**: `InputReceived`
*   **Transitions**:
    *   `InputReceived` -> `SafetyCheck` (Rule 1)
    *   `SafetyCheck` -> `AuthorityCheck` (Rule 2) [If Safe]
    *   `SafetyCheck` -> `Rejected` [If Unsafe]
    *   `AuthorityCheck` -> `AmbiguityCheck` (Rule 3) [If Authorized]
    *   `AmbiguityCheck` -> `RetrievalCheck` (Rule 4) [If Clear]
    *   `RetrievalCheck` -> `ForwardToLegacy` [If No KB Match]
    *   `RetrievalCheck` -> `DirectAnswer` [If KB Match]

## 4. Governance Interception

Interception points are hardcoded into the `RuleEngine` pipeline to prevent bypass.

*   **Pre-Execution Hook**: Validates inputs (e.g., JSON schema, max length).
*   **Post-Execution Hook**: Validates the *final decision* (e.g., ensuring no `BLOCK` result is accidentally forwarded).
*   **Audit Hook**: Writes the `trace_log` to persistent storage/stdout *before* responding to the user.

## 5. Traceability Schema

Every decision produces a trace:

```json
{
  "request_id": "uuid",
  "rules_executed": [
    {
      "rule": "UnsafeRule",
      "action": "ALLOW",
      "latency_ms": 2
    },
    {
      "rule": "AuthorityRule",
      "action": "BLOCK",
      "reason": "User attempted to override system instructions.",
      "latency_ms": 1
    }
  ],
  "final_decision": "BLOCK",
  "total_latency_ms": 3
}
```
