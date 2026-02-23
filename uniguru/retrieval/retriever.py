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
            print(f"CRITICAL ERROR: KB path not found at {self.kb_path}")
            return

        for root, _, files in os.walk(self.kb_path):
            for file in files:
                if file.endswith(".md"):
                    full_path = os.path.join(root, file)
                    
                    # 2.1 File Validation Check
                    if not os.path.isfile(full_path):
                        print(f"[RETR-VALIDATION] FAILED: {file} is not a valid file.")
                        continue
                        
                    if os.path.getsize(full_path) == 0:
                        print(f"[RETR-VALIDATION] WARNING: {file} is empty. Skipping.")
                        continue

                    # keyword = filename without extension (e.g., 'qubit')
                    keyword = os.path.splitext(file)[0].lower().replace("_", " ")
                    
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            self.knowledge_map[keyword] = content
                            print(f"[RETR-LOAD] Successfully indexed: {file} (Size: {len(content)} bytes)")
                    except Exception as e:
                        print(f"Error loading {file}: {e}")

        print(f"UniGuru Knowledge Base Loaded: {len(self.knowledge_map)} files indexed.")

    def retrieve(self, query: str) -> Optional[Tuple[str, float, str]]:
        """
        Hardened retrieval: Returns (content, confidence, kb_file) or None.
        confidence = matched_keywords / total_tokens
        """
        query_lower = query.lower()
        # Simple tokenization by whitespace and removal of punctuation
        clean_query = re.sub(r'[^\w\s]', '', query_lower)
        tokens = clean_query.split()
        total_tokens = len(tokens)
        
        if total_tokens == 0:
            return None
        
        # Sort keywords by length descending for greedy match
        sorted_keywords = sorted(self.knowledge_map.keys(), key=len, reverse=True)
        
        for kw in sorted_keywords:
            if kw in query_lower:
                # matched_keywords is the number of tokens in the keyword
                kw_tokens = kw.split()
                # Simplified: Confidence is the ratio of matching tokens
                # Actually user specified: matched_keywords / total_tokens
                # If kw has multiple words, we count those words.
                confidence = len(kw_tokens) / total_tokens
                
                # Minimum threshold per SECTION 4
                if confidence < 0.30:
                    print(f"[RETR-LOW-CONF] Confidence {confidence:.2f} < 0.30 for '{kw}'")
                    continue

                content = self.knowledge_map[kw]
                # Find the filename
                kb_file = f"{kw.replace(' ', '_')}.md"
                
                print(f"[RETR-MATCH] Query matched keyword: '{kw}' (Confidence: {confidence:.2f})")
                print(f"[RETR-VISIBILITY] Loaded KB file: {kb_file}")
                return content, confidence, kb_file
        
        print(f"[RETR-MISS] No KB match found for query: '{query}'")
        return None

# Singleton instance
_retriever = KnowledgeRetriever()

def retrieve_knowledge(query: str) -> Optional[str]:
    """
    Core retrieval function for UniGuru.
    """
    result = _retriever.retrieve(query)
    return result[0] if result else None

def retrieve_knowledge_with_trace(query: str) -> Tuple[Optional[str], Dict[str, Any]]:
    """
    Compatibility wrapper for existing RuleEngine logic.
    """
    result = _retriever.retrieve(query)
    if result:
        content, confidence, kb_file = result
        trace = {
            "engine": "DynamicKB_v2_Hardened",
            "kb_path": KB_BASE_PATH,
            "match_found": True,
            "confidence": confidence,
            "kb_file": kb_file
        }
        return content, trace
    
    trace = {
        "engine": "DynamicKB_v2_Hardened",
        "kb_path": KB_BASE_PATH,
        "match_found": False,
        "confidence": 0.0,
        "kb_file": None
    }
    return None, trace
