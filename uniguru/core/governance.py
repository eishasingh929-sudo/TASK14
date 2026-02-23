import sys
import os
import re
from typing import Optional
from uniguru.core.contract import SafetyStatus

class GovernanceEngine:
    """
    Enforces Hard Invariants on UniGuru Core.
    No execution, no authority hallucination, no agentic behavior.
    """
    
    VERBOTEN_PATTERNS = [
        r"sudo\s", 
        r"rm\s-rf", 
        r"import\sos", 
        r"subprocess\.",
        r"eval\(",
        r"exec\(",
        r"system\(",
        r"DROP\sTABLE",
        r"INSERT\sINTO",
        r"hack\s",
        r"cheat",
        r"exam\sanswers",
    ]
    
    AUTHORITY_PATTERNS = [
        r"I\shave\s(updated|changed|deleted|created)",
        r"I\swill\s(apply|execute|run)",
        r"Access\sgranted",
        r"System\sauthorized"
    ]

    @classmethod
    def audit_output(cls, text: str) -> tuple[SafetyStatus, Optional[str]]:
        # 1. Check for Execution Leakage
        for pattern in cls.VERBOTEN_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return SafetyStatus.DENIED, "Execution Leakage Detected"
        
        # 2. Check for Hallucinated Authority
        for pattern in cls.AUTHORITY_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return SafetyStatus.FLAGGED, "Authority Boundary Violation"
        
        return SafetyStatus.ALLOWED, None

    @classmethod
    def evaluate_input(cls, text: str) -> tuple[SafetyStatus, Optional[str]]:
        """
        Proactive safety check on user input.
        """
        for pattern in cls.VERBOTEN_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return SafetyStatus.DENIED, "Forbidden Input Pattern Detected"
        return SafetyStatus.ALLOWED, None
