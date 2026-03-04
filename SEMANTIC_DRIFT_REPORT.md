# SEMANTIC DRIFT REPORT

## Scope: ONTOLOGY EVOLUTION
**Status**: ACTIVE MONITORING

The UniGuru Semantic Drift Detector ensures that the ontology does not silently mutate or lose structural integrity during updates.

### 1. Drift Detection Rules (Strict)

| Rule Type | Violation Case | Action |
| :--- | :--- | :--- |
| **Parent Change** | `parent_id` mutation | Require `snapshot_version` bump. |
| **Truth Downgrade** | `truth_level` decrease | **REJECTED** (Non-negotiable). |
| **Canonical Name Mutation**| `canonical_name` change | Require `snapshot_version` bump. |

### 2. Violation Logic Implementation

The `drift_detector.py` in `uniguru/ontology/drift_detector.py` implements the following logic:

- **Truth Downgrades**: Any attempt to lower a `truth_level` for a known `concept_id` results in a total rejection of the snapshot update, regardless of the version.
- **Structural Shifts**: If a concept's `parent_id` or `canonical_name` changes, the `drift_detector` checks if `current_snapshot_version > previous_snapshot_version`. If not, a violation is recorded.
- **Silent Mutation Prevention**: Silent updates (changes without version increments) are blocked by the `version_bumped` check.

### 3. Current State Analysis

- **Current Version**: 1
- **Detected Drift**: NONE
- **Action**: All changes for v1 are locked. Any future `uniguru/ontology/graph.py` updates must increment `snapshot_version` to 2.

### 4. Enforcement Verdict

- **Integrity Status**: PASS
- **Silent Mutation Protection**: ENABLED
- **Authority Separation**: Only the UniGuru Registry can authoritatively determine drift status.
