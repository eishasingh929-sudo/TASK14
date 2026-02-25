from typing import Dict, Any

class SourceVerifier:
    """
    Verifies the integrity and authenticity of retrieved information.
    """
    @staticmethod
    def verify(retrieval_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhances retrieval result with verification metadata.
        """
        if not retrieval_result.get("verified"):
            retrieval_result["truth_declaration"] = "UNVERIFIABLE"
            return retrieval_result
            
        # Basic verification: Check if source and author are present
        source = retrieval_result.get("source_file")
        author = retrieval_result.get("author")
        
        if source and author != "Unknown":
            retrieval_result["truth_declaration"] = "VERIFIED"
            retrieval_result["verification_level"] = "HIGH"
        elif source:
            retrieval_result["truth_declaration"] = "VERIFIED_PARTIAL"
            retrieval_result["verification_level"] = "MEDIUM"
        else:
            retrieval_result["truth_declaration"] = "UNVERIFIED"
            retrieval_result["verification_level"] = "LOW"
            
        return retrieval_result

    @staticmethod
    def verify_retrieval_trace(trace: Dict[str, Any], min_confidence: float = 0.5) -> Dict[str, Any]:
        """
        Normalizes retrieval trace output and runs verification with a confidence gate.
        """
        confidence = float(trace.get("confidence", 0.0) or 0.0)
        source_file = trace.get("kb_file")
        payload = {
            "verified": bool(trace.get("match_found")) and confidence >= min_confidence and bool(source_file),
            "source_file": source_file,
            "author": "UniGuru KB",
            "confidence": confidence,
            "confidence_threshold": min_confidence
        }
        return SourceVerifier.verify(payload)
