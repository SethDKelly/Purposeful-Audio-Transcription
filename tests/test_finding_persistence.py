"""Normalized findings persistence (v0.8 P1)."""

from sqlalchemy import select

from backend.db.base import get_session
from backend.db.models import FindingEvidenceQuoteRow, FindingRow
from backend.domain.enums import Confidence, FindingType, ModuleRunStatus, SourceType
from backend.domain.finding import Finding, ModuleRun
from backend.repositories.finding_repository import FindingRepository
from backend.repositories.module_run_repository import ModuleRunRepository
from backend.schemas.module_output_v1 import ModuleRunOutput
from backend.services.exploration_service import ExplorationService
from backend.services.module_runner import ModuleRunner
from backend.services.transcript_service import TranscriptService


def _sample_finding(*, finding_id: str = "F001") -> Finding:
    return Finding(
        id=finding_id,
        module_run_id="ignored",
        type=FindingType.OBSERVATION,
        title="Defensive pattern",
        summary="Speaker A deflects when accountability is raised.",
        confidence=Confidence.MODERATE,
        evidence_quote_ids=["Q001", "Q002"],
        alternative_explanations=["Could be anxiety rather than avoidance."],
        limitations=["Single conversation sample."],
        construct_ids=["defensiveness"],
    )


def _create_run(
    *,
    module_id: str,
    workflow_run_id: str,
) -> ModuleRun:
    bundle = TranscriptService().ingest(
        "Person A: Hello.\nPerson B: Hi.",
        source_type=SourceType.PASTE,
        title="finding-persist",
    )
    with get_session() as session:
        run = ModuleRunRepository().create(
            session,
            module_id=module_id,
            transcript_id=bundle.transcript.id,
            workflow_run_id=workflow_run_id,
        )
        run.status = ModuleRunStatus.COMPLETED.value
        ModuleRunRepository().save(session, run)
        return run


def test_finding_repository_replace_and_list() -> None:
    findings = FindingRepository()
    run = _create_run(module_id="nvc_analysis", workflow_run_id="wf-1")

    with get_session() as session:
        ids = findings.replace_for_module_run(
            session,
            run,
            [_sample_finding()],
            module_version="1.0.0",
        )
        assert len(ids) == 1

        listed = findings.list_by_workflow_run_id(session, "wf-1")
        assert len(listed) == 1
        item = listed[0]
        assert item["finding_key"] == "nvc_analysis:F001"
        assert item["title"] == "Defensive pattern"
        assert item["evidence_quote_ids"] == ["Q001", "Q002"]
        assert item["alternative_explanations"] == [
            "Could be anxiety rather than avoidance."
        ]
        assert item["limitations"] == ["Single conversation sample."]

        quote_count = len(
            session.scalars(
                select(FindingEvidenceQuoteRow).where(
                    FindingEvidenceQuoteRow.finding_id == ids[0]
                )
            ).all()
        )
        assert quote_count == 2

        findings.replace_for_module_run(session, run, [_sample_finding(finding_id="F002")])
        listed = findings.list_by_workflow_run_id(session, "wf-1")
        assert len(listed) == 1
        assert listed[0]["id"] == "F002"


def test_module_runner_persists_normalized_findings() -> None:
    run = _create_run(module_id="gottman_analysis", workflow_run_id="wf-persist")
    run.status = ModuleRunStatus.RUNNING.value

    output = ModuleRunOutput(
        module_id="gottman_analysis",
        module_version="1.0.0",
        executive_summary="Summary",
        findings=[_sample_finding()],
        constructs=[],
        relationships=[],
    )
    completed = ModuleRunner()._complete_run(run, output, safety_flags=[])
    assert completed.status == ModuleRunStatus.COMPLETED.value

    with get_session() as session:
        rows = session.scalars(
            select(FindingRow).where(FindingRow.workflow_run_id == "wf-persist")
        ).all()
        assert len(rows) == 1
        assert rows[0].source_id == "F001"
        assert rows[0].module_id == "gottman_analysis"


def test_exploration_prefers_normalized_findings() -> None:
    findings = FindingRepository()
    run = _create_run(module_id="systems_analysis", workflow_run_id="wf-explore")
    with get_session() as session:
        findings.replace_for_module_run(
            session, run, [_sample_finding(finding_id="F010")]
        )

    listed = ExplorationService().list_findings("wf-explore")
    assert len(listed) == 1
    assert listed[0]["finding_key"] == "systems_analysis:F010"
    assert listed[0]["title"] == "Defensive pattern"
