import os
import sys

sys.path.insert(0, r"c:\Users\Yass0\OneDrive\Desktop\TASK14\backend")

from fastapi.testclient import TestClient
from uniguru.service.api import app
import json

client = TestClient(app)

# Explicitly test without caller identity headers to ensure Fallback is NOT forced!
res1 = client.post("/ask", json={"query": "Who is Mahavira?"})
res2 = client.post("/ask", json={"query": "Tell me a joke"})
res3 = client.post("/ask", json={"query": "how are you"})

out_data = {
    "kb": res1.json() if res1.status_code == 200 else str(res1.status_code),
    "random": res2.json() if res2.status_code == 200 else str(res2.status_code),
    "llm": res3.json() if res3.status_code == 200 else str(res3.status_code),
}

with open("out.json", "w", encoding="utf-8") as f:
    json.dump(out_data, f, indent=2)

print("Done writing out.json")
