import sys
import os
from retriever.engine import retrieve
from verifier.source_verifier import SourceVerifier

def test_retrieval(query: str):
    print(f"\n--- Testing Query: '{query}' ---")
    result = retrieve(query)
    verified_result = SourceVerifier.verify(result)
    
    print(f"Status: {verified_result['answer'][:100]}...")
    print(f"Verified: {verified_result.get('verified')}")
    print(f"Truth Declaration: {verified_result.get('truth_declaration')}")
    print(f"Source: {verified_result.get('source_file')}")
    print(f"Confidence: {verified_result.get('confidence_level')}")

if __name__ == "__main__":
    # Ensure PYTHONPATH is correct
    # sys.path.append(os.getcwd())
    
    # Test cases based on Quantum_KB already ingested
    test_retrieval("What is a qubit?")
    test_retrieval("Explain quantum entanglement")
    test_retrieval("Who invented something unknown?")
