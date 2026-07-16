from pathlib import Path

import pytest

from backend.core.exceptions import WorkflowNotFoundError
from backend.core.workflow_registry import WorkflowRegistry


def test_workflow_registry_loads_all_workflows() -> None:
    registry = WorkflowRegistry()
    workflows = registry.list_workflows()
    assert len(workflows) == 7
    ids = {workflow.config.id for workflow in workflows}
    assert ids == {
        "quick_review",
        "full_mvp",
        "conflict_coaching",
        "mediation_brief",
        "clinical_exploration",
        "full_multidisciplinary",
        "research_oriented",
    }


def test_workflow_registry_get_quick_review() -> None:
    registry = WorkflowRegistry()
    workflow = registry.get("quick_review")
    assert workflow.module_sequence == [
        "relationship_conversation_analysis",
        "nvc_analysis",
        "bias_epistemic_quality",
    ]
    assert workflow.config.meta_synthesis is False
    assert workflow.config.output_tone == "practical"


def test_workflow_registry_get_full_mvp() -> None:
    registry = WorkflowRegistry()
    workflow = registry.get("full_mvp")
    assert workflow.module_sequence[-1] == "meta_synthesis"


def test_workflow_registry_get_clinical_exploration() -> None:
    registry = WorkflowRegistry()
    workflow = registry.get("clinical_exploration")
    assert workflow.config.meta_synthesis is True
    assert workflow.config.output_tone == "clinical_exploratory"
    assert "exploratory_psychological_formulation" in workflow.module_sequence


def test_workflow_registry_unknown() -> None:
    registry = WorkflowRegistry()
    with pytest.raises(WorkflowNotFoundError):
        registry.get("missing_workflow")


def test_workflow_registry_validates_yaml(tmp_path: Path) -> None:
    workflows_dir = tmp_path / "workflows"
    workflows_dir.mkdir()
    (workflows_dir / "bad.yaml").write_text("id: broken\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid workflow config"):
        WorkflowRegistry(workflows_dir=workflows_dir)
