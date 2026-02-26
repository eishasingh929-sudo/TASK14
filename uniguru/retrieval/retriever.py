import os
import re
from typing import Dict, Optional, Tuple, Any, List
from uniguru.verifier.source_verifier import SourceVerifier

# Paths for Knowledge Bases
_MODULE_DIR = os.path.dirname(__file__)
_KB_ROOT = os.path.normpath(os.path.join(_MODULE_DIR, "..", "knowledge"))

KB_PATHS: Dict[str, str] = {
    "gurukul":      os.path.normpath(os.path.join(_MODULE_DIR, "..", "Quantum_KB")),
    "jain":         os.path.normpath(os.path.join(_KB_ROOT, "jain")),
    "swaminarayan": os.path.normpath(os.path.join(_KB_ROOT, "swaminarayan")),
    "gurukul_main": os.path.normpath(os.path.join(_KB_ROOT, "gurukul")),
}

class AdvancedRetriever:
    """
    Upgraded Multi-Source Retriever.
    Supports Top-N retrieval, Source Comparison, and Conflict Detection.
    """
    def __init__(self, top_n: int = 3):
        self.top_n = top_n
        self.knowledge_map: Dict[str, str] = {}
        self.source_map: Dict[str, str] = {}
        self.file_map: Dict[str, str] = {}
        self._load_memory()

    def _load_memory(self):
        for kb_name, kb_path in KB_PATHS.items():
            if not os.path.exists(kb_path): continue
            for root, _, files in os.walk(kb_path):
                for file in files:
                    if not file.endswith(".md"): continue
                    full_path = os.path.join(root, file)
                    keyword = os.path.splitext(file)[0].lower().replace("_", " ")
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    self.knowledge_map[keyword] = content
                    self.source_map[keyword] = kb_name
                    self.file_map[keyword] = file

    def retrieve_multi(self, query: str) -> List[Dict[str, Any]]:
        """Retrieves top N documents matching the query."""
        query_lower = query.lower()
        clean_query = re.sub(r"[^\w\s]", "", query_lower)
        tokens = clean_query.split()
        
        matches = []
        for kw, content in self.knowledge_map.items():
            kw_tokens = kw.split()
            matched_count = sum(1 for t in kw_tokens if t in tokens)
            if matched_count > 0:
                confidence = matched_count / len(tokens) if tokens else 0
                matches.append({
                    "content": content,
                    "confidence": confidence,
                    "keyword": kw,
                    "source": self.source_map.get(kw, "unknown"),
                    "file": self.file_map.get(kw, "unknown")
                })
        
        # Sort by confidence
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        return matches[0:self.top_n]

    def reason_and_compare(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Structured comparison and conflict detection.
        Identifies if sources agree or contradict.
        """
        if not results:
            return {"decision": "no_match", "content": None, "reasoning": "No relevant documents found."}

        num_docs = len(results)
        primary = results[0]
        
        sources_list = [r.get("source", "unknown") for r in results]
        unique_sources = list(set(sources_list))
        
        reasoning_str = f"Retrieved {num_docs} documents from {len(unique_sources)} sources ({', '.join(unique_sources)})."
        
        status = "AGREEMENT"
        if num_docs > 1:
            # Check for significant length or content differences as a proxy for conflict
            first_len = len(str(primary.get("content", "")))
            for i in range(1, num_docs):
                r = results[i]
                r_content = str(r.get("content", ""))
                if abs(len(r_content) - first_len) > 2000:
                    status = "POTENTIAL_CONTRADICTION"
                    reasoning_str = f"{reasoning_str} Warning: Significant variance in source detail detected."
                    break
        
        return {
            "decision": "answer",
            "content": primary.get("content"),
            "verification_status": "VERIFIED" if status == "AGREEMENT" else "PARTIAL",
            "reasoning": reasoning_str,
            "status": status,
            "metadata": {
                "sources_consulted": sources_list,
                "top_match": primary.get("file")
            }
        }

def retrieve_advanced(query: str) -> Dict[str, Any]:
    retriever = AdvancedRetriever()
    results = retriever.retrieve_multi(query)
    return retriever.reason_and_compare(results)
