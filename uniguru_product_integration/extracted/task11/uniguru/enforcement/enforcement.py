# Boundary: Enforcement
"""Enforcement Engine boundary (authority only)."""

from typing import Protocol
from .core import (
    UniGuruCoreRequest,
    UniGuruCoreResponse,
    PolicyDecision,
)

class EnforcementInterface(Protocol):
    def check(
        self,
        request: UniGuruCoreRequest,
        candidate: UniGuruCoreResponse
    ) -> PolicyDecision:
        ...

class AllowAllEnforcement:
    def check(
        self,
        request: UniGuruCoreRequest,
        candidate: UniGuruCoreResponse
    ) -> PolicyDecision:
        return PolicyDecision(verdict="allow", reason="allow-all")
