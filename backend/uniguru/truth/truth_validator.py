from __future__ import annotations

from typing import Any, Dict

from uniguru.service.live_service import LiveUniGuruService


class TruthValidator:
    """
    Compatibility facade over the canonical UniGuru service.

    Historical callers used this module for KB-first truth enforcement.
    It now delegates to the same service used by `/ask`.
    """

    _service = LiveUniGuruService()

    @classmethod
    def validate_and_format(cls, query: str) -> Dict[str, Any]:
        response = cls._service.ask(
            user_query=query,
            session_id="truth-validator",
            allow_web_retrieval=True,
        )
        return {
            "response": response.get("answer"),
            "source": (response.get("ontology_reference") or {}).get("concept_id"),
            "status": response.get("verification_status"),
            "reason": response.get("reason"),
            "raw_response": response,
        }


def ask_uniguru(query: str) -> Dict[str, Any]:
    return TruthValidator.validate_and_format(query)
