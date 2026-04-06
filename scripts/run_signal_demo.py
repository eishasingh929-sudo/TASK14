"""
scripts/run_signal_demo.py
--------------------------
Example run of the signal pipeline with 5 mock queries.

Usage (from repo root):
    python scripts/run_signal_demo.py

Output:
  - Printed structured results for each query
  - Log entries appended to demo_logs/signal_bucket_log.jsonl
"""
from __future__ import annotations

import json
import os
import sys

# Ensure backend/ is on the path when run from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from uniguru.runtime_env import load_project_env
load_project_env()

from uniguru.signals.pipeline import run_signal_pipeline

DEMO_QUERIES = [
    "What is a qubit?",
    "How should I prepare a resume for placements?",
    "Explain ahimsa in Jainism.",
    "hello there",
    "sudo rm -rf /",
]


def _print_result(query: str, result: dict) -> None:
    print(f"\n{'='*70}")
    print(f"QUERY       : {query}")
    print(f"REQUEST ID  : {result['request_id']}")
    print(f"INTENT      : {result['intent']}")
    print(f"CONFIDENCE  : {result['confidence']}")
    print(f"DEGRADED    : {result['degradation_flag']}")
    print(f"EVENT ID    : {result['event_id']}")
    print(f"LATENCY     : {result['latency_ms']} ms")
    print(f"\nFINAL ANSWER:\n  {result['final_answer'][:200]}{'...' if len(result['final_answer']) > 200 else ''}")
    print(f"\nSIGNALS USED ({len(result['supporting_signals'])}):")
    for sig in result["supporting_signals"]:
        print(f"  [{sig['confidence']:.2f}] {sig['source']}")
        print(f"         {sig['content'][:120]}...")
    print(f"\nREASONING TRACE:")
    for step in result["reasoning_trace"]:
        print(f"  {step}")


def main() -> None:
    print("UniGuru Signal Pipeline — Demo Run")
    print(f"Queries: {len(DEMO_QUERIES)}")

    all_results = []
    for query in DEMO_QUERIES:
        result = run_signal_pipeline(query)
        _print_result(query, result)
        all_results.append({"query": query, "result": result})

    # Write demo output JSON
    output_path = os.path.join(
        os.path.dirname(__file__), "..", "demo_logs", "signal_pipeline_demo.json"
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(all_results, fh, indent=2, ensure_ascii=False)

    print(f"\n{'='*70}")
    print(f"Demo complete. {len(DEMO_QUERIES)} queries processed.")
    print(f"Structured output : demo_logs/signal_pipeline_demo.json")
    print(f"Bucket log        : demo_logs/signal_bucket_log.jsonl")


if __name__ == "__main__":
    main()
