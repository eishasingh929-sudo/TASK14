import os
import re
import time
import uuid
from typing import List, Dict, Any, Optional, Tuple

KB_BASE_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "knowledge", "Quantum_KB")
)

STOPWORDS = {
    "what", "is", "a", "the", "an", "how", "to", "explain", "tell", "me", "about",
    "of", "and", "or", "in", "on", "at", "for", "with", "by", "from"
}

# ---------------------------
# CORE RETRIEVAL ENGINE V2
# ---------------------------

class RetrievalEngineV2:
    def __init__(self, kb_path: str = KB_BASE_PATH):
        self.kb_path = kb_path
        self.file_index = self._build_index()

    def _build_index(self) -> List[Dict[str, Any]]:
        """
        Recursively scans KB path and builds a normalized file index.
        """
        index = []
        for root, _, files in os.walk(self.kb_path):
            for file in files:
                if file.endswith(".md"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.kb_path)
                    
                    # Tier Logic
                    if os.path.dirname(rel_path) == "":
                        tier = "foundations" if file not in ["README.md", "KB_INDEX.md"] else "general"
                        tier_weight = 1.5 if tier == "foundations" else 0.5
                    else:
                        tier = "domain"
                        tier_weight = 1.0
                    
                    # Normalized keywords for matching (filename without extension)
                    keywords = re.sub(r'[^a-z0-9]', ' ', file.lower().replace(".md", "")).split()
                    
                    index.append({
                        "rel_path": rel_path,
                        "full_path": full_path,
                        "tier": tier,
                        "tier_weight": tier_weight,
                        "filename_keywords": set(keywords)
                    })
        return index

    def normalize_query(self, query: str) -> List[str]:
        """
        Lowercases, strips punctuation, and removes stopwords.
        """
        clean = re.sub(r'[^a-z0-9\s]', '', query.lower())
        tokens = clean.split()
        return [t for t in tokens if t not in STOPWORDS]

    def retrieve(self, query: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Deterministic multi-keyword scoring and retrieval.
        """
        start_time = time.perf_counter()
        normalized_tokens = self.normalize_query(query)
        query_set = set(normalized_tokens)
        
        scoring_results = []
        
        for entry in self.file_index:
            # Intersection of query tokens and filename keywords
            matches = entry["filename_keywords"].intersection(query_set)
            
            if matches:
                # Score = (number of matches) * (tier weight)
                score = len(matches) * entry["tier_weight"]
                scoring_results.append({
                    "file": entry["rel_path"],
                    "full_path": entry["full_path"],
                    "matches": sorted(list(matches)),
                    "score": score,
                    "tier": entry["tier"]
                })
        
        # Deterministic Sort: Score (desc), then Path (asc)
        scoring_results.sort(key=lambda x: (-x["score"], x["file"]))
        
        # Take Top Matches (Threshold = 0)
        selected_matches = []
        for res in scoring_results:
            if res["score"] > 0:
                selected_matches.append(res)
        
        # Result content collection
        contents = []
        final_files = []
        
        # Limit to top 3
        count = 0
        for match in selected_matches:
            if count >= 3:
                break
            
            f_path = str(match["full_path"])
            with open(f_path, "r", encoding="utf-8") as f:
                contents.append(f.read())
                final_files.append(str(match["file"]))
            count += 1
        
        end_time = time.perf_counter()
        
        # Build Trace Log
        top_scores = []
        count = 0
        for r in scoring_results:
            if count >= 5:
                break
            top_scores.append({
                "file": r["file"],
                "matches": r["matches"],
                "score": r["score"],
                "tier": r["tier"]
            })
            count += 1

        trace = {
            "retrieval_trace_id": str(uuid.uuid4()),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "latency_ms": round(float((end_time - start_time) * 1000), 3),
            "query": {
                "original": query,
                "normalized": " ".join(normalized_tokens),
                "tokens": normalized_tokens
            },
            "scoring": top_scores,
            "final_selection": {
                "files": final_files,
                "fallback_triggered": len(final_files) == 0
            }
        }
        
        if not contents:
            return None, trace
            
        final_output = "\n\n---\n\n".join(contents)
        return final_output, trace

# ---------------------------
# LEGACY WRAPPERS
# ---------------------------

_engine = RetrievalEngineV2()

def retrieve_knowledge(query: str) -> Optional[str]:
    """
    Backward compatible function. Returns only the content.
    """
    content, _ = _engine.retrieve(query)
    return content

def retrieve_knowledge_with_trace(query: str) -> Tuple[Optional[str], Dict[str, Any]]:
    """
    V2 interface returning both content and trace.
    """
    return _engine.retrieve(query)
