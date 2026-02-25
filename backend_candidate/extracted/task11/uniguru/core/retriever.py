"""
Simple Knowledge Base Retriever for UniGuru.
Reads markdown files from Quantum_KB and performs primitive keyword search.
"""
import os

KEYWORDS_MAP = {
    # Intro / Foundations
    "quantum": "Foundations/nielsen_chuang_core.md",
    "superposition": "Foundations/nielsen_chuang_core.md",
    "entanglement": "Foundations/nielsen_chuang_core.md",
    "qubit": "Foundations/nielsen_chuang_core.md",
    
    # Algorithms
    "shor": "Quantum_Algorithms/quantum_algorithms_overview.md",
    "grover": "Quantum_Algorithms/quantum_algorithms_overview.md",
    "deutsch": "Quantum_Algorithms/quantum_algorithms_overview.md",
    
    # Hardware (Assuming similar single-file structure, check if fails)
    "transmon": "Quantum_Hardware/transmons.md",
    "ion trap": "Quantum_Hardware/trapped_ions.md",
    "cryogenic": "Quantum_Hardware/cryogenics.md",
    
    # Math
    "linear algebra": "Quantum_Mathematics/linear_algebra.md",
    "complex number": "Quantum_Mathematics/complex_numbers.md",
    "hilbert": "Quantum_Mathematics/hilbert_spaces.md",

    # Biology
    "photosynthesis": "Quantum_Biology/photosynthesis.md",
    "enzymes": "Quantum_Biology/enzyme_catalysis.md",
    
    # Chemistry
    "molecular": "Quantum_Chemistry/molecular_simulation.md",
    "dft": "Quantum_Chemistry/dft.md"
}

def retrieve_knowledge(query):
    query = query.lower()
    kb_root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Quantum_KB")
    
    best_match = None
    
    # Priority: Check direct keyword map
    for keyword, rel_path in KEYWORDS_MAP.items():
        if keyword in query:
            return _read_kb_file(os.path.join(kb_root, rel_path))
            
    return None

def _read_kb_file(path):
    try:
        # Handling potential path issues
        if not os.path.exists(path):
            # Try finding it broadly if exact path fails (resilience)
            dirname, filename = os.path.split(path)
            # This is a simple fallback hack
            return f"[System: KB file {filename} not found at expected path.]"
            
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            # Return a summary (first 500 chars) to avoid blowing up context
            return content[:1000] + "\n... [truncated]"
    except Exception as e:
        return f"[System: Error reading KB: {str(e)}]"
