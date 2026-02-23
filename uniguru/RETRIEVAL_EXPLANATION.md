# UniGuru Retrieval Layer: Deterministic Grounding

## 1. What is Retrieval?
In AI systems, **Retrieval** is the process of fetching external information to answer a specific query. In UniGuru, retrieval is the bridge between a "Universal Intelligence" and "Specific Knowledge."

## 2. What RAG Means
**RAG (Retrieval-Augmented Generation)** usually involves three steps:
1.  **Retrieve**: Find relevant documents.
2.  **Augment**: Add those documents to the prompt.
3.  **Generate**: Let an LLM write the answer.

**UniGuru modifies step 3**: Instead of "letting an LLM write," UniGuru **extracts and formats** the retrieved content deterministically.

## 3. Embeddings vs. Deterministic Lookup
*   **Embeddings (Stochastic)**: Converts text into math (vectors) and finds "similar" math. This is fuzzy and can lead to matching "cat" with "dog" if their vectors are close.
*   **Deterministic Lookup (UniGuru)**: Uses direct keyword matching. If the query contains "qubit," it loads `qubit.md`. This is 100% predictable and auditable.

## 4. How the Knowledge Base (KB) is Loaded
The `KnowledgeRetriever` class scans a directory (e.g., `Quantum_KB`) at startup:
1.  It iterates through every `.md` file.
2.  It maps the filename (keyword) to the file content.
3.  It stores this in a memory map (Dictionary).

## 5. Visibility Logging (Transparency)
To ensure production traceability, UniGuru prints exactly which file it matched.

**Mock Modification Example:**
```python
def retrieve(self, query: str):
    # ... match logic ...
    for keyword, content in self.knowledge_map.items():
        if keyword in query.lower():
            # VISIBILITY LOGGING: Crucial for production debugging
            print(f"[RETR-VISIBILITY] Successfully loaded ground truth from: {keyword}.md")
            return content
```

## 6. Modification to Show Loaded File
By printing the specific file match, an architect can verify if the system is grounding correctly. If the user asks about "entanglement" and the log shows `qubit.md` was loaded, the architect knows exactly which keyword indexing rule needs tuning.
