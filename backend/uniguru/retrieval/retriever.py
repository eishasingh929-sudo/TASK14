import os
import re
from typing import Any, Dict, List, Optional, Tuple

from uniguru.reasoning.concept_resolver import ConceptResolver
from uniguru.reasoning.graph_reasoner import GraphReasoner

# Paths for knowledge bases
_MODULE_DIR = os.path.dirname(__file__)
_KB_ROOT = os.path.normpath(os.path.join(_MODULE_DIR, "..", "knowledge"))

_BASE_KB_PATHS: Dict[str, str] = {
    "quantum": os.path.normpath(os.path.join(_KB_ROOT, "quantum")),
    "jain": os.path.normpath(os.path.join(_KB_ROOT, "jain")),
    "swaminarayan": os.path.normpath(os.path.join(_KB_ROOT, "swaminarayan")),
    "gurukul": os.path.normpath(os.path.join(_KB_ROOT, "gurukul")),
    "datasets": os.path.normpath(os.path.join(_KB_ROOT, "datasets")),
}

STOPWORDS = {
    "a",
    "an",
    "the",
    "is",
    "are",
    "was",
    "were",
    "what",
    "which",
    "who",
    "when",
    "where",
    "why",
    "how",
    "about",
    "for",
    "to",
    "in",
    "on",
    "of",
    "and",
    "or",
    "me",
    "tell",
    "explain",
}

GENERIC_FILE_KEYWORDS = {"readme", "kb index", "kb_index", "index"}


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", (text or "").lower())


def _kb_paths() -> Dict[str, str]:
    paths = dict(_BASE_KB_PATHS)
    raw_extra = os.getenv("UNIGURU_KB_EXTRA_PATHS", "").strip()
    if not raw_extra:
        return paths

    for candidate in raw_extra.split(","):
        normalized = candidate.strip()
        if not normalized:
            continue
        if not os.path.isabs(normalized):
            normalized = os.path.normpath(os.path.join(_KB_ROOT, normalized))
        category = os.path.basename(normalized).lower().replace(" ", "_") or "extra"
        key = f"extra_{category}"
        paths[key] = normalized
    return paths


class AdvancedRetriever:
    """
    Multi-source internal KB retriever.
    Only local knowledge paths are used.
    """

    def __init__(self, top_n: int = 3):
        self.top_n = top_n
        self.knowledge_map: Dict[str, str] = {}
        self.source_map: Dict[str, str] = {}
        self.file_map: Dict[str, str] = {}
        self.path_map: Dict[str, str] = {}
        self._documents: List[Dict[str, Any]] = []
        self._load_memory()

    def _load_memory(self) -> None:
        for kb_name, kb_path in _kb_paths().items():
            if not os.path.exists(kb_path):
                continue
            for root, _, files in os.walk(kb_path):
                for file_name in files:
                    if not file_name.endswith(".md"):
                        continue
                    full_path = os.path.join(root, file_name)
                    keyword = os.path.splitext(file_name)[0].lower().replace("_", " ")
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            content = f.read()
                    except OSError:
                        # Demo-safety mode: unreadable KB files are skipped, not fatal.
                        continue

                    relative_path = os.path.relpath(full_path, _KB_ROOT).replace("\\", "/")
                    keyword_tokens = {token for token in _tokenize(keyword) if token not in STOPWORDS}
                    content_tokens = {token for token in _tokenize(content) if token not in STOPWORDS}
                    is_generic = keyword in GENERIC_FILE_KEYWORDS

                    self.knowledge_map[keyword] = content
                    self.source_map[keyword] = kb_name
                    self.file_map[keyword] = file_name
                    self.path_map[keyword] = relative_path
                    self._documents.append(
                        {
                            "keyword": keyword,
                            "keyword_tokens": keyword_tokens,
                            "content_tokens": content_tokens,
                            "content": content,
                            "source": kb_name,
                            "file": file_name,
                            "path": relative_path,
                            "is_generic": is_generic,
                        }
                    )

    def retrieve_multi(self, query: str) -> List[Dict[str, Any]]:
        """Retrieves top N documents matching the query."""
        query_lower = str(query or "").lower()
        query_tokens = [token for token in _tokenize(query_lower) if token not in STOPWORDS]
        if not query_tokens:
            return []
        query_token_set = set(query_tokens)

        matches = []
        for document in self._documents:
            kw_tokens = document["keyword_tokens"]
            content_tokens = document["content_tokens"]
            keyword_overlap = query_token_set.intersection(kw_tokens)
            content_overlap = query_token_set.intersection(content_tokens)
            exact_phrase_match = 1.0 if document["keyword"] in query_lower else 0.0

            if (
                not keyword_overlap
                and not content_overlap
                and exact_phrase_match == 0.0
            ):
                continue

            if len(query_token_set) >= 3 and len(content_overlap) < 2 and exact_phrase_match == 0.0:
                # Reduces accidental matches on single token overlaps for longer queries.
                continue

            keyword_coverage = len(keyword_overlap) / max(len(kw_tokens), 1)
            query_coverage = len(content_overlap) / len(query_token_set)
            specificity_bonus = 0.08 if kw_tokens and kw_tokens.issubset(query_token_set) else 0.0
            generic_penalty = 0.12 if document["is_generic"] else 0.0

            confidence = (0.5 * keyword_coverage) + (0.35 * query_coverage) + (0.15 * exact_phrase_match)
            confidence = max(0.0, min(confidence + specificity_bonus - generic_penalty, 1.0))
            if confidence < 0.2:
                continue
            matches.append(
                {
                    "content": document["content"],
                    "confidence": confidence,
                    "keyword": document["keyword"],
                    "keyword_match_count": len(keyword_overlap),
                    "content_match_count": len(content_overlap),
                    "matched_tokens": sorted(content_overlap),
                    "query_token_count": len(query_token_set),
                    "source": document["source"],
                    "file": document["file"],
                    "path": document["path"],
                }
            )

        matches.sort(
            key=lambda x: (
                float(x["confidence"]),
                int(x["keyword_match_count"]),
                int(x["content_match_count"]),
            ),
            reverse=True,
        )
        return matches[0 : self.top_n]

    def reason_and_compare(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Structured comparison and conflict detection across local sources."""
        if not results:
            return {"decision": "no_match", "content": None, "reasoning": "No relevant documents found."}

        num_docs = len(results)
        primary = results[0]

        sources_list = [r.get("source", "unknown") for r in results]
        unique_sources = list(set(sources_list))

        reasoning_str = (
            f"Retrieved {num_docs} documents from {len(unique_sources)} internal sources "
            f"({', '.join(unique_sources)})."
        )

        status = "AGREEMENT"
        if num_docs > 1:
            first_len = len(str(primary.get("content", "")))
            for i in range(1, num_docs):
                result = results[i]
                result_content = str(result.get("content", ""))
                if abs(len(result_content) - first_len) > 2000:
                    status = "POTENTIAL_CONTRADICTION"
                    reasoning_str = (
                        f"{reasoning_str} Warning: significant variance in source detail detected."
                    )
                    break

        return {
            "decision": "answer",
            "content": primary.get("content"),
            "verification_status": "VERIFIED" if status == "AGREEMENT" else "PARTIAL",
            "reasoning": reasoning_str,
            "status": status,
            "metadata": {
                "sources_consulted": sources_list,
                "top_match": primary.get("file"),
                "top_match_path": primary.get("path"),
                "top_keyword": primary.get("keyword"),
                "keyword_match_count": primary.get("keyword_match_count", 0),
                "content_match_count": primary.get("content_match_count", 0),
                "matched_tokens": primary.get("matched_tokens", []),
                "query_token_count": primary.get("query_token_count", 0),
                "top_confidence": primary.get("confidence", 0.0),
            },
        }


def retrieve_advanced(query: str) -> Dict[str, Any]:
    try:
        retriever = AdvancedRetriever()
        results = retriever.retrieve_multi(query)
        return retriever.reason_and_compare(results)
    except Exception:
        return {"decision": "no_match", "content": None, "reasoning": "Retriever fallback mode activated."}


def retrieve_knowledge(query: str) -> Optional[str]:
    result = retrieve_advanced(query)
    return result.get("content") if result.get("decision") == "answer" else None


def retrieve_knowledge_with_trace(query: str) -> Tuple[Optional[str], Dict[str, Any]]:
    try:
        retriever = AdvancedRetriever()
        results = retriever.retrieve_multi(query)
        result = retriever.reason_and_compare(results)
    except Exception:
        trace = {
            "engine": "AdvancedRetriever_v2",
            "kb_path": _KB_ROOT,
            "match_found": False,
            "confidence": 0.0,
            "kb_file": None,
            "sources_consulted": ["retriever_fallback", "ontology_registry", "ontology_graph"],
        }
        return None, trace

    if result.get("decision") == "answer" and result.get("content"):
        metadata = result.get("metadata") or {}
        trace = {
            "engine": "AdvancedRetriever_v2",
            "kb_path": _KB_ROOT,
            "match_found": True,
            "confidence": float(metadata.get("top_confidence", 0.0)),
            "kb_file": metadata.get("top_match"),
            "kb_file_path": metadata.get("top_match_path"),
            "matched_keyword": metadata.get("top_keyword"),
            "keyword_match_count": int(metadata.get("keyword_match_count", 0)),
            "content_match_count": int(metadata.get("content_match_count", 0)),
            "matched_tokens": list(metadata.get("matched_tokens", [])),
            "query_token_count": int(metadata.get("query_token_count", 0)),
            "sources_consulted": metadata.get("sources_consulted", []),
        }
        concept_resolution = ConceptResolver().resolve(query=query, retrieval_trace=trace)
        reasoning_path = GraphReasoner().reasoning_path_from_domain_root(
            concept_id=concept_resolution["concept_id"],
            domain=concept_resolution["domain"],
        )
        trace["ontology_domain"] = concept_resolution["domain"]
        trace["ontology_concept_id"] = concept_resolution["concept_id"]
        trace["ontology_relationship_depth"] = len(reasoning_path)
        trace["ontology_relationship_chain"] = [node["concept_id"] for node in reasoning_path]
        trace["sources_consulted"] = sorted(
            set(list(trace["sources_consulted"]) + ["ontology_registry", "ontology_graph"])
        )
        return result.get("content"), trace

    trace = {
        "engine": "AdvancedRetriever_v2",
        "kb_path": _KB_ROOT,
        "match_found": False,
        "confidence": 0.0,
        "kb_file": None,
        "sources_consulted": ["ontology_registry", "ontology_graph"],
    }
    return None, trace
