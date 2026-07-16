"""Ontology vocabulary loading and cross-reference validation."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from backend.core.module_registry import ModuleRegistry
from backend.core.ontology_registry import OntologyRegistry
from backend.domain.enums import RelationshipType
from config.settings import settings

GOLDEN_ROOT = Path(__file__).parent / "fixtures" / "golden_transcripts"


def test_ontology_registry_loads_core_constructs() -> None:
    registry = OntologyRegistry()
    assert "observation" in registry.construct_ids
    assert "repair_attempt" in registry.construct_ids
    assert "interaction_cycle" in registry.construct_ids
    assert len(registry.construct_ids) >= 26


def test_ontology_registry_loads_relationships() -> None:
    registry = OntologyRegistry()
    assert "supports" in registry.relationship_ids
    assert "evidence_for" in registry.relationship_ids
    assert len(registry.relationship_ids) >= 15


def test_construct_aliases_resolve() -> None:
    registry = OntologyRegistry()
    assert registry.resolve_construct("feeling") == "emotion"
    assert registry.resolve_construct("communication_pattern") == "interaction_cycle"
    assert registry.resolve_construct("leverage_point") == "intervention"


def test_relationship_aliases_resolve() -> None:
    registry = OntologyRegistry()
    assert registry.resolve_relationship("reinforces") == "supports"
    assert registry.resolve_relationship("causes") == "contributes_to"


def test_relationship_type_enum_matches_ontology() -> None:
    registry = OntologyRegistry()
    enum_values = {item.value for item in RelationshipType}
    assert enum_values <= registry.relationship_ids


def test_module_registry_validates_expected_constructs() -> None:
    registry = ModuleRegistry()
    module = registry.get("nvc_analysis")
    assert module.config.expected_constructs == ["observation", "emotion", "need", "request"]


def test_module_registry_rejects_unknown_expected_constructs(tmp_path: Path) -> None:
    modules_dir = tmp_path / "modules"
    prompts_dir = tmp_path / "prompts"
    modules_dir.mkdir()
    prompts_dir.mkdir()
    (prompts_dir / "prompt.md").write_text("Test prompt", encoding="utf-8")
    (modules_dir / "bad.yaml").write_text(
        """
id: bad_module
name: Bad
version: "1.0.0"
primary_lens: Test
analytical_level: observable
unit_of_analysis: interaction
primary_question: Test?
expected_constructs:
  - not_a_real_construct
prompt_file: prompt.md
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unknown expected_constructs"):
        ModuleRegistry(modules_dir=modules_dir, prompts_dir=prompts_dir)


def test_golden_fixture_construct_types_exist_in_ontology() -> None:
    if not GOLDEN_ROOT.is_dir():
        pytest.skip("golden transcript fixtures not present")

    registry = OntologyRegistry()
    for fixture_dir in GOLDEN_ROOT.iterdir():
        if not fixture_dir.is_dir():
            continue
        assertions_path = fixture_dir / "expected_assertions.yaml"
        if not assertions_path.is_file():
            continue
        assertions = yaml.safe_load(assertions_path.read_text(encoding="utf-8")) or {}
        include_any = (assertions.get("expected_construct_types") or {}).get("include_any") or []
        for construct_type in include_any:
            assert registry.resolve_construct(construct_type), (
                f"{fixture_dir.name}: unknown construct type {construct_type!r}"
            )

        for signal in assertions.get("required_signals") or []:
            signal_type = signal.get("type")
            if signal_type:
                assert registry.resolve_construct(signal_type), (
                    f"{fixture_dir.name}: unknown signal type {signal_type!r}"
                )


def test_all_modules_load_with_ontology_validation() -> None:
    registry = ModuleRegistry(
        modules_dir=settings.modules_dir,
        prompts_dir=settings.prompts_dir,
    )
    assert len(registry.list_modules(enabled_only=False)) == 14
