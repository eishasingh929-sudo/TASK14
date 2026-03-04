# GURUKUL REGISTRY ALIGNMENT REPORT

## Registry Contract: `UniGuru <=> Gurukul`
**Status**: ALIGNED & ENFORCED

This document defines the alignment between UniGuru (The Canonical Ontology Backbone) and Gurukul (The Consumer of Ontology).

### 1. Registry Contract Schema

Gurukul must consume the following payload for every ontological reference:

```json
{
  "concept_id": "UUID",
  "canonical_name": "string",
  "domain": "enum",
  "truth_level": "integer 0-4",
  "snapshot_version": "int",
  "snapshot_hash": "sha256"
}
```

### 2. RuleEngine Modification (Authority Separation)

Every answer emitted by the UniGuru `RuleEngine` now includes a mandatory `ontology_reference`. This reference is constructed by the `OntologyRegistry` and bound to the decision output.

#### Output Structure

```json
{
  "decision": "answer",
  "ontology_reference": {
    "concept_id": "adf9434a-c8b9-4f5d-9d4b-8b7e3c286028",
    "snapshot_version": 1,
    "snapshot_hash": "7b01e6aca6b9552affc74df475aa3aa252dd23bc6f36020158ccae4589570586"
  }
}
```

### 3. Gurukul Implementation (Adapter Alignment)

The `GurukulIntegrationAdapter` in `uniguru/integrations/gurukul/adapter.py` is the primary consumer. 

1. **Strict Consumption**: Gurukul consumes the `ontology_reference` and uses it to look up the full `registry_contract` from the `OntologyRegistry`.
2. **Authority Separation**:
   - Gurukul **cannot** override `truth_level`.
   - Gurukul **cannot** mutate `canonical_name`.
   - Gurukul **cannot** redefine the ontology `parent`.
3. **Sealing**: The `snapshot_hash` ensures that Gurukul is consuming the exact same version of the ontology that UniGuru is providing.

### 4. Alignment Verdict

- **Contract Integrity**: SECURE
- **Authority Separation Proof**: The `OntologyRegistry` acts as the single source of truth. Gurukul has no write access to the ontology state and acts solely as a consumer of verified concepts.
- **Fail-Closed**: Any mismatch in `snapshot_version` or `snapshot_hash` during registry lookup causes an immediate failure.
