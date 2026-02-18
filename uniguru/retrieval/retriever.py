import os
import re
from typing import Dict, Optional, Tuple, Any

# Locate KB folder at repo root (one level up from retrieval/ folder)
KB_BASE_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "Quantum_KB")
)

class KnowledgeRetriever:
    def __init__(self, kb_path: str = KB_BASE_PATH):
        self.kb_path = kb_path
        self.knowledge_map: Dict[str, str] = {}
        self.keywords: Dict[str, str] = {} # keyword -> content
        self._load_memory()

    def _load_memory(self):
        """
        Recursively scans KB path and loads .md files into memory.
        """
        if not os.path.exists(self.kb_path):
            print(f"WARNING: KB path not found at {self.kb_path}")
            return

        for root, _, files in os.walk(self.kb_path):
            for file in files:
                if file.endswith(".md"):
                    full_path = os.path.join(root, file)
                    # keyword = filename without extension (e.g., 'qubit')
                    keyword = os.path.splitext(file)[0].lower().replace("_", " ")
                    
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            self.knowledge_map[keyword] = content
                    except Exception as e:
                        print(f"Error loading {file}: {e}")

        print(f"UniGuru Knowledge Base Loaded: {len(self.knowledge_map)} files indexed.")

    def retrieve(self, query: str) -> Optional[str]:
        """
        Standardized retrieval logic:
        Check if any keyword appears in the lowercase query.
        """
        query_lower = query.lower()
        
        # Sort keywords by length descending to match longer specific terms first 
        # (e.g., 'density matrix' before 'matrix')
        sorted_keywords = sorted(self.knowledge_map.keys(), key=len, reverse=True)
        
        for kw in sorted_keywords:
            if kw in query_lower:
                return self.knowledge_map[kw]
        
        # Fallback logging
        print(f"KB MISS: {query}")
        return None

# Singleton instance
_retriever = KnowledgeRetriever()

def retrieve_knowledge(query: str) -> Optional[str]:
    """
    Core retrieval function for UniGuru.
    """
    return _retriever.retrieve(query)

def retrieve_knowledge_with_trace(query: str) -> Tuple[Optional[str], Dict[str, Any]]:
    """
    Compatibility wrapper for existing RuleEngine logic.
    """
    content = _retriever.retrieve(query)
    trace = {
        "engine": "DynamicKB_v1",
        "kb_path": KB_BASE_PATH,
        "files_indexed": len(_retriever.knowledge_map),
        "match_found": content is not None
    }
    return content, trace
