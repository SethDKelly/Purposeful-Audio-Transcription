"""Resolve safety_mode and record SafetyEvents (v2.0)."""

from __future__ import annotations

from backend.db.base import get_session
from backend.repositories.safety_event_repository import safety_event_repository
from backend.services.safety_risk_scanner import SafetyScanResult, safety_risk_scanner
from backend.services.transcript_service import TranscriptService, transcript_service


class WorkflowSafetyService:
    def __init__(self, transcripts: TranscriptService | None = None) -> None:
        self._transcripts = transcripts or transcript_service

    def scan_transcript(
        self,
        transcript_id: str,
        *,
        record_event: bool = True,
    ) -> SafetyScanResult:
        bundle = self._transcripts.get(transcript_id)
        scan = safety_risk_scanner.scan(bundle.transcript.raw_text)
        if record_event and scan.risk_level != "none":
            with get_session() as session:
                safety_event_repository.create(
                    session,
                    event_type="scan",
                    risk_level=scan.risk_level,
                    transcript_id=transcript_id,
                    categories=scan.matched_categories,
                    details={"safety_mode_recommended": scan.safety_mode_recommended},
                )
        return scan

    def resolve_safety_mode(
        self,
        transcript_id: str,
        *,
        request_flag: bool | None = None,
        workflow_run_id: str | None = None,
    ) -> bool:
        if request_flag is True:
            enabled = True
            scan = self.scan_transcript(transcript_id, record_event=False)
        else:
            scan = self.scan_transcript(transcript_id, record_event=True)
            enabled = scan.safety_mode_recommended
        if enabled:
            with get_session() as session:
                safety_event_repository.create(
                    session,
                    event_type="safety_mode_enabled",
                    risk_level=scan.risk_level if scan.risk_level != "none" else "elevated",
                    transcript_id=transcript_id,
                    workflow_run_id=workflow_run_id,
                    categories=scan.matched_categories,
                    details={"request_flag": request_flag},
                )
        return enabled

    def list_events(
        self,
        *,
        transcript_id: str | None = None,
        workflow_run_id: str | None = None,
    ) -> list[dict]:
        with get_session() as session:
            if workflow_run_id:
                return safety_event_repository.list_for_run(session, workflow_run_id)
            if transcript_id:
                return safety_event_repository.list_for_transcript(session, transcript_id)
            return []


workflow_safety_service = WorkflowSafetyService()
