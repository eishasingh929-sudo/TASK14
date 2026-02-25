import os
import re
import datetime

"""
Offline Ingestion Script for UniGuru Quantum KB.
This script is intended to be run LOCALLY (Offline) to prepare formatted Markdown files
for the Quantum Knowledge Base. It does NOT run in production.

Usage:
    python ingest_paper.py <path_to_pdf_or_text> <category>
"""

def extract_metadata(text):
    """
    Simulated extraction of metadata using regex or simple heuristics.
    In a real scenario, this would use a PDF library or LLM.
    """
    title_match = re.search(r"Title:\s*(.+)", text, re.IGNORECASE)
    author_match = re.search(r"Authors?:\s*(.+)", text, re.IGNORECASE)
    year_match = re.search(r"\b(19|20)\d{2}\b", text)
    
    return {
        "title": title_match.group(1) if title_match else "Unknown Title",
        "authors": author_match.group(1) if author_match else "Unknown Authors",
        "year": year_match.group(0) if year_match else "Unknown Year",
        "ingestion_date": datetime.date.today().isoformat()
    }

def format_knowledge_entry(content, category):
    meta = extract_metadata(content)
    
    template = f"""# {meta['title']}

- **Source**: {meta['title']} (Extracted)
- **Year**: {meta['year']}
- **Authors**: {meta['authors']}
- **Domain**: {category}
- **Ingestion Date**: {meta['ingestion_date']}

## Summary
{content[:500]}... [Truncated for brevity]

## Full Content
{content}
"""
    return template

def save_to_kb(formatted_content, filename, Category):
    base_path = os.path.join("Quantum_KB", Category)
    os.makedirs(base_path, exist_ok=True)
    
    file_path = os.path.join(base_path, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(formatted_content)
    print(f"Saved to {file_path}")

if __name__ == "__main__":
    # Example usage (Offline Simulation)
    sample_text = """
    Title: Quantum Error Correction Codes
    Authors: P. Shor
    Year: 1996
    
    Quantum error correction is essential for fault-tolerant quantum computation.
    """
    
    formatted = format_knowledge_entry(sample_text, "Quantum_Software")
    save_to_kb(formatted, "shor_qec_1996.md", "Quantum_Software")
