# UniGuru Sovereign Knowledge Engine Architecture

## Overview
The UniGuru Sovereign Knowledge Engine is a deterministic, non-LLM based information retrieval system designed to provide verified answers from local knowledge bases. It replaces external LLM dependency with a structured index and keyword-based retrieval mechanism.

## Core Components

### 1. File Parser (`loaders/file_parser.py`)
- **Responsibility**: Extracts text and metadata from `.md`, `.txt`, and `.pdf` files.
- **Capabilities**: 
  - Parses YAML-like frontmatter from Markdown files.
  - Uses `PyMuPDF` (fitz) for high-fidelity PDF text extraction.
  - Captures source, author, and publication details.

### 2. Knowledge Ingestor (`loaders/ingestor.py`)
- **Responsibility**: Scans directories, processes files via the `FileParser`, and builds a keyword index.
- **Index Structure**: Map of `keyword` to a list of `{content, metadata}` objects.
- **Storage**: Persists the index as a JSON file in `knowledge/index/master_index.json`.

### 3. Sovereign Retriever (`retriever/engine.py`)
- **Responsibility**: Performs keyword matching against the query.
- **Algorithm**: 
  - Greedy multi-word keyword matching (longest match first).
  - Calculates confidence based on token overlap.
- **Output**: Returns structured data including answer content, source file, author, and confidence.

### 4. Source Verifier (`verifier/source_verifier.py`)
- **Responsibility**: Validates the retrieval result.
- **Truth Declaration**:
  - `VERIFIED`: High confidence with source and author.
  - `VERIFIED_PARTIAL`: Confidence with source only.
  - `UNVERIFIABLE`: No match found or unverifiable source.

## Retrieval Process Flow
1. **Input**: User Query
2. **Matching**: Engine looks for keywords/phrases in the query that exist in the `master_index.json`.
3. **Selection**: If multiple matches exist, the one with highest confidence/longest keyword is chosen.
4. **Verification**: `SourceVerifier` audits the match and assigns a truth declaration.
5. **Assembly**: Final response is built with explicit source citation and truth declaration.

## Safety Constraints
- **Zero Hallucination**: No text is generated; only retrieved content is returned.
- **Source Traceability**: Every answer must have a traceable source file.
- **Refusal Mechanism**: If no match is found above the 0.3 confidence threshold, the system returns a standardized "I do not have verified knowledge" message.
