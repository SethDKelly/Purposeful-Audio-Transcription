"""Orchestrate multi-module analysis workflows."""

import logging

from backend.core.exceptions import WorkflowRunError
from backend.core.module_registry import module_registry
from backend.core.workflow_registry import WorkflowDefinition, workflow_registry
from backend.db.base import get_session
from backend.domain.enums import ModuleRunStatus, WorkflowRunStatus
from backend.domain.finding import ModuleRun
from backend.domain.workflow import WorkflowRun
from backend.repositories.workflow_run_repository import WorkflowRunRepository, utc_now
from backend.services.module_runner import ModuleRunner, module_runner
from backend.services.transcript_service import TranscriptService, transcript_service

logger = logging.getLogger(__name__)


class WorkflowEngine:
    def __init__(
        self,
        workflows=workflow_registry,
        modules=module_registry,
        runner: ModuleRunner | None = None,
        transcripts: TranscriptService | None = None,
        repository: WorkflowRunRepository | None = None,
    ) -> None:
        self._workflows = workflows
        self._modules = modules
        self._runner = runner or module_runner
        self._transcripts = transcripts or transcript_service
        self._repository = repository or WorkflowRunRepository()

    def run(
        self,
        workflow_id: str,
        transcript_id: str,
        model: str | None = None,
    ) -> WorkflowRun:
        workflow = self._workflows.get(workflow_id)
        self._transcripts.get(transcript_id)

        with get_session() as session:
            workflow_run = self._repository.create(
                session,
                workflow_id=workflow_id,
                transcript_id=transcript_id,
                model_used=model,
            )
            workflow_run.status = WorkflowRunStatus.RUNNING_MODULES.value
            self._repository.save(session, workflow_run)

        module_runs: list[ModuleRun] = []
        prior_outputs: list[dict] = []

        try:
            for module_id in workflow.module_sequence:
                module = self._modules.get(module_id)
                if module.config.input_type == "module_outputs":
                    workflow_run.status = WorkflowRunStatus.SYNTHESIZING.value
                    self._persist(workflow_run)
                    module_run = self._runner.run_synthesis(
                        module_id=module_id,
                        transcript_id=transcript_id,
                        prior_outputs=prior_outputs,
                        model=model,
                        workflow_run_id=workflow_run.id,
                    )
                else:
                    module_run = self._runner.run(
                        module_id=module_id,
                        transcript_id=transcript_id,
                        model=model,
                        workflow_run_id=workflow_run.id,
                    )

                module_runs.append(module_run)
                if module_run.status != ModuleRunStatus.COMPLETED.value:
                    return self._fail_workflow(
                        workflow_run,
                        module_run,
                        f"Module {module_id} failed",
                    )

                if module_run.parsed_output:
                    prior_outputs.append(module_run.parsed_output)

            return self._complete_workflow(workflow_run, module_runs)
        except WorkflowRunError:
            raise
        except Exception as exc:
            logger.exception("Workflow run %s failed unexpectedly", workflow_run.id)
            workflow_run.status = WorkflowRunStatus.FAILED.value
            workflow_run.error_log = str(exc)
            workflow_run.completed_at = utc_now()
            self._persist(workflow_run)
            raise WorkflowRunError(f"Workflow failed: {exc}") from exc

    def get(self, run_id: str) -> WorkflowRun:
        with get_session() as session:
            return self._repository.get(session, run_id)

    def get_with_module_runs(self, run_id: str) -> tuple[WorkflowRun, list[ModuleRun]]:
        workflow_run = self.get(run_id)
        module_runs = self._runner.list_by_workflow_run(run_id)
        return workflow_run, module_runs

    def _complete_workflow(
        self,
        workflow_run: WorkflowRun,
        module_runs: list[ModuleRun],
    ) -> WorkflowRun:
        workflow_run.status = WorkflowRunStatus.COMPLETED.value
        workflow_run.completed_at = utc_now()
        workflow_run.error_log = None
        self._persist(workflow_run)
        logger.info(
            "Workflow run %s completed with %s module runs",
            workflow_run.id,
            len(module_runs),
        )
        return workflow_run

    def _fail_workflow(
        self,
        workflow_run: WorkflowRun,
        module_run: ModuleRun,
        message: str,
    ) -> WorkflowRun:
        workflow_run.status = WorkflowRunStatus.FAILED.value
        workflow_run.completed_at = utc_now()
        errors = module_run.validation_errors or [message]
        workflow_run.error_log = "; ".join(errors)
        self._persist(workflow_run)
        logger.warning(
            "Workflow run %s failed at module %s: %s",
            workflow_run.id,
            module_run.module_id,
            workflow_run.error_log,
        )
        return workflow_run

    def _persist(self, workflow_run: WorkflowRun) -> None:
        with get_session() as session:
            self._repository.save(session, workflow_run)


def build_workflow_analysis_text(
    workflow: WorkflowDefinition,
    module_runs: list[ModuleRun],
) -> str:
    sections: list[str] = [f"# {workflow.config.name}", ""]
    for module_run in module_runs:
        if not module_run.parsed_output:
            continue
        output = module_run.parsed_output
        sections.append(f"## {output.get('module_id', module_run.module_id)}")
        sections.append(output.get("executive_summary", ""))
        report = output.get("raw_markdown_report", "").strip()
        if report:
            sections.append(report)
        sections.append("")
    return "\n".join(sections).strip()


workflow_engine = WorkflowEngine()
