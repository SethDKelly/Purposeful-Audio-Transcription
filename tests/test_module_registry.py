from pathlib import Path

import pytest

from backend.core.exceptions import ModuleNotFoundError
from backend.core.module_registry import ModuleRegistry


def test_module_registry_loads_mvp_modules() -> None:
    registry = ModuleRegistry()
    modules = registry.list_modules()
    assert len(modules) == 5
    ids = {module.config.id for module in modules}
    assert ids == {
        "relationship_conversation_analysis",
        "nvc_analysis",
        "systems_analysis",
        "bias_epistemic_quality",
        "meta_synthesis",
    }


def test_module_registry_get_module() -> None:
    registry = ModuleRegistry()
    module = registry.get("nvc_analysis")
    assert module.config.name == "NVC Analysis"
    assert module.config.version == "1.0.0"
    assert "Nonviolent Communication" in module.module_prompt


def test_module_registry_unknown_module() -> None:
    registry = ModuleRegistry()
    with pytest.raises(ModuleNotFoundError):
        registry.get("missing_module")


def test_module_registry_validates_yaml(tmp_path: Path) -> None:
    modules_dir = tmp_path / "modules"
    modules_dir.mkdir()
    (modules_dir / "bad.yaml").write_text("id: broken\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid module config"):
        ModuleRegistry(modules_dir=modules_dir, prompts_dir=tmp_path)
