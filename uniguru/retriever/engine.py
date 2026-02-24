import os
import json
import re
from typing import Dict, Any, List, Optional, Tuple

class SovereignRetriever:
    """
    Sovereign Retrieval Engine for UniGuru.
    Operates on the structured index in knowledge/index/
    """
    def __init__(self, index_path: str = "knowledge/index/master_index.json"):
        self.index_path = index_path
        self.index = {}
        self._load_index()

    def _load_index(self):
        if os.path.exists(self.index_path):
            with open(self.index_path, "r", encoding="utf-8") as f:
                self.index = json.load(f)
            print(f"Sovereign Index Loaded: {len(self.index)} keywords available.")
        else:
            print(f"WARNING: Index not found at {self.index_path}")

    def _calculate_confidence(self, query: str, keyword: str) -> float:
        """
        Calculates confidence based on keyword coverage in query tokens.
        """
        query_tokens = set(re.sub(r'[^\w\s]', '', query.lower()).split())
        kw_tokens = set(keyword.split())
        
        if not kw_tokens:
            return 0.0
            
        matched = kw_tokens.intersection(query_tokens)
        return len(matched) / len(kw_tokens) if len(kw_tokens) > 0 else 0.0

    def query(self, user_query: str) -> Dict[str, Any]:
        """
        Main entry point for retrieval.
        Returns a structured response with source trace.
        """
        query_lower = user_query.lower()
        best_match = None
        highest_confidence = 0.0
        
        # Greedy multi-word keyword matching
        sorted_keywords = sorted(self.index.keys(), key=len, reverse=True)
        
        for kw in sorted_keywords:
            if kw in query_lower:
                # Basic confidence: if the keyword is in the query
                # We can also check token overlap
                conf = self._calculate_confidence(user_query, kw)
                
                # If substring match, we give it a boost if it's the exact phrase
                if kw in query_lower:
                    conf = max(conf, 0.5) # Minimum 0.5 for exact phrase match
                
                if conf > highest_confidence:
                    highest_confidence = conf
                    best_match = kw
        
        if best_match and highest_confidence >= 0.3:
            entry = self.index[best_match][0] # Take first source for now
            content = entry["content"]
            meta = entry["metadata"]
            
            return {
                "answer": content,
                "source_file": meta.get("source"),
                "author": meta.get("author"),
                "publication": meta.get("publication"),
                "confidence_level": round(highest_confidence, 2),
                "verified": True
            }
            
        return {
            "answer": "I do not have verified knowledge to answer this question.",
            "source_file": None,
            "confidence_level": 0.0,
            "verified": False
        }

# Singleton for easy access
_engine = SovereignRetriever()

def retrieve(query: str) -> Dict[str, Any]:
    return _engine.query(query)
