"""Resolve safety_mode for workflow runs (v1.0 P5)."""

from __future__ import annotations

from backend.services.safety_risk_scanner import SafetyScanResult, safety_risk_scanner
from backend.services.transcript_service import TranscriptService, transcript_service


class WorkflowSafetyService:
    def __init__(self, transcripts: TranscriptService | None = None) -> None:
        self._transcripts = transcripts or transcript_service

    def scan_transcript(self, transcript_id: str) -> SafetyScanResult:
        bundle = self._transcripts.get(transcript_id)
        return safety_risk_scanner.scan(bundle.transcript.raw_text)

    def resolve_safety_mode(
        self,
        transcript_id: str,
        *,
        request_flag: bool | None = None,
    ) -> bool:
        if request_flag is True:
            return True
        scan = self.scan_transcript(transcript_id)
        return scan.safety_mode_recommended


workflow_safety_service = WorkflowSafetyService()
