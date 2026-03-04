# ONTOLOGY SCHEMA FREEZE REPORT

## Status: IMMUTABLE

This document serves as the canonical definition for the **UniGuru Concept Schema**. This schema is now frozen. No dynamic fields or structural mutations are permitted without a formal version bump and drift analysis.

### 1. Concept Fields (Required)

| Field | Type | Description |
| :--- | :--- | :--- |
| `concept_id` | UUID | Immutable unique identifier. |
| `canonical_name` | String | Standardized name for the concept. |
| `parent_id` | UUID \| None | Link to parent concept for structural hierarchy. |
| `truth_level` | Integer | Assigned truth depth (0–4). |
| `domain` | Enum | Classification: `quantum`, `jain`, `swaminarayan`, `gurukul`, `core`. |
| `source_reference`| String | Direct URI or file path to knowledge origin. |
| `snapshot_version`| Integer | The snapshot version in which this concept was defined. |
| `created_at` | Timestamp | ISO 8601 formatting (UTC). |
| `immutable` | Boolean | Hard flag indicating structural stability. |

### 2. Strict Truth Levels

| Level | Name | Definition |
| :--- | :--- | :--- |
| **0** | Unknown | Unprocessed or conflicting data. |
| **1** | Partially Verified | Source exists but cross-referencing is pending. |
| **2** | Verified Secondary | Confirmed by secondary sources/commentaries. |
| **3** | Canonical Verified | Matches primary canonical source (Shastras/Text). |
| **4** | Foundational Immutable | Core ontological axioms (Root Nodes). |

### 3. Implementation Guardrails

- **Acyclic Enforcement**: The `OntologyGraph` enforces a Directed Acyclic Graph (DAG) structure; no concept can parent itself or form cycles.
- **Frozen Dataclass**: The `Concept` implementation in `uniguru/ontology/schema.py` uses `frozen=True` to prevent runtime mutation.
- **Schema Validation**: `validate_concept_dict` will reject any payload containing extra or missing fields.

### 4. Integrity Seal

The schema logic is contained in `uniguru/ontology/schema.py` and is currently protected by deterministic hashing in the snapshot system.
