"""Load and validate canonical ontology vocabulary from config/ontology/."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from config.settings import settings


class OntologyTermModel(BaseModel):
    id: str
    label: str
    description: str
    category: str = "core"
    aliases: list[str] = Field(default_factory=list)
    confidence_ceiling: str | None = None


class ConstructsFileModel(BaseModel):
    version: int
    description: str = ""
    constructs: list[OntologyTermModel]


class RelationshipsFileModel(BaseModel):
    version: int
    description: str = ""
    relationships: list[OntologyTermModel]


@dataclass(frozen=True)
class OntologyTerm:
    id: str
    label: str
    description: str
    category: str
    aliases: tuple[str, ...]
    confidence_ceiling: str | None


class OntologyRegistry:
    """Canonical construct and relationship vocabulary for RRE."""

    def __init__(self, ontology_dir: Path | None = None) -> None:
        self._ontology_dir = ontology_dir or settings.ontology_dir
        self._constructs, self._construct_aliases = self._load_constructs()
        self._relationships, self._relationship_aliases = self._load_relationships()

    def _load_terms_file(
        self,
        filename: str,
        key: str,
    ) -> tuple[dict[str, OntologyTerm], dict[str, str]]:
        path = self._ontology_dir / filename
        if not path.is_file():
            raise FileNotFoundError(f"Missing ontology file: {path}")

        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if key == "constructs":
            parsed = ConstructsFileModel.model_validate(raw)
            items = parsed.constructs
        else:
            parsed = RelationshipsFileModel.model_validate(raw)
            items = parsed.relationships

        by_id: dict[str, OntologyTerm] = {}
        alias_map: dict[str, str] = {}
        for item in items:
            term = OntologyTerm(
                id=item.id,
                label=item.label,
                description=item.description,
                category=item.category,
                aliases=tuple(item.aliases),
                confidence_ceiling=item.confidence_ceiling,
            )
            if term.id in by_id:
                raise ValueError(f"Duplicate ontology {key} id: {term.id}")
            by_id[term.id] = term
            for alias in term.aliases:
                normalized = _normalize_key(alias)
                if normalized in alias_map and alias_map[normalized] != term.id:
                    raise ValueError(
                        f"Conflicting alias {alias!r} for {key}: "
                        f"{alias_map[normalized]} vs {term.id}"
                    )
                alias_map[normalized] = term.id
        return by_id, alias_map

    def _load_constructs(self) -> tuple[dict[str, OntologyTerm], dict[str, str]]:
        return self._load_terms_file("constructs.yaml", "constructs")

    def _load_relationships(self) -> tuple[dict[str, OntologyTerm], dict[str, str]]:
        return self._load_terms_file("relationships.yaml", "relationships")

    @property
    def construct_ids(self) -> frozenset[str]:
        return frozenset(self._constructs)

    @property
    def relationship_ids(self) -> frozenset[str]:
        return frozenset(self._relationships)

    def get_construct(self, construct_id: str) -> OntologyTerm | None:
        return self._constructs.get(construct_id)

    def get_relationship(self, relationship_id: str) -> OntologyTerm | None:
        return self._relationships.get(relationship_id)

    def resolve_construct(self, value: str) -> str | None:
        key = _normalize_key(value)
        if key in self._constructs:
            return key
        return self._construct_aliases.get(key)

    def resolve_relationship(self, value: str) -> str | None:
        key = _normalize_key(value)
        if key in self._relationships:
            return key
        return self._relationship_aliases.get(key)

    def unknown_constructs(self, values: list[str]) -> list[str]:
        unknown: list[str] = []
        for value in values:
            if not value or self.resolve_construct(value):
                continue
            unknown.append(value)
        return unknown

    def unknown_relationships(self, values: list[str]) -> list[str]:
        unknown: list[str] = []
        for value in values:
            if not value or self.resolve_relationship(value):
                continue
            unknown.append(value)
        return unknown

    def list_constructs(self) -> list[OntologyTerm]:
        return sorted(self._constructs.values(), key=lambda term: term.id)

    def list_relationships(self) -> list[OntologyTerm]:
        return sorted(self._relationships.values(), key=lambda term: term.id)


def _normalize_key(value: str) -> str:
    return str(value).strip().lower().replace(" ", "_").replace("-", "_")


ontology_registry = OntologyRegistry()
