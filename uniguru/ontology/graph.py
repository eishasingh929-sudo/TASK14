from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Tuple

from uniguru.ontology.schema import Concept, concept_from_dict


_FROZEN_CONCEPT_ROWS: Tuple[dict, ...] = (
    {
        "concept_id": "8cb2fa29-2d7e-4bd0-af9d-080f3dd0459d",
        "canonical_name": "UniGuru Canonical Root",
        "parent_id": None,
        "truth_level": 4,
        "domain": "core",
        "source_reference": "uniguru/ontology/schema.py",
        "snapshot_version": 1,
        "created_at": "2026-03-04T00:00:00Z",
        "immutable": True,
    },
    {
        "concept_id": "f5e3a359-9ad5-4fcb-b483-598d0917f865",
        "canonical_name": "UniGuru Unresolved Concept",
        "parent_id": "8cb2fa29-2d7e-4bd0-af9d-080f3dd0459d",
        "truth_level": 0,
        "domain": "core",
        "source_reference": "uniguru/ontology/registry.py",
        "snapshot_version": 1,
        "created_at": "2026-03-04T00:00:00Z",
        "immutable": True,
    },
    {
        "concept_id": "adf9434a-c8b9-4f5d-9d4b-8b7e3c286028",
        "canonical_name": "Quantum Knowledge Domain",
        "parent_id": "8cb2fa29-2d7e-4bd0-af9d-080f3dd0459d",
        "truth_level": 3,
        "domain": "quantum",
        "source_reference": "uniguru/Quantum_KB/README.md",
        "snapshot_version": 1,
        "created_at": "2026-03-04T00:00:00Z",
        "immutable": True,
    },
    {
        "concept_id": "ceb14ea2-d665-4ebf-ab6a-8dcaed4bd793",
        "canonical_name": "Jain Knowledge Domain",
        "parent_id": "8cb2fa29-2d7e-4bd0-af9d-080f3dd0459d",
        "truth_level": 3,
        "domain": "jain",
        "source_reference": "uniguru/knowledge/jain",
        "snapshot_version": 1,
        "created_at": "2026-03-04T00:00:00Z",
        "immutable": True,
    },
    {
        "concept_id": "eb517fbb-1585-4f83-8532-42489d0975d5",
        "canonical_name": "Swaminarayan Knowledge Domain",
        "parent_id": "8cb2fa29-2d7e-4bd0-af9d-080f3dd0459d",
        "truth_level": 3,
        "domain": "swaminarayan",
        "source_reference": "uniguru/knowledge/swaminarayan",
        "snapshot_version": 1,
        "created_at": "2026-03-04T00:00:00Z",
        "immutable": True,
    },
    {
        "concept_id": "70dedec2-fc86-41a0-ab4f-30299e4a5fb7",
        "canonical_name": "Gurukul Knowledge Domain",
        "parent_id": "8cb2fa29-2d7e-4bd0-af9d-080f3dd0459d",
        "truth_level": 3,
        "domain": "gurukul",
        "source_reference": "uniguru/knowledge/gurukul",
        "snapshot_version": 1,
        "created_at": "2026-03-04T00:00:00Z",
        "immutable": True,
    },
)


def get_frozen_concepts() -> Tuple[Concept, ...]:
    return tuple(concept_from_dict(row) for row in _FROZEN_CONCEPT_ROWS)


class OntologyGraph:
    def __init__(self, concepts: Iterable[Concept]):
        self.concepts = tuple(concepts)
        self.by_id: Dict[str, Concept] = {concept.concept_id: concept for concept in self.concepts}
        self.children: Dict[Optional[str], List[str]] = {}
        self._index_children()
        self._validate()

    def _index_children(self) -> None:
        for concept in self.concepts:
            self.children.setdefault(concept.parent_id, []).append(concept.concept_id)
        for child_ids in self.children.values():
            child_ids.sort()

    def _validate(self) -> None:
        for concept in self.concepts:
            if not concept.immutable:
                raise ValueError(f"Concept is not immutable: {concept.concept_id}")
            if concept.parent_id is not None and concept.parent_id not in self.by_id:
                raise ValueError(
                    f"Parent concept missing for {concept.concept_id}: {concept.parent_id}"
                )
            if concept.parent_id == concept.concept_id:
                raise ValueError(f"Concept cannot parent itself: {concept.concept_id}")
        self._ensure_acyclic()

    def _ensure_acyclic(self) -> None:
        visited: Dict[str, int] = {}

        def visit(concept_id: str) -> None:
            state = visited.get(concept_id, 0)
            if state == 1:
                raise ValueError(f"Ontology cycle detected at {concept_id}")
            if state == 2:
                return
            visited[concept_id] = 1
            concept = self.by_id[concept_id]
            if concept.parent_id is not None:
                visit(concept.parent_id)
            visited[concept_id] = 2

        for concept_id in self.by_id:
            visit(concept_id)
