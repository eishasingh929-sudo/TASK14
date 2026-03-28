from __future__ import annotations

from typing import Any, Dict

from uniguru.retrieval.retriever import retrieve_knowledge_with_trace


class SovereignRetriever:
    """
    Compatibility wrapper around the canonical UniGuru retriever.

    Older callers still import `kb_engine.retrieve`; they now receive data
    derived from the same retrieval path used by the FastAPI service.
    """

    def query(self, user_query: str) -> Dict[str, Any]:
        answer, trace = retrieve_knowledge_with_trace(user_query)
        if answer:
            source_file = trace.get("kb_file_path") or trace.get("kb_file")
            return {
                "answer": answer,
                "source_file": source_file,
                "author": "UniGuru KB",
                "publication": trace.get("source_title"),
                "confidence_level": round(float(trace.get("confidence", 0.0) or 0.0), 2),
                "verified": True,
            }

        return {
            "answer": "I do not have verified knowledge to answer this question.",
            "source_file": None,
            "confidence_level": 0.0,
            "verified": False,
        }


_engine = SovereignRetriever()


def retrieve(query: str) -> Dict[str, Any]:
    return _engine.query(query)
