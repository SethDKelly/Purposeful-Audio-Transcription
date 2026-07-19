"""Offline evaluation runs persisted for release gates (v2.0)."""

from __future__ import annotations

from backend.db.base import get_session
from backend.evaluation.harness import EvalGateConfig, evaluate_module_output
from backend.repositories.evaluation_run_repository import evaluation_run_repository
from tests.helpers.golden_transcripts import load_golden_fixture_by_id


class EvaluationRunService:
    def list_recent(self, *, limit: int = 50) -> list[dict]:
        with get_session() as session:
            return evaluation_run_repository.list_recent(session, limit=limit)

    def get(self, run_id: str) -> dict | None:
        with get_session() as session:
            return evaluation_run_repository.get(session, run_id)

    def record(
        self,
        *,
        kind: str,
        gate_passed: bool,
        fixture_id: str | None = None,
        module_id: str | None = None,
        summary: dict | None = None,
    ) -> dict:
        with get_session() as session:
            return evaluation_run_repository.create(
                session,
                kind=kind,
                gate_passed=gate_passed,
                fixture_id=fixture_id,
                module_id=module_id,
                summary=summary,
            )

    def run_offline_fixture(
        self,
        *,
        fixture_id: str,
        module_id: str,
        module_output: dict,
    ) -> dict:
        fixture = load_golden_fixture_by_id(fixture_id)
        result = evaluate_module_output(
            fixture=fixture,
            module_id=module_id,
            module_output=module_output,
            gates=EvalGateConfig(),
        )
        summary = result.to_dict()
        return self.record(
            kind="golden_offline",
            gate_passed=result.gate_passed,
            fixture_id=fixture_id,
            module_id=module_id,
            summary=summary,
        )


evaluation_run_service = EvaluationRunService()
