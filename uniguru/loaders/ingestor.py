import os
import json
import re
from typing import List, Dict, Any
from loaders.file_parser import FileParser

class KnowledgeIngestor:
    """
    Ingests files from various directories and builds a keyword-based index.
    Saves the index to knowledge/index/
    """
    def __init__(self, index_dir: str = "knowledge/index"):
        self.index_dir = index_dir
        self.parser = FileParser()
        self.index = {} # keyword -> list of {content, metadata}

        if not os.path.exists(self.index_dir):
            os.makedirs(self.index_dir)

    def _clean_text(self, text: str) -> str:
        # Remove non-alphanumeric except spaces
        return re.sub(r'[^\w\s]', '', text.lower())

    def _extract_keywords(self, text: str) -> List[str]:
        # Simple keyword extraction: unique words longer than 3 chars
        words = self._clean_text(text).split()
        return list(set([w for w in words if len(w) > 3]))

    def ingest_directory(self, directory: str, category: str = "general"):
        """
        Walks through a directory and ingests all supported files.
        """
        if not os.path.exists(directory):
            print(f"Directory {directory} does not exist. Skipping.")
            return

        print(f"Ingesting directory: {directory} (Category: {category})")
        
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                result = self.parser.parse(file_path)
                
                if result and result["content"]:
                    content = result["content"]
                    metadata = result["metadata"]
                    metadata["category"] = category
                    
                    # Also use filename as a primary keyword
                    base_keyword = os.path.splitext(file)[0].lower().replace("_", " ")
                    self._add_to_index(base_keyword, content, metadata)
                    
                    # Optionally extract more keywords from content
                    # For simple retrieve engine, we might just use key concepts
                    # But the prompt says "Keyword match", so filename is usually the key.

    def _add_to_index(self, keyword: str, content: str, metadata: Dict[str, Any]):
        if keyword not in self.index:
            self.index[keyword] = []
        
        # Check if already exists to avoid duplicates
        existing_sources = [m["metadata"]["path"] for m in self.index[keyword]]
        if metadata["path"] not in existing_sources:
            self.index[keyword].append({
                "content": content,
                "metadata": metadata
            })

    def save_index(self):
        """
        Saves the memory index to disk.
        """
        index_file = os.path.join(self.index_dir, "master_index.json")
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(self.index, f, indent=2)
        print(f"Index saved to {index_file} ({len(self.index)} keywords indexed).")

if __name__ == "__main__":
    ingestor = KnowledgeIngestor()
    
    # Phase 1: Quantum KB
    ingestor.ingest_directory("Quantum_KB", category="quantum")
    
    # Phase 2: Gurukul KB
    ingestor.ingest_directory("knowledge/gurukul", category="gurukul")
    
    # Phase 3 & 4 (Future holders)
    ingestor.ingest_directory("knowledge/jain", category="jain")
    ingestor.ingest_directory("knowledge/swaminarayan", category="swaminarayan")
    
    ingestor.save_index()
