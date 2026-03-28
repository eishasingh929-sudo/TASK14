from __future__ import annotations

import re
import time
import uuid
from typing import Any, Dict, Optional

from uniguru.core.rules.base import RuleContext
from uniguru.core.rules.base import RuleAction
from uniguru.enforcement.safety import SafetyRule
from uniguru.governance.ambiguity import AmbiguityRule
from uniguru.governance.authority import AuthorityRule
from uniguru.governance.delegation import DelegationRule
from uniguru.governance.emotional import EmotionalRule


class GovernancePreflight:
    """Shared deterministic preflight used by the canonical UniGuru pipeline."""

    def __init__(self) -> None:
        self._rules = [
            SafetyRule(),
            AuthorityRule(),
            DelegationRule(),
            EmotionalRule(),
            AmbiguityRule(),
        ]

    def evaluate(
        self,
        *,
        query: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        request_id = str(uuid.uuid4())
        metadata = dict(context or {})
        aggregated_flags = {
            "authority": False,
            "delegation": False,
            "emotional": False,
            "ambiguity": False,
            "safety": False,
        }
        trace = []

        for rule in self._rules:
            if isinstance(rule, AmbiguityRule) and not re.search(r"[a-z0-9]", query.lower()):
                continue
            started = time.perf_counter()
            result = rule.evaluate(
                RuleContext(
                    request_id=request_id,
                    content=query,
                    timestamp=time.time(),
                    metadata=metadata,
                )
            )
            latency_ms = (time.perf_counter() - started) * 1000
            for flag, value in result.governance_flags.items():
                if value:
                    aggregated_flags[flag] = True
            trace.append(
                {
                    "rule": rule.name,
                    "action": result.action.value,
                    "reason": result.reason,
                    "latency_ms": round(float(latency_ms), 3),
                }
            )
            if result.action == RuleAction.ALLOW:
                continue

            return {
                "decision": result.action.value,
                "reason": result.reason,
                "governance_flags": aggregated_flags,
                "data": {
                    "response_content": str(result.response_content or "").strip(),
                    "request_id": request_id,
                    "trace": trace,
                    "rule_triggered": result.rule_name or rule.name,
                    **(result.extra_metadata or {}),
                },
                "verification_status": "UNVERIFIED",
            }

        return None
