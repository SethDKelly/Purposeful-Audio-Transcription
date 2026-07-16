"""Longitudinal synthesis handoff (v0.9 P4)."""

from backend.core.exceptions import CaseValidationError
from backend.db.base import get_session
from backend.domain.enums import Confidence, FindingType, ModuleRunStatus, SourceType
from backend.domain.finding import Finding
from backend.repositories.finding_repository import FindingRepository
from backend.repositories.module_run_repository import ModuleRunRepository
from backend.repositories.workflow_run_repository import WorkflowRunRepository
from backend.services.case_service import case_service
from backend.services.longitudinal_synthesis_service import LongitudinalSynthesisService
from backend.services.transcript_service import TranscriptService
import pytest


def test_longitudinal_handoff_requires_two_completed_sessions() -> None:
    case = case_service.create(title="Synth case")
    t1 = TranscriptService().ingest(
        "Person A: Hi.\nPerson B: Hello.",
        source_type=SourceType.PASTE,
        title="S1",
    )
    case_service.assign_transcript(t1.transcript.id, case_id=case.id, session_label="S1")
    service = LongitudinalSynthesisService()
    with pytest.raises(CaseValidationError):
        service.build_handoff(case.id)

    t2 = TranscriptService().ingest(
        "Person A: Later.\nPerson B: Ok.",
        source_type=SourceType.PASTE,
        title="S2",
    )
    case_service.assign_transcript(t2.transcript.id, case_id=case.id, session_label="S2")
    with get_session() as session:
        for transcript in (t1, t2):
            wr = WorkflowRunRepository().create(
                session,
                workflow_id="quick_review",
                transcript_id=transcript.transcript.id,
                model_used="test",
            )
            wr.status = "completed"
            WorkflowRunRepository().save(session, wr)
            run = ModuleRunRepository().create(
                session,
                module_id="nvc_analysis",
                transcript_id=transcript.transcript.id,
                workflow_run_id=wr.id,
            )
            run.status = ModuleRunStatus.COMPLETED.value
            ModuleRunRepository().save(session, run)
            FindingRepository().replace_for_module_run(
                session,
                run,
                [
                    Finding(
                        id="F001",
                        module_run_id=run.id,
                        type=FindingType.OBSERVATION,
                        title="Theme",
                        summary="Theme summary",
                        confidence=Confidence.MODERATE,
                        evidence_quote_ids=["Q001"],
                    )
                ],
            )

    handoff = service.build_handoff(case.id)
    assert "longitudinal_inventory" in handoff
    assert len(handoff["longitudinal_inventory"]["sessions"]) == 2
