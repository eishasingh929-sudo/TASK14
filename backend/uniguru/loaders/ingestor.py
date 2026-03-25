import os
import json
import re
from typing import List, Dict, Any
try:
    from loaders.file_parser import FileParser
except ImportError:
    from uniguru.loaders.file_parser import FileParser


class KnowledgeIngestor:
    """
    Ingests files and builds a keyword-based runtime index.
    Saves artifacts under knowledge/index/.
    """

    def __init__(self, index_dir: str = "knowledge/index"):
        self.index_dir = index_dir
        self.parser = FileParser()
        self.index: Dict[str, List[Dict[str, Any]]] = {}
        self.ingestion_log: List[Dict[str, Any]] = []
        self._project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

        if not os.path.exists(self.index_dir):
            os.makedirs(self.index_dir)

    def _clean_text(self, text: str) -> str:
        return re.sub(r"[^\w\s]", " ", text.lower())

    def _extract_keywords(self, text: str) -> List[str]:
        words = self._clean_text(text).split()
        return sorted(set(w for w in words if len(w) > 3))

    @staticmethod
    def _extract_frontmatter_value(content: str, key: str) -> str:
        match = re.search(r"---\s*(.*?)\s*---", content, flags=re.DOTALL)
        if not match:
            return ""
        header = match.group(1)
        for line in header.strip().splitlines():
            if ":" not in line:
                continue
            k, v = line.split(":", 1)
            if k.strip().lower() == key.lower():
                return v.strip()
        return ""

    def ingest_directory(self, directory: str, category: str = "general"):
        """Walks through a directory and ingests all supported files."""
        if not os.path.exists(directory):
            print(f"Directory {directory} does not exist. Skipping.")
            return

        print(f"Ingesting directory: {directory} (Category: {category})")

        for root, _, files in os.walk(directory):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if file_name.lower().endswith(".json"):
                    self._ingest_structured_json(file_path=file_path, category=category)
                    continue
                result = self.parser.parse(file_path)
                if not result or not result.get("content"):
                    continue

                content = result["content"]
                metadata = result["metadata"]
                metadata["path"] = os.path.relpath(file_path, self._project_root).replace("\\", "/")
                metadata["category"] = category
                status = str(
                    metadata.get("verification_status")
                    or self._extract_frontmatter_value(content, "verification_status")
                    or "UNSPECIFIED"
                ).upper()

                if status == "UNSPECIFIED" and category in ["jain", "swaminarayan", "gurukul", "ankita", "nupur"]:
                    status = "VERIFIED"
                
                metadata["verification_status"] = status

                base_keyword = os.path.splitext(file_name)[0].lower().replace("_", " ")
                self._add_to_index(base_keyword, content, metadata)

                dynamic_keywords = self._extract_keywords(base_keyword)[:5]
                for keyword in dynamic_keywords:
                    self._add_to_index(keyword, content, metadata)

                self.ingestion_log.append(
                    {
                        "path": metadata.get("path"),
                        "category": category,
                        "verification_status": metadata.get("verification_status"),
                    }
                )

    def _ingest_structured_json(self, file_path: str, category: str) -> None:
        try:
            with open(file_path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError):
            return

        if isinstance(payload, list):
            entries = [entry for entry in payload if isinstance(entry, dict)]
        elif isinstance(payload, dict) and isinstance(payload.get("entries"), list):
            entries = [entry for entry in payload["entries"] if isinstance(entry, dict)]
        elif isinstance(payload, dict):
            entries = [payload]
        else:
            entries = []

        for index, entry in enumerate(entries, start=1):
            title = str(entry.get("title") or entry.get("name") or f"{os.path.basename(file_path)}-{index}").strip()
            content = str(entry.get("content") or entry.get("answer") or entry.get("details") or "").strip()
            if not title or not content:
                continue

            entry_ref = str(entry.get("id") or entry.get("slug") or index).strip()
            metadata = {
                "source": str(entry.get("source") or title),
                "path": f"{os.path.relpath(file_path, self._project_root).replace(chr(92), '/') }#{entry_ref}",
                "author": str(entry.get("author") or "Unknown"),
                "publication": str(entry.get("publication") or "Unknown"),
                "type": "json-entry",
                "category": category,
                "verification_status": str(entry.get("verification_status") or "VERIFIED").upper(),
            }

            self._add_to_index(title.lower(), content, metadata)
            for keyword in self._extract_keywords(title)[:6]:
                self._add_to_index(keyword, content, metadata)

            self.ingestion_log.append(
                {
                    "path": metadata["path"],
                    "category": category,
                    "verification_status": metadata["verification_status"],
                }
            )

    def _add_to_index(self, keyword: str, content: str, metadata: Dict[str, Any]):
        if keyword not in self.index:
            self.index[keyword] = []

        existing_sources = [entry["metadata"]["path"] for entry in self.index[keyword]]
        if metadata["path"] not in existing_sources:
            self.index[keyword].append({"content": content, "metadata": metadata})

    def _build_runtime_summary(self) -> Dict[str, Any]:
        summary: Dict[str, Any] = {
            "documents_total": len(self.ingestion_log),
            "keywords_total": len(self.index),
            "categories": {},
            "verification_status": {},
        }

        for record in self.ingestion_log:
            category = record["category"]
            status = record["verification_status"]
            summary["categories"][category] = summary["categories"].get(category, 0) + 1
            summary["verification_status"][status] = summary["verification_status"].get(status, 0) + 1

        return summary

    def save_index(self):
        """Saves runtime index and ingestion manifest to disk."""
        index_file = os.path.join(self.index_dir, "master_index.json")
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(self.index, f, indent=2)

        manifest = {
            "summary": self._build_runtime_summary(),
            "ingestion_log": self.ingestion_log,
        }
        manifest_file = os.path.join(self.index_dir, "runtime_manifest.json")
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        print(
            f"Index saved to {index_file} ({len(self.index)} keywords indexed). "
            f"Manifest saved to {manifest_file}."
        )


if __name__ == "__main__":
    ingestor = KnowledgeIngestor()

    ingestor.ingest_directory("backend/uniguru/knowledge/quantum", category="quantum")
    ingestor.ingest_directory("backend/uniguru/knowledge/gurukul", category="gurukul")
    ingestor.ingest_directory("backend/uniguru/knowledge/jain", category="jain")
    ingestor.ingest_directory("backend/uniguru/knowledge/swaminarayan", category="swaminarayan")

    ingestor.save_index()
