import os
import sys
import json
import time

sys.path.insert(0, r"c:\Users\Yass0\OneDrive\Desktop\TASK14\backend")

from fastapi.testclient import TestClient
from uniguru.service.api import app

client = TestClient(app)

results = {}

# 1. Zero Failure Proof (20 queries)
zero_failures = []
for i in range(20):
    res = client.post("/ask", json={"query": f"Query {i}"})
    zero_failures.append({
        "status_code": res.status_code,
        "is_empty": len(res.content) == 0
    })
results["zero_failure"] = zero_failures

# 2. Dataset Ingestion Proof (5 queries)
dataset_queries = [
    "Who is Mahavira?",
    "What is Anekantavada?",
    "Tell me about Jain cosmology.",
    "Explain the Karma doctrine in Jainism.",
    "Who is Rishabhadeva?"
]
dataset_responses = []
for q in dataset_queries:
    res = client.post("/ask", json={"query": q})
    dataset_responses.append(res.json())
results["dataset"] = dataset_responses

# 3. LLM Fallback Proof (3 KB, 3 LLM)
kb_queries = [
    "What is Tattvartha Sutra?",
    "Tell me about Shravaka ethics.",
    "What is Sutrakritanga?"
]
kb_responses = []
for q in kb_queries:
    res = client.post("/ask", json={"query": q})
    kb_responses.append(res.json())
results["kb"] = kb_responses

llm_queries = [
    "Tell me a joke about a programmer.",
    "How to make a cake?",
    "What's the weather?"
]
llm_responses = []
for q in llm_queries:
    res = client.post("/ask", json={"query": q})
    llm_responses.append(res.json())
results["llm"] = llm_responses

with open(r"c:\Users\Yass0\OneDrive\Desktop\TASK14\proof_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("Done. Saved to proof_results.json")
