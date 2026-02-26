"""
Phase 6 Integration Validation Script
Tests all major components of the UniGuru Bridge system.
"""
import sys
import os
sys.path.insert(0, r"c:\Users\Yass0\OneDrive\Desktop\TASK14")

PASS = "PASS"
FAIL = "FAIL"
results = []

def test(name, condition, detail=""):
    status = PASS if condition else FAIL
    results.append((name, status, detail))
    print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))

print("=" * 60)
print("UniGuru Bridge Integration Validation")
print("=" * 60)

# ---- TEST 1: Enforcement SHA256 Sealing ---------------------------------
print("\n[PHASE 2] Enforcement SHA256 Sealing")
try:
    from uniguru.enforcement.enforcement import UniGuruEnforcement
    e = UniGuruEnforcement()
    sig = e.generate_signature("ahimsa is non-violence", "req-001")
    test("Signature generated", len(sig) == 64, f"{sig[:32]}...")
    ok = e.verify_signature("ahimsa is non-violence", "req-001", sig)
    test("Self-verification passes", ok)
    bad = e.verify_signature("tampered content", "req-001", sig)
    test("Tamper detection works (should be False)", not bad)

    # Test validate_and_bind
    schema = {
        "decision": "answer",
        "severity": 0.1,
        "governance_flags": {"safety": False, "authority": False, "delegation": False, "emotional": False, "ambiguity": False},
        "reason": "test",
        "data": {"response_content": "Test answer about ahimsa.", "request_id": "req-001"},
        "enforced": False
    }
    result = e.validate_and_bind(schema)
    test("validate_and_bind sets enforced=True", result.get("enforced") is True)
    test("validate_and_bind generates signature", result.get("enforcement_signature") is not None)
    test("validate_and_bind signature_verified=True", result.get("signature_verified") is True)
    test("sealed_at timestamp attached", result.get("sealed_at") is not None)

    # Test verify_response (Bridge-level check)
    valid = e.verify_response(result)
    test("Bridge verify_response passes valid sealed response", valid)

    # Tamper result and verify it fails
    tampered = dict(result)
    tampered_data = dict(tampered["data"])
    tampered_data["response_content"] = "HACKED"
    tampered["data"] = tampered_data
    invalid = e.verify_response(tampered)
    test("Bridge verify_response rejects tampered response", not invalid)

except Exception as ex:
    test("Enforcement module importable", False, str(ex))

# ---- TEST 2: Source Verifier Hardened -----------------------------------
print("\n[PHASE 4] Source Verifier Hardened v2")
try:
    from uniguru.verifier.source_verifier import SourceVerifier, VerificationStatus
    sv = SourceVerifier()

    r1 = sv.verify_source("Vachanamrut", "https://www.baps.org/vachanamrut")
    test("Vachanamrut = VERIFIED", r1.status == VerificationStatus.VERIFIED)
    test("Vachanamrut allowed=True", r1.allowed)
    test("Vachanamrut formatted response correct",
         "Based on verified source" in r1.formatted_response)

    r2 = sv.verify_source("Tattvartha Sutra", "https://www.jainfoundation.in/tattvartha-sutra")
    test("Tattvartha Sutra = VERIFIED", r2.status == VerificationStatus.VERIFIED)

    r3 = sv.verify_source("Random blog post", "https://randomblog.com/jain")
    test("Random blog = UNVERIFIED", r3.status == VerificationStatus.UNVERIFIED)
    test("Random blog allowed=False", not r3.allowed)
    test("UNVERIFIED formatted response correct",
         "cannot verify" in r3.formatted_response.lower())

    # Test KB file verification
    kb_path = r"c:\Users\Yass0\OneDrive\Desktop\TASK14\uniguru\knowledge\jain\tattvartha_sutra.md"
    if os.path.exists(kb_path):
        rf = sv.verify_from_kb_file(kb_path)
        test("KB file frontmatter verification works", rf.status == VerificationStatus.VERIFIED)

    # Test legacy static interface
    legacy_result = SourceVerifier.verify({"verified": True, "source_file": "acharanga_sutra.md", "author": "Jacobi"})
    test("Legacy verify() interface works", legacy_result.get("truth_declaration") == "VERIFIED")

except Exception as ex:
    test("SourceVerifier module importable", False, str(ex))

# ---- TEST 3: Multi-KB Retriever -----------------------------------------
print("\n[PHASE 3] Multi-KB Retriever Loading")
try:
    from uniguru.retrieval.retriever import KnowledgeRetriever, KB_PATHS
    test("KB_PATHS configured with 4 paths", len(KB_PATHS) == 4)
    test("Jain KB path configured", "jain" in KB_PATHS)
    test("Swaminarayan KB path configured", "swaminarayan" in KB_PATHS)

    kr = KnowledgeRetriever()
    files = kr.list_indexed_files()
    test("At least 20 files indexed across all KB", len(files) >= 20, f"Found {len(files)}")

    jain_files = [f for f in files if f["kb_source"] == "jain"]
    sw_files = [f for f in files if f["kb_source"] == "swaminarayan"]
    test("Jain KB has 10 files", len(jain_files) >= 10, f"Found {len(jain_files)}")
    test("Swaminarayan KB has 10 files", len(sw_files) >= 10, f"Found {len(sw_files)}")

    # Test retrieval
    result = kr.retrieve("mahavira jain")
    test("Retrieval finds Mahavira content", result is not None, f"Got: {result[2] if result else 'None'}")

    result2 = kr.retrieve("vachanamrut swaminarayan")
    test("Retrieval finds Vachanamrut content", result2 is not None, f"Got: {result2[2] if result2 else 'None'}")

except Exception as ex:
    test("KnowledgeRetriever importable", False, str(ex))

# ---- TEST 4: Web Retriever -----------------------------------------------
print("\n[PHASE 5] Web Retriever Domain Verification")
try:
    from uniguru.retrieval.web_retriever import WebRetriever
    wr = WebRetriever()

    test("stanford.edu allowed", wr.is_allowed_domain("https://stanford.edu/jainism"))
    test("baps.org allowed", wr.is_allowed_domain("https://www.baps.org/vachanamrut"))
    test("sacred-texts.com allowed", wr.is_allowed_domain("https://www.sacred-texts.com/jai/"))
    test("Wikipedia allowed", wr.is_allowed_domain("https://en.wikipedia.org/wiki/Jainism"))
    test("randomblog.com blocked", not wr.is_allowed_domain("https://randomblog.com/jain"))
    test("reddit blocked", not wr.is_allowed_domain("https://reddit.com/r/jainism"))
    test("medium.com blocked", not wr.is_allowed_domain("https://medium.com/@user/jain"))

except Exception as ex:
    test("WebRetriever importable", False, str(ex))

# ---- SUMMARY ------------------------------------------------------------
print()
print("=" * 60)
passed = sum(1 for _, s, _ in results if s == PASS)
failed = sum(1 for _, s, _ in results if s == FAIL)
print(f"TOTAL: {passed} PASSED, {failed} FAILED out of {len(results)} tests")
print("=" * 60)
if failed > 0:
    print("\nFAILED TESTS:")
    for name, status, detail in results:
        if status == FAIL:
            print(f"  - {name}: {detail}")
