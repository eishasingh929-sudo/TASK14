# TRUTH_VERIFIER_INTEGRATION

Date: 2026-02-25

## Objective
Enforce truth verification before deterministic KB answer release.

## Integration Done
- `RetrievalRule` now calls `SourceVerifier.verify_retrieval_trace(...)`.
- Verification metadata is attached in response payload under `data.verification`.
- If verification fails, response becomes:
  - `I cannot verify this information with current knowledge.`

## Verified Example
Query:
```text
What is a qubit?
```
Verification payload excerpt:
```json
{
  "truth_declaration":"VERIFIED",
  "verification_level":"HIGH",
  "source_file":"qubit.md"
}
```

## Rejected Example
Verifier check with missing source:
```json
{
  "verified": false,
  "source_file": null,
  "truth_declaration": "UNVERIFIABLE"
}
```
Enforced response policy:
```text
I cannot verify this information with current knowledge.
```
