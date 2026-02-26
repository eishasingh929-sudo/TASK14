import os
import re
from typing import Dict, Optional, Tuple, Any, List

# All KB folders — multi-knowledge base support (Phase 3 expansion)
_MODULE_DIR = os.path.dirname(__file__)
_KB_ROOT = os.path.normpath(os.path.join(_MODULE_DIR, "..", "knowledge"))

# Individual KB paths
KB_PATHS: Dict[str, str] = {
    "gurukul":      os.path.normpath(os.path.join(_MODULE_DIR, "..", "Quantum_KB")),
    "jain":         os.path.normpath(os.path.join(_KB_ROOT, "jain")),
    "swaminarayan": os.path.normpath(os.path.join(_KB_ROOT, "swaminarayan")),
    "gurukul_main": os.path.normpath(os.path.join(_KB_ROOT, "gurukul")),
}

# Legacy single-path alias (for backward compat)
KB_BASE_PATH = KB_PATHS["gurukul"]


class KnowledgeRetriever:
    def __init__(self, kb_paths: Optional[Dict[str, str]] = None):
        """
        Multi-knowledge-base retriever.
        Scans ALL configured KB paths (gurukul, jain, swaminarayan).
        """
        self.kb_paths = kb_paths or KB_PATHS
        self.knowledge_map: Dict[str, str] = {}       # keyword -> content
        self.source_map: Dict[str, str] = {}           # keyword -> source kb name
        self.file_map: Dict[str, str] = {}             # keyword -> filename
        self._load_all_memory()

    def _load_all_memory(self):
        """Load all configured KB directories."""
        for kb_name, kb_path in self.kb_paths.items():
            self._load_memory(kb_path, kb_name)
        print(
            f"[KB-MULTI] Total Knowledge Base loaded: {len(self.knowledge_map)} files indexed "
            f"across {len(self.kb_paths)} KB sources."
        )

    def _load_memory(self, kb_path: str, kb_name: str = "unknown"):
        """
        Recursively scans a KB path and loads .md files into memory.
        """
        if not os.path.exists(kb_path):
            print(f"[KB-LOAD] WARNING: KB path not found: {kb_path} (skipping {kb_name})")
            return

        for root, _, files in os.walk(kb_path):
            for file in files:
                if not file.endswith(".md"):
                    continue

                full_path = os.path.join(root, file)

                if not os.path.isfile(full_path):
                    print(f"[RETR-VALIDATION] FAILED: {file} is not a valid file.")
                    continue

                if os.path.getsize(full_path) == 0:
                    print(f"[RETR-VALIDATION] WARNING: {file} is empty. Skipping.")
                    continue

                # keyword = filename without extension
                keyword = os.path.splitext(file)[0].lower().replace("_", " ")

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    self.knowledge_map[keyword] = content
                    self.source_map[keyword] = kb_name
                    self.file_map[keyword] = file
                    print(
                        f"[RETR-LOAD] Indexed [{kb_name}]: {file} ({len(content)} bytes)"
                    )
                except Exception as e:
                    print(f"[RETR-LOAD] Error loading {file}: {e}")

    def retrieve(self, query: str) -> Optional[Tuple[str, float, str]]:
        """
        Hardened multi-KB retrieval.
        Returns (content, confidence, kb_file) or None.
        confidence = matched_keywords / total_meaningful_tokens
        """
        query_lower = query.lower()
        clean_query = re.sub(r"[^\w\s]", "", query_lower)
        tokens = clean_query.split()

        stopwords = {
            "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "for",
            "from", "how", "i", "in", "is", "it", "of", "on", "or", "please",
            "tell", "that", "the", "this", "to", "what", "when", "where", "which",
            "who", "why", "me", "about", "explain",
        }
        meaningful_tokens = [t for t in tokens if t not in stopwords]
        total_tokens = len(meaningful_tokens) if meaningful_tokens else len(tokens)

        if total_tokens == 0:
            return None

        # Sort keywords by length descending for greedy match
        sorted_keywords = sorted(self.knowledge_map.keys(), key=len, reverse=True)

        for kw in sorted_keywords:
            kw_tokens = kw.split()

            # Strategy 1: Exact substring match (full multi-word keyword in query)
            exact_match = kw in query_lower

            # Strategy 2: Partial match — count how many keyword words appear in query
            matched_count = sum(
                1 for t in kw_tokens if t in meaningful_tokens or t in tokens
            )
            partial_ratio = matched_count / max(len(kw_tokens), 1)

            # Accept if exact match OR at least 50% of keyword words appear in query
            if not (exact_match or partial_ratio >= 0.50):
                continue

            # Compute confidence: matched keyword tokens / total meaningful query tokens
            confidence = matched_count / max(total_tokens, 1)

            # For short/single-word queries that partially match keyword,
            # boost confidence — avoids unfair penalty for focused queries
            if total_tokens <= 2 and matched_count >= 1:
                confidence = max(confidence, 0.50)

            if confidence < 0.30:
                print(f"[RETR-LOW-CONF] Confidence {confidence:.2f} < 0.30 for '{kw}'")
                continue

            content = self.knowledge_map[kw]
            kb_file = self.file_map.get(kw, f"{kw.replace(' ', '_')}.md")
            kb_source = self.source_map.get(kw, "unknown")

            print(
                f"[RETR-MATCH] Query matched keyword: '{kw}' "
                f"(Confidence: {confidence:.2f}, KB: {kb_source})"
            )
            print(f"[RETR-VISIBILITY] Loaded KB file: {kb_file}")
            return content, confidence, kb_file

        print(f"[RETR-MISS] No KB match found for query: '{query}'")
        return None

    def list_indexed_files(self) -> List[Dict[str, str]]:
        """Returns a list of all indexed files with their KB source."""
        return [
            {
                "keyword": kw,
                "file": self.file_map.get(kw, ""),
                "kb_source": self.source_map.get(kw, ""),
            }
            for kw in sorted(self.knowledge_map.keys())
        ]


# ---- Singleton instance ------------------------------------------------ #
_retriever = KnowledgeRetriever()


def retrieve_knowledge(query: str) -> Optional[str]:
    """Core retrieval function for UniGuru."""
    result = _retriever.retrieve(query)
    return result[0] if result else None


def retrieve_knowledge_with_trace(query: str) -> Tuple[Optional[str], Dict[str, Any]]:
    """Compatibility wrapper for existing RuleEngine logic."""
    result = _retriever.retrieve(query)
    if result:
        content, confidence, kb_file = result
        trace = {
            "engine": "MultiKB_v3_Hardened",
            "kb_paths": list(KB_PATHS.values()),
            "match_found": True,
            "confidence": confidence,
            "kb_file": kb_file,
        }
        return content, trace

    trace = {
        "engine": "MultiKB_v3_Hardened",
        "kb_paths": list(KB_PATHS.values()),
        "match_found": False,
        "confidence": 0.0,
        "kb_file": None,
    }
    return None, trace
