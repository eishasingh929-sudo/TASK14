import sys
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from uniguru.loaders.ingestor import KnowledgeIngestor


def _dataset_directories() -> list[tuple[str, str]]:
    configured = [
        ("quantum", "backend/uniguru/knowledge/quantum"),
        ("gurukul", "backend/uniguru/knowledge/gurukul"),
        ("jain", "backend/uniguru/knowledge/jain"),
        ("swaminarayan", "backend/uniguru/knowledge/swaminarayan"),
        ("ankita", "backend/uniguru/knowledge/datasets/ankita"),
        ("nupur", "backend/uniguru/knowledge/datasets/nupur"),
    ]
    extra_dirs = os.getenv("UNIGURU_EXTRA_DATASET_DIRS", "").strip()
    if extra_dirs:
        for raw in extra_dirs.split(","):
            candidate = raw.strip()
            if not candidate:
                continue
            category = Path(candidate).name.lower().replace(" ", "_") or "extra"
            configured.append((category, candidate))
    return configured


def main() -> None:
    ingestor = KnowledgeIngestor(index_dir="backend/uniguru/knowledge/index")
    for category, directory in _dataset_directories():
        ingestor.ingest_directory(directory, category=category)
    ingestor.save_index()

    sample_records = [record for record in ingestor.ingestion_log if record.get("category") in {"ankita", "nupur"}][:8]
    proof = {
        "index_dir": "backend/uniguru/knowledge/index",
        "summary": {
            "documents_total": len(ingestor.ingestion_log),
            "sample_records_count": len(sample_records),
        },
        "sample_ingested_data": sample_records,
    }
    output_path = ROOT / "demo_logs" / "dataset_ingestion_proof.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(proof, indent=2), encoding="utf-8")
    print(str(output_path))


if __name__ == "__main__":
    main()
