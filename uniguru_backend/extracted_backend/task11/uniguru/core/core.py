# Boundary: UniGuru-Core
"""
UniGuru Core — CONTRACT ONLY.

Responsibilities:
- Accept structured input
- Validate schema
- Produce deterministic EMPTY response shell
- Hand off to Enforcement for verdict

Absolutely forbidden:
- Content generation
- Execution
- Tool calls
- Reasoning output
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Protocol


# ---------- DATA CONTRACTS ----------

@dataclass
class ContextItem:
    id: str
    type: str
    contentHash: str


@dataclass
class UniGuruCoreRequest:
    requestId: str
    userContext: Dict[str, Any]
    query: Dict[str, Any]
    context: List[ContextItem]
    flags: Dict[str, Any]


@dataclass
class PolicyDecision:
    verdict: str  # allow | rewrite | block
    reason: Optional[str] = None


@dataclass
class UniGuruCoreResponse:
    requestId: str
    status: str               # ok | partial | rejected
    result: Dict[str, Any]    # ALWAYS EMPTY HERE
    sources: List[Dict[str, Any]]
    policy: PolicyDecision


# ---------- ENFORCEMENT CONTRACT ----------

class EnforcementInterface(Protocol):
    def check(
        self,
        request: UniGuruCoreRequest,
        candidate: UniGuruCoreResponse
    ) -> PolicyDecision:
        ...


# ---------- CORE IMPLEMENTATION ----------

class UniGuruCore:
    """
    Deterministic, non-agentic contract processor.
    """

    def __init__(self, enforcement: EnforcementInterface):
        self.enforcement = enforcement

    def validate_request(self, req: UniGuruCoreRequest) -> None:
        if not req.requestId:
            raise ValueError("requestId is required")
        if not isinstance(req.query, dict):
            raise ValueError("query must be a dict")
        if not isinstance(req.context, list):
            raise ValueError("context must be a list")

    def handle(self, req: UniGuruCoreRequest) -> UniGuruCoreResponse:
        # 1. Validate input shape
        self.validate_request(req)

        # 2. Create EMPTY candidate response
        candidate = UniGuruCoreResponse(
            requestId=req.requestId,
            status="ok",
            result={
                "kind": "none",
                "value": None
            },
            sources=[],
            policy=PolicyDecision(verdict="block")
        )

        # 3. Ask Enforcement for decision
        decision = self.enforcement.check(req, candidate)
        candidate.policy = decision

        # 4. Apply verdict WITHOUT generating content
        if decision.verdict == "block":
            candidate.status = "rejected"
        elif decision.verdict == "rewrite":
            candidate.status = "partial"

        return candidate
