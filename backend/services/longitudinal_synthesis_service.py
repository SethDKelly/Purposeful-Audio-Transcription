"""Case-level longitudinal synthesis (v0.9 P4)."""

from __future__ import annotations

from typing import Any

from backend.core.exceptions import CaseValidationError, ExplorationError
from backend.db.base import get_session
from backend.domain.finding import ModuleRun
from backend.repositories.case_repository import CaseRepository
from backend.services.exploration_service import ExplorationService, exploration_service
from backend.services.module_runner import ModuleRunner, module_runner
from backend.services.structured_graph_service import (
    StructuredGraphService,
    structured_graph_service,
)


class LongitudinalSynthesisService:
    def __init__(
        self,
        cases: CaseRepository | None = None,
        exploration: ExplorationService | None = None,
        structured: StructuredGraphService | None = None,
        runner: ModuleRunner | None = None,
    ) -> None:
        self._cases = cases or CaseRepository()
        self._exploration = exploration or exploration_service
        self._structured = structured or structured_graph_service
        self._runner = runner or module_runner

    def build_handoff(self, case_id: str) -> dict[str, Any]:
        with get_session() as session:
            detail = self._cases.get_detail(session, case_id)
        if len(detail.transcripts) < 2:
            raise CaseValidationError(
                "Longitudinal synthesis requires at least two transcripts in the case"
            )

        sessions: list[dict] = []
        for transcript in detail.transcripts:
            runs = self._exploration.list_transcript_workflow_runs(transcript.id)
            if not runs:
                continue
            latest = runs[-1]
            inventory = self._structured.synthesis_handoff(latest["id"])
            sessions.append(
                {
                    "transcript_id": transcript.id,
                    "session_label": transcript.session_label or transcript.title,
                    "session_date": transcript.session_date.isoformat()
                    if transcript.session_date
                    else None,
                    "workflow_run_id": latest["id"],
                    "inventory": inventory,
                }
            )
        if len(sessions) < 2:
            raise CaseValidationError(
                "Longitudinal synthesis needs completed workflow runs on at least two transcripts"
            )

        try:
            comparison = self._exploration.compare_case_transcripts(case_id)
        except ExplorationError:
            comparison = None

        return {
            "longitudinal_inventory": {
                "case_id": case_id,
                "case_title": detail.case.title,
                "sessions": sessions,
                "comparison": comparison,
                "guidance": (
                    "Primary input is longitudinal_inventory. Cite session labels and "
                    "finding/construct IDs. Contrast earliest vs latest sessions."
                ),
            }
        }

    def run(
        self,
        case_id: str,
        *,
        model: str | None = None,
    ) -> ModuleRun:
        handoff = self.build_handoff(case_id)
        sessions = handoff["longitudinal_inventory"]["sessions"]
        latest_transcript_id = sessions[-1]["transcript_id"]
        # Provide compact session inventories as prior_outputs for the synthesizer.
        prior_outputs = [
            {
                "session_label": session["session_label"],
                "session_date": session["session_date"],
                "workflow_run_id": session["workflow_run_id"],
                "structured_inventory": session["inventory"],
            }
            for session in sessions
        ]
        # Embed longitudinal envelope as first prior payload for prompt context.
        prior_outputs = [handoff["longitudinal_inventory"], *prior_outputs]
        return self._runner.run_synthesis(
            module_id="longitudinal_synthesis",
            transcript_id=latest_transcript_id,
            prior_outputs=prior_outputs,
            model=model,
            workflow_run_id=None,
        )


longitudinal_synthesis_service = LongitudinalSynthesisService()
