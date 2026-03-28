import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

from uniguru.reasoning.concept_resolver import ConceptResolver
from uniguru.reasoning.graph_reasoner import GraphReasoner

_MODULE_DIR = os.path.dirname(__file__)
_KB_ROOT = os.path.normpath(os.path.join(_MODULE_DIR, "..", "knowledge"))
_RUNTIME_INDEX_PATH = os.path.normpath(os.path.join(_KB_ROOT, "index", "master_index.json"))

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

GENERIC_FILE_KEYWORDS = {
    "readme",
    "kb index",
    "kb_index",
    "index",
    "algorithm",
    "quantum",
    "teachings",
    "content",
    "answer notes",
}


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", (text or "").lower())


def _token_set(text: str) -> set[str]:
    return {token for token in _tokenize(text) if token not in STOPWORDS}


def _coerce_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        parts = [part.strip() for part in value.split(",")]
        return [part for part in parts if part]
    return []


def _frontmatter(content: str) -> Dict[str, str]:
    match = re.match(r"^\s*---\s*\n(.*?)\n---\s*\n?", content, flags=re.DOTALL)
    if not match:
        return {}
    result: Dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip().lower()] = value.strip()
    return result


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
    """Multi-source local KB retriever with structured dataset support."""

    def __init__(self, top_n: int = 3):
        self.top_n = top_n
        self.knowledge_map: Dict[str, str] = {}
        self.source_map: Dict[str, str] = {}
        self.file_map: Dict[str, str] = {}
        self.path_map: Dict[str, str] = {}
        self._documents: List[Dict[str, Any]] = []
        self._document_ids: set[tuple[str, str]] = set()
        self._load_memory()

    def _append_document(
        self,
        *,
        keyword: str,
        content: str,
        source: str,
        file_name: str,
        relative_path: str,
        source_title: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        sample_queries: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> None:
        keyword = keyword.strip().lower()
        if not keyword or not content.strip():
            return

        alias_list = aliases or []
        sample_query_list = sample_queries or []
        tag_list = tags or []
        title = (source_title or keyword).strip()
        is_generic = keyword in GENERIC_FILE_KEYWORDS
        document_id = (relative_path, keyword)
        if document_id in self._document_ids:
            return
        self._document_ids.add(document_id)

        self.knowledge_map[keyword] = content
        self.source_map[keyword] = source
        self.file_map[keyword] = file_name
        self.path_map[keyword] = relative_path
        self._documents.append(
            {
                "keyword": keyword,
                "keyword_tokens": _token_set(keyword),
                "content_tokens": _token_set(content),
                "alias_tokens": set().union(*[_token_set(alias) for alias in alias_list]) if alias_list else set(),
                "sample_query_tokens": set().union(*[_token_set(item) for item in sample_query_list])
                if sample_query_list
                else set(),
                "aliases": alias_list,
                "sample_queries": sample_query_list,
                "tags": tag_list,
                "content": content,
                "source": source,
                "file": file_name,
                "path": relative_path,
                "source_title": title,
                "is_generic": is_generic,
            }
        )

    def _load_markdown_document(self, kb_name: str, full_path: str, file_name: str) -> None:
        try:
            with open(full_path, "r", encoding="utf-8") as handle:
                content = handle.read()
        except OSError:
            return

        metadata = _frontmatter(content)
        keyword = os.path.splitext(file_name)[0].lower().replace("_", " ")
        relative_path = os.path.relpath(full_path, _KB_ROOT).replace("\\", "/")
        aliases = _coerce_list(metadata.get("aliases"))
        tags = _coerce_list(metadata.get("tags"))
        sample_queries = _coerce_list(metadata.get("sample_queries"))
        source_title = metadata.get("title") or keyword

        self._append_document(
            keyword=keyword,
            content=content,
            source=kb_name,
            file_name=file_name,
            relative_path=relative_path,
            source_title=source_title,
            aliases=aliases,
            sample_queries=sample_queries,
            tags=tags,
        )

    def _load_json_document(self, kb_name: str, full_path: str, file_name: str) -> None:
        try:
            with open(full_path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError):
            return

        entries: List[Dict[str, Any]]
        if isinstance(payload, list):
            entries = [entry for entry in payload if isinstance(entry, dict)]
        elif isinstance(payload, dict) and isinstance(payload.get("entries"), list):
            entries = [entry for entry in payload["entries"] if isinstance(entry, dict)]
        elif isinstance(payload, dict):
            entries = [payload]
        else:
            entries = []

        relative_path = os.path.relpath(full_path, _KB_ROOT).replace("\\", "/")
        for index, entry in enumerate(entries, start=1):
            title = str(entry.get("title") or entry.get("name") or f"{file_name}-{index}").strip()
            content = str(entry.get("content") or entry.get("answer") or entry.get("details") or "").strip()
            source_label = str(entry.get("source") or title).strip()
            entry_id = str(entry.get("id") or entry.get("slug") or index).strip()
            keyword = title.lower()
            aliases = _coerce_list(entry.get("aliases"))
            sample_queries = _coerce_list(entry.get("sample_queries"))
            tags = _coerce_list(entry.get("tags"))

            self._append_document(
                keyword=keyword,
                content=content,
                source=kb_name,
                file_name=file_name,
                relative_path=f"{relative_path}#{entry_id}",
                source_title=source_label,
                aliases=aliases,
                sample_queries=sample_queries,
                tags=tags,
            )

    def _load_runtime_index(self) -> None:
        if not os.path.exists(_RUNTIME_INDEX_PATH):
            return
        try:
            with open(_RUNTIME_INDEX_PATH, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError):
            return

        if not isinstance(payload, dict):
            return

        for keyword, entries in payload.items():
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                content = str(entry.get("content") or "").strip()
                metadata = entry.get("metadata") if isinstance(entry.get("metadata"), dict) else {}
                relative_path = str(metadata.get("path") or metadata.get("source") or f"index/{keyword}").strip()
                relative_path = relative_path.replace("\\", "/")
                file_name = os.path.basename(relative_path.split("#", 1)[0]) or f"{keyword}.md"
                self._append_document(
                    keyword=str(keyword).strip().lower(),
                    content=content,
                    source=str(metadata.get("category") or metadata.get("source") or "indexed_kb"),
                    file_name=file_name,
                    relative_path=relative_path,
                    source_title=str(metadata.get("source") or keyword).strip(),
                    aliases=[str(keyword).replace("_", " ")],
                    tags=_coerce_list(metadata.get("category")),
                )

    def _load_memory(self) -> None:
        for kb_name, kb_path in _kb_paths().items():
            if not os.path.exists(kb_path):
                continue
            for root, _, files in os.walk(kb_path):
                for file_name in files:
                    full_path = os.path.join(root, file_name)
                    lower = file_name.lower()
                    if lower.endswith(".md"):
                        self._load_markdown_document(kb_name=kb_name, full_path=full_path, file_name=file_name)
                    elif lower.endswith(".json"):
                        self._load_json_document(kb_name=kb_name, full_path=full_path, file_name=file_name)
        self._load_runtime_index()

    def retrieve_multi(self, query: str) -> List[Dict[str, Any]]:
        query_lower = str(query or "").lower()
        query_token_set = _token_set(query_lower)
        if not query_token_set:
            return []

        matches = []
        for document in self._documents:
            keyword_overlap = query_token_set.intersection(document["keyword_tokens"])
            content_overlap = query_token_set.intersection(document["content_tokens"])
            alias_overlap = query_token_set.intersection(document["alias_tokens"])
            sample_query_overlap = query_token_set.intersection(document["sample_query_tokens"])
            exact_keyword_match = 1.0 if document["keyword"] in query_lower else 0.0
            exact_alias_match = 1.0 if any(alias.lower() in query_lower for alias in document["aliases"]) else 0.0

            if not any(
                (
                    keyword_overlap,
                    content_overlap,
                    alias_overlap,
                    sample_query_overlap,
                    exact_keyword_match,
                    exact_alias_match,
                )
            ):
                continue

            if len(query_token_set) >= 4 and not (keyword_overlap or alias_overlap or sample_query_overlap):
                if len(content_overlap) < 2:
                    continue

            keyword_coverage = len(keyword_overlap) / max(len(document["keyword_tokens"]), 1)
            content_coverage = len(content_overlap) / len(query_token_set)
            alias_coverage = len(alias_overlap) / max(len(document["alias_tokens"]), 1) if document["alias_tokens"] else 0.0
            sample_query_coverage = (
                len(sample_query_overlap) / max(len(document["sample_query_tokens"]), 1)
                if document["sample_query_tokens"]
                else 0.0
            )
            generic_penalty = 0.12 if document["is_generic"] else 0.0
            specificity_bonus = 0.1 if document["keyword_tokens"] and document["keyword_tokens"].issubset(query_token_set) else 0.0

            confidence = (
                0.35 * keyword_coverage
                + 0.25 * content_coverage
                + 0.2 * max(alias_coverage, exact_alias_match)
                + 0.1 * sample_query_coverage
                + 0.1 * exact_keyword_match
            )
            confidence = max(0.0, min(confidence + specificity_bonus - generic_penalty, 1.0))
            if confidence < 0.22:
                continue

            matched_tokens = sorted(set(content_overlap) | set(keyword_overlap) | set(alias_overlap) | set(sample_query_overlap))
            matches.append(
                {
                    "content": document["content"],
                    "confidence": confidence,
                    "keyword": document["keyword"],
                    "keyword_match_count": len(keyword_overlap),
                    "content_match_count": len(content_overlap),
                    "matched_tokens": matched_tokens,
                    "query_token_count": len(query_token_set),
                    "source": document["source"],
                    "file": document["file"],
                    "path": document["path"],
                    "source_title": document["source_title"],
                    "sample_queries": document["sample_queries"],
                }
            )

        matches.sort(
            key=lambda item: (
                float(item["confidence"]),
                int(item["keyword_match_count"]),
                int(item["content_match_count"]),
            ),
            reverse=True,
        )
        return matches[0 : self.top_n]

    def reason_and_compare(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not results:
            return {"decision": "no_match", "content": None, "reasoning": "No relevant documents found."}

        primary = results[0]
        sources_list = [result.get("path", "unknown") for result in results]
        unique_sources = list(dict.fromkeys(sources_list))
        status = "AGREEMENT"

        if len(results) > 1:
            first_len = len(str(primary.get("content", "")))
            for result in results[1:]:
                if abs(len(str(result.get("content", ""))) - first_len) > 2000:
                    status = "POTENTIAL_CONTRADICTION"
                    break

        return {
            "decision": "answer",
            "content": primary.get("content"),
            "verification_status": "VERIFIED" if status == "AGREEMENT" else "PARTIAL",
            "reasoning": f"Retrieved {len(results)} documents from {len(unique_sources)} internal sources.",
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
                "source_title": primary.get("source_title"),
                "sample_queries": primary.get("sample_queries", []),
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
            "engine": "AdvancedRetriever_v3",
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
            "engine": "AdvancedRetriever_v3",
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
            "source_title": metadata.get("source_title"),
            "sample_queries": metadata.get("sample_queries", []),
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
        "engine": "AdvancedRetriever_v3",
        "kb_path": _KB_ROOT,
        "match_found": False,
        "confidence": 0.0,
        "kb_file": None,
        "sources_consulted": ["ontology_registry", "ontology_graph"],
    }
    return None, trace
