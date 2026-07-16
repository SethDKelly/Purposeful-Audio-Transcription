"""Build and validate cross-module synthesis reports."""

import logging

from backend.core.exceptions import SynthesisError, SynthesisNotFoundError
from backend.db.base import get_session
from backend.domain.enums import WorkflowRunStatus
from backend.domain.finding import ModuleRun
from backend.domain.synthesis import SynthesisReport
from backend.repositories.synthesis_report_repository import (
    SynthesisReportRepository,
    new_synthesis_report_id,
    utc_now,
)
from backend.services.safety_validator import SafetyValidator, safety_validator
from backend.services.synthesis_output_validator import (
    SynthesisOutputValidator,
    synthesis_output_validator,
)
from backend.services.synthesis_parser import SynthesisParser, synthesis_parser
from backend.services.synthesis_preprocessor import (
    META_SYNTHESIS_MODULE_ID,
    SynthesisPreprocessor,
    synthesis_preprocessor,
)
from backend.services.workflow_engine import WorkflowEngine, workflow_engine

logger = logging.getLogger(__name__)


class SynthesisEngine:
    def __init__(
        self,
        workflows: WorkflowEngine | None = None,
        preprocessor: SynthesisPreprocessor | None = None,
        parser: SynthesisParser | None = None,
        validator: SynthesisOutputValidator | None = None,
        safety: SafetyValidator | None = None,
        repository: SynthesisReportRepository | None = None,
    ) -> None:
        self._workflows = workflows or workflow_engine
        self._preprocessor = preprocessor or synthesis_preprocessor
        self._parser = parser or synthesis_parser
        self._validator = validator or synthesis_output_validator
        self._safety = safety or safety_validator
        self._repository = repository or SynthesisReportRepository()

    def get_report(self, workflow_run_id: str) -> SynthesisReport:
        with get_session() as session:
            cached = self._repository.get_by_workflow_run_id(session, workflow_run_id)
            if cached is not None:
                return cached

        workflow_run, module_runs = self._workflows.get_with_module_runs(workflow_run_id)
        if workflow_run.status != WorkflowRunStatus.COMPLETED.value:
            raise SynthesisNotFoundError(
                f"Synthesis is unavailable while workflow run is {workflow_run.status}"
            )

        completed_runs = [
            run for run in module_runs if run.status == "completed" and run.parsed_output
        ]
        if not completed_runs:
            raise SynthesisNotFoundError(
                f"No completed module outputs for workflow run {workflow_run_id}"
            )

        report = self._build_report(workflow_run_id, completed_runs)
        report.created_at = utc_now()

        safety_result = self._safety.validate_synthesis(report)
        if not safety_result.is_safe:
            raise SynthesisError(
                "Synthesis report failed safety validation: "
                + "; ".join(safety_result.violations)
            )
        report.safety_flags = safety_result.flags

        validation = self._validator.validate(
            report,
            self._preprocessor.process(
                completed_runs, workflow_run_id=workflow_run_id
            ).allowed_quote_ids,
        )
        if not validation.is_valid:
            raise SynthesisError(
                "Synthesis report failed validation: " + "; ".join(validation.errors)
            )

        with get_session() as session:
            self._repository.save(session, report)

        logger.info("Built synthesis report %s for workflow run %s", report.id, workflow_run_id)
        return report

    def _build_report(
        self,
        workflow_run_id: str,
        module_runs: list[ModuleRun],
    ) -> SynthesisReport:
        preprocessed = self._preprocessor.process(
            module_runs, workflow_run_id=workflow_run_id
        )
        synthesis_id = new_synthesis_report_id()
        meta_run = _find_meta_synthesis_run(module_runs)

        if meta_run and meta_run.parsed_output:
            return self._parser.parse_meta_module_output(
                meta_run.parsed_output,
                workflow_run_id=workflow_run_id,
                synthesis_id=synthesis_id,
                module_run_id=meta_run.id,
                preprocessed=preprocessed,
            )

        return self._parser.build_from_module_outputs(
            workflow_run_id=workflow_run_id,
            synthesis_id=synthesis_id,
            preprocessed=preprocessed,
            module_runs=module_runs,
        )


def _find_meta_synthesis_run(module_runs: list[ModuleRun]) -> ModuleRun | None:
    for module_run in reversed(module_runs):
        if module_run.module_id == META_SYNTHESIS_MODULE_ID:
            return module_run
    return None


synthesis_engine = SynthesisEngine()
