"""Tests for workflow DAG expansion and validation."""

import pytest

from backend.core.workflow_dag import WorkflowStepConfig, expand_steps_to_waves
from backend.core.workflow_registry import WorkflowRegistry
from backend.domain.enums import ModuleRunStatus, WorkflowRunStatus
from backend.services.transcript_service import TranscriptService
from tests.test_workflow_engine import _build_engine, _ingest_golden, _module_llm_response
from unittest.mock import MagicMock


def test_expand_steps_respects_depends_on() -> None:
    steps = [
        WorkflowStepConfig(
            id="a",
            parallel=["relationship_conversation_analysis", "nvc_analysis"],
        ),
        WorkflowStepConfig(
            id="b",
            depends_on=["a"],
            module="meta_synthesis",
        ),
    ]
    waves = expand_steps_to_waves(steps)
    assert waves[0].module_ids == [
        "relationship_conversation_analysis",
        "nvc_analysis",
    ]
    assert waves[-1].module_ids == ["meta_synthesis"]
    assert waves[-1].is_synthesis is True


def test_expand_steps_rejects_cycle() -> None:
    steps = [
        WorkflowStepConfig(id="a", depends_on=["b"], parallel=["nvc_analysis"]),
        WorkflowStepConfig(id="b", depends_on=["a"], parallel=["systems_analysis"]),
    ]
    with pytest.raises(ValueError, match="cycle"):
        expand_steps_to_waves(steps)


def test_full_mvp_loads_with_steps() -> None:
    workflow = WorkflowRegistry().get("full_mvp")
    assert workflow.waves is not None
    assert workflow.module_sequence[-1] == "meta_synthesis"
    assert "relationship_conversation_analysis" in workflow.module_sequence


def test_engine_runs_dag_full_mvp() -> None:
    mock_llm = MagicMock()
    mock_llm.chat.side_effect = [
        _module_llm_response("relationship_conversation_analysis"),
        _module_llm_response("nvc_analysis"),
        _module_llm_response("systems_analysis"),
        _module_llm_response("bias_epistemic_quality"),
        _module_llm_response("meta_synthesis"),
    ]
    engine = _build_engine(mock_llm)
    bundle = _ingest_golden(TranscriptService())
    TranscriptService().mark_ready(bundle.transcript.id)

    workflow_run = engine.run(
        workflow_id="full_mvp",
        transcript_id=bundle.transcript.id,
        model="test-model",
    )
    _, module_runs = engine.get_with_module_runs(workflow_run.id)
    assert workflow_run.status == WorkflowRunStatus.COMPLETED.value
    assert len(module_runs) == 5
    assert all(run.status == ModuleRunStatus.COMPLETED.value for run in module_runs)
    assert module_runs[-1].module_id == "meta_synthesis"
