"""Orchestrate multi-module analysis workflows."""

from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from backend.core.exceptions import WorkflowRunCancelled, WorkflowRunError, WorkflowRunTimeout
from backend.core.log_context import log_context_extra, workflow_run_id_var
from backend.core.module_registry import module_registry
from backend.core.workflow_registry import WorkflowDefinition, workflow_registry
from backend.db.base import get_session
from backend.domain.telemetry import aggregate_workflow_telemetry
from backend.domain.enums import ModuleRunStatus, WorkflowRunStatus
from backend.domain.finding import ModuleRun
from backend.domain.workflow import WorkflowRun
from backend.repositories.workflow_run_repository import WorkflowRunRepository, utc_now
from backend.services.convergence_scoring_service import (
    ConvergenceScoringService,
    convergence_scoring_service,
)
from backend.services.graph_merge_service import GraphMergeService, graph_merge_service
from backend.services.module_runner import (
    ModuleRunner,
    compact_module_output_for_handoff,
    module_runner,
)
from backend.services.transcript_service import TranscriptService, transcript_service
from backend.services.safety_risk_scanner import SKIP_IN_SAFETY_MODE
from config.settings import settings

logger = logging.getLogger(__name__)


class WorkflowEngine:
    def __init__(
        self,
        workflows=workflow_registry,
        modules=module_registry,
        runner: ModuleRunner | None = None,
        transcripts: TranscriptService | None = None,
        repository: WorkflowRunRepository | None = None,
        graph_merge: GraphMergeService | None = None,
        convergence: ConvergenceScoringService | None = None,
    ) -> None:
        self._workflows = workflows
        self._modules = modules
        self._runner = runner or module_runner
        self._transcripts = transcripts or transcript_service
        self._repository = repository or WorkflowRunRepository()
        self._graph_merge = graph_merge or graph_merge_service
        self._convergence = convergence or convergence_scoring_service

    def create_run(
        self,
        workflow_id: str,
        transcript_id: str,
        model: str | None = None,
        *,
        queued: bool = False,
        safety_mode: bool = False,
    ) -> WorkflowRun:
        self._workflows.get(workflow_id)
        self._transcripts.ensure_ready_for_analysis(transcript_id)

        with get_session() as session:
            workflow_run = self._repository.create(
                session,
                workflow_id=workflow_id,
                transcript_id=transcript_id,
                model_used=model,
                status=(
                    WorkflowRunStatus.CREATED.value
                    if queued
                    else WorkflowRunStatus.RUNNING_MODULES.value
                ),
                safety_mode=safety_mode,
            )
            if not queued:
                workflow_run.status = WorkflowRunStatus.RUNNING_MODULES.value
                self._repository.save(session, workflow_run)
        return workflow_run

    def request_cancel(self, run_id: str) -> WorkflowRun:
        with get_session() as session:
            workflow_run = self._repository.get(session, run_id)
            terminal = {
                WorkflowRunStatus.COMPLETED.value,
                WorkflowRunStatus.FAILED.value,
                WorkflowRunStatus.CANCELLED.value,
            }
            if workflow_run.status in terminal:
                return workflow_run
            workflow_run.cancel_requested = True
            if workflow_run.status == WorkflowRunStatus.CREATED.value:
                workflow_run.status = WorkflowRunStatus.CANCELLED.value
                workflow_run.completed_at = utc_now()
                workflow_run.error_log = "Cancelled before execution"
            self._repository.save(session, workflow_run)
            return workflow_run

    def run(
        self,
        workflow_id: str,
        transcript_id: str,
        model: str | None = None,
        *,
        run_id: str | None = None,
        safety_mode: bool | None = None,
    ) -> WorkflowRun:
        workflow = self._workflows.get(workflow_id)
        self._transcripts.ensure_ready_for_analysis(transcript_id)

        if run_id:
            workflow_run = self.get(run_id)
            if workflow_run.workflow_id != workflow_id:
                raise WorkflowRunError("Workflow run does not match workflow_id")
            if workflow_run.transcript_id != transcript_id:
                raise WorkflowRunError("Workflow run does not match transcript_id")
            existing_module_runs = self._runner.list_by_workflow_run(run_id)
            resolved_model = model or workflow_run.model_used
            resolved_safety = (
                workflow_run.safety_mode if safety_mode is None else safety_mode
            )
        else:
            resolved_safety = bool(safety_mode)
            workflow_run = self.create_run(
                workflow_id,
                transcript_id,
                model=model,
                safety_mode=resolved_safety,
            )
            existing_module_runs = []
            resolved_model = model

        workflow_run.safety_mode = resolved_safety
        return self._execute(
            workflow,
            workflow_run,
            existing_module_runs,
            resolved_model,
        )

    def get(self, run_id: str) -> WorkflowRun:
        with get_session() as session:
            return self._repository.get(session, run_id)

    def get_with_module_runs(self, run_id: str) -> tuple[WorkflowRun, list[ModuleRun]]:
        workflow_run = self.get(run_id)
        module_runs = self._runner.list_by_workflow_run(run_id)
        return workflow_run, module_runs

    def list_incomplete(self) -> list[WorkflowRun]:
        with get_session() as session:
            return self._repository.list_incomplete(session)

    def list_queued(self) -> list[WorkflowRun]:
        with get_session() as session:
            return self._repository.list_queued(session)

    def list_failed(self, *, limit: int = 50) -> list[WorkflowRun]:
        with get_session() as session:
            return self._repository.list_failed(session, limit=limit)

    def queue_stats(self) -> dict[str, object]:
        with get_session() as session:
            return self._repository.queue_stats(session)

    def claim_queued(self, run_id: str) -> WorkflowRun | None:
        with get_session() as session:
            return self._repository.claim_queued(session, run_id)

    def _module_concurrency(self) -> int:
        # SQLite write contention makes parallel module runs unsafe in pytest/local DB.
        if settings.is_sqlite:
            return 1
        return max(1, int(settings.workflow_module_concurrency or 1))

    def _check_abort(self, workflow_run: WorkflowRun, started: float) -> None:
        refreshed = self.get(workflow_run.id)
        workflow_run.cancel_requested = refreshed.cancel_requested
        workflow_run.status = refreshed.status
        if refreshed.cancel_requested or refreshed.status == WorkflowRunStatus.CANCELLED.value:
            workflow_run.status = WorkflowRunStatus.CANCELLED.value
            workflow_run.completed_at = utc_now()
            workflow_run.error_log = "Cancelled by user"
            self._persist(workflow_run)
            raise WorkflowRunCancelled(f"Workflow run {workflow_run.id} cancelled")

        timeout = float(settings.workflow_job_timeout_seconds or 0)
        if timeout > 0 and (time.monotonic() - started) > timeout:
            workflow_run.status = WorkflowRunStatus.FAILED.value
            workflow_run.completed_at = utc_now()
            workflow_run.error_log = f"Timed out after {int(timeout)}s"
            self._persist(workflow_run)
            raise WorkflowRunTimeout(workflow_run.error_log)

    def _execute(
        self,
        workflow: WorkflowDefinition,
        workflow_run: WorkflowRun,
        existing_module_runs: list[ModuleRun],
        model: str | None,
    ) -> WorkflowRun:
        started = time.monotonic()
        transcript_id = workflow_run.transcript_id
        workflow_token = workflow_run_id_var.set(workflow_run.id)
        completed_module_ids = {
            module_run.module_id
            for module_run in existing_module_runs
            if module_run.status == ModuleRunStatus.COMPLETED.value
        }
        prior_outputs = [
            compact_module_output_for_handoff(module_run.parsed_output)
            for module_run in existing_module_runs
            if module_run.parsed_output
            and module_run.status == ModuleRunStatus.COMPLETED.value
        ]
        module_runs = list(existing_module_runs)

        logger.info(
            "Workflow run %s starting modules for %s",
            workflow_run.id,
            workflow.config.id,
            extra=log_context_extra(
                event="workflow.run.started",
                run_id=workflow_run.id,
                workflow_id=workflow.config.id,
                status=workflow_run.status,
            ),
        )

        workflow_run.status = WorkflowRunStatus.RUNNING_MODULES.value
        self._persist(workflow_run)

        try:
            waves = workflow.waves
            if waves is None:
                return self._execute_linear(
                    workflow,
                    workflow_run,
                    transcript_id,
                    completed_module_ids,
                    prior_outputs,
                    module_runs,
                    model,
                    started,
                )

            for wave in waves:
                self._check_abort(workflow_run, started)
                pending = [
                    m
                    for m in wave.module_ids
                    if m not in completed_module_ids
                    and not (
                        workflow_run.safety_mode and m in SKIP_IN_SAFETY_MODE
                    )
                ]
                if not pending:
                    continue
                if wave.is_synthesis or any(
                    self._modules.get(m).config.input_type == "module_outputs"
                    for m in pending
                ):
                    with get_session() as session:
                        self._graph_merge.merge_workflow_constructs_in_session(
                            session, workflow_run.id
                        )
                        self._convergence.score_workflow_constructs_in_session(
                            session, workflow_run.id
                        )
                    workflow_run.status = WorkflowRunStatus.SYNTHESIZING.value
                    self._persist(workflow_run)
                    for module_id in pending:
                        self._check_abort(workflow_run, started)
                        module_run = self._runner.run_synthesis(
                            module_id=module_id,
                            transcript_id=transcript_id,
                            prior_outputs=prior_outputs,
                            model=model,
                            workflow_run_id=workflow_run.id,
                            safety_mode=workflow_run.safety_mode,
                        )
                        module_runs.append(module_run)
                        if module_run.status != ModuleRunStatus.COMPLETED.value:
                            return self._fail_workflow(
                                workflow_run,
                                module_run,
                                f"Module {module_id} failed",
                                started,
                            )
                        if module_run.parsed_output:
                            prior_outputs.append(
                                compact_module_output_for_handoff(module_run.parsed_output)
                            )
                        completed_module_ids.add(module_id)
                else:
                    failed = self._run_transcript_wave(
                        workflow_run=workflow_run,
                        transcript_id=transcript_id,
                        module_ids=pending,
                        model=model,
                        module_runs=module_runs,
                        prior_outputs=prior_outputs,
                        started=started,
                    )
                    if failed is not None:
                        return failed
                    completed_module_ids.update(pending)

            return self._complete_workflow(workflow_run, module_runs, started)
        except WorkflowRunCancelled:
            return self.get(workflow_run.id)
        except WorkflowRunTimeout:
            return self.get(workflow_run.id)
        except WorkflowRunError:
            raise
        except Exception as exc:
            logger.exception(
                "Workflow run %s failed unexpectedly",
                workflow_run.id,
                extra=log_context_extra(
                    event="workflow.run.failed",
                    error_type=type(exc).__name__,
                    run_id=workflow_run.id,
                    workflow_id=workflow_run.workflow_id,
                ),
            )
            workflow_run.status = WorkflowRunStatus.FAILED.value
            workflow_run.error_log = str(exc)
            workflow_run.completed_at = utc_now()
            self._persist(workflow_run)
            raise WorkflowRunError(f"Workflow failed: {exc}") from exc
        finally:
            workflow_run_id_var.reset(workflow_token)

    def _execute_linear(
        self,
        workflow: WorkflowDefinition,
        workflow_run: WorkflowRun,
        transcript_id: str,
        completed_module_ids: set[str],
        prior_outputs: list[dict],
        module_runs: list[ModuleRun],
        model: str | None,
        started: float,
    ) -> WorkflowRun:
        pending_transcript: list[str] = []

        def flush_transcript_wave() -> WorkflowRun | None:
            nonlocal pending_transcript
            if not pending_transcript:
                return None
            wave = pending_transcript
            pending_transcript = []
            return self._run_transcript_wave(
                workflow_run=workflow_run,
                transcript_id=transcript_id,
                module_ids=wave,
                model=model,
                module_runs=module_runs,
                prior_outputs=prior_outputs,
                started=started,
            )

        for module_id in workflow.module_sequence:
            self._check_abort(workflow_run, started)
            if workflow_run.safety_mode and module_id in SKIP_IN_SAFETY_MODE:
                logger.info(
                    "Skipping module %s for safety_mode on workflow run %s",
                    module_id,
                    workflow_run.id,
                    extra={
                        "event": "workflow.module.skipped",
                        "run_id": workflow_run.id,
                        "workflow_id": workflow.config.id,
                        "module_id": module_id,
                        "reason": "safety_mode",
                    },
                )
                continue
            if module_id in completed_module_ids:
                logger.info(
                    "Skipping completed module %s for workflow run %s",
                    module_id,
                    workflow_run.id,
                    extra={
                        "event": "workflow.module.skipped",
                        "run_id": workflow_run.id,
                        "workflow_id": workflow.config.id,
                        "module_id": module_id,
                    },
                )
                continue

            module = self._modules.get(module_id)
            if module.config.input_type == "module_outputs":
                failed = flush_transcript_wave()
                if failed is not None:
                    return failed
                with get_session() as session:
                    self._graph_merge.merge_workflow_constructs_in_session(
                        session, workflow_run.id
                    )
                    self._convergence.score_workflow_constructs_in_session(
                        session, workflow_run.id
                    )
                workflow_run.status = WorkflowRunStatus.SYNTHESIZING.value
                self._persist(workflow_run)
                module_run = self._runner.run_synthesis(
                    module_id=module_id,
                    transcript_id=transcript_id,
                    prior_outputs=prior_outputs,
                    model=model,
                    workflow_run_id=workflow_run.id,
                    safety_mode=workflow_run.safety_mode,
                )
                module_runs.append(module_run)
                if module_run.status != ModuleRunStatus.COMPLETED.value:
                    return self._fail_workflow(
                        workflow_run,
                        module_run,
                        f"Module {module_id} failed",
                        started,
                    )
                if module_run.parsed_output:
                    prior_outputs.append(
                        compact_module_output_for_handoff(module_run.parsed_output)
                    )
            else:
                pending_transcript.append(module_id)

        failed = flush_transcript_wave()
        if failed is not None:
            return failed

        return self._complete_workflow(workflow_run, module_runs, started)

    def _run_transcript_wave(
        self,
        *,
        workflow_run: WorkflowRun,
        transcript_id: str,
        module_ids: list[str],
        model: str | None,
        module_runs: list[ModuleRun],
        prior_outputs: list[dict],
        started: float,
    ) -> WorkflowRun | None:
        """Run independent transcript modules with bounded parallelism.

        Returns a failed WorkflowRun if any module fails; otherwise None after
        appending results in YAML order to module_runs / prior_outputs.
        """
        if not module_ids:
            return None

        concurrency = min(self._module_concurrency(), len(module_ids))
        logger.info(
            "Workflow run %s running transcript wave size=%s concurrency=%s modules=%s",
            workflow_run.id,
            len(module_ids),
            concurrency,
            module_ids,
            extra={
                "event": "workflow.wave.started",
                "run_id": workflow_run.id,
                "workflow_id": workflow_run.workflow_id,
                "module_count": len(module_ids),
                "concurrency": concurrency,
            },
        )

        results: dict[str, ModuleRun] = {}
        if concurrency == 1:
            for module_id in module_ids:
                self._check_abort(workflow_run, started)
                module_run = self._runner.run(
                    module_id=module_id,
                    transcript_id=transcript_id,
                    model=model,
                    workflow_run_id=workflow_run.id,
                )
                results[module_id] = module_run
                if module_run.status != ModuleRunStatus.COMPLETED.value:
                    module_runs.append(module_run)
                    return self._fail_workflow(
                        workflow_run,
                        module_run,
                        f"Module {module_id} failed",
                        started,
                    )
        else:
            with ThreadPoolExecutor(
                max_workers=concurrency,
                thread_name_prefix="workflow-module",
            ) as pool:
                futures = {
                    pool.submit(
                        self._runner.run,
                        module_id,
                        transcript_id,
                        model,
                        workflow_run.id,
                    ): module_id
                    for module_id in module_ids
                }
                first_failure: ModuleRun | None = None
                for future in as_completed(futures):
                    module_id = futures[future]
                    try:
                        module_run = future.result()
                    except Exception as exc:  # noqa: BLE001
                        logger.exception(
                            "Parallel module %s raised for workflow run %s",
                            module_id,
                            workflow_run.id,
                        )
                        workflow_run.status = WorkflowRunStatus.FAILED.value
                        workflow_run.completed_at = utc_now()
                        workflow_run.error_log = f"Module {module_id} failed: {exc}"
                        self._persist(workflow_run)
                        for pending in futures:
                            pending.cancel()
                        raise WorkflowRunError(workflow_run.error_log) from exc
                    results[module_id] = module_run
                    if (
                        module_run.status != ModuleRunStatus.COMPLETED.value
                        and first_failure is None
                    ):
                        first_failure = module_run

                if first_failure is not None:
                    # Preserve YAML order for any completed siblings already stored.
                    for module_id in module_ids:
                        if module_id in results:
                            module_runs.append(results[module_id])
                    return self._fail_workflow(
                        workflow_run,
                        first_failure,
                        f"Module {first_failure.module_id} failed",
                        started,
                    )

        for module_id in module_ids:
            module_run = results[module_id]
            module_runs.append(module_run)
            if module_run.parsed_output:
                prior_outputs.append(
                    compact_module_output_for_handoff(module_run.parsed_output)
                )
        return None

    def _complete_workflow(
        self,
        workflow_run: WorkflowRun,
        module_runs: list[ModuleRun],
        started: float,
    ) -> WorkflowRun:
        workflow_run.status = WorkflowRunStatus.COMPLETED.value
        workflow_run.completed_at = utc_now()
        workflow_run.error_log = None
        module_telem = [
            run.telemetry
            for run in module_runs
            if isinstance(run.telemetry, dict)
        ]
        if module_telem:
            workflow_run.telemetry_summary = aggregate_workflow_telemetry(module_telem)
        with get_session() as session:
            self._graph_merge.merge_workflow_constructs_in_session(session, workflow_run.id)
            self._convergence.score_workflow_constructs_in_session(session, workflow_run.id)
        self._persist(workflow_run)
        duration_ms = int((time.monotonic() - started) * 1000)
        logger.info(
            "Workflow run %s completed with %s module runs",
            workflow_run.id,
            len(module_runs),
            extra={
                "event": "workflow.run.completed",
                "run_id": workflow_run.id,
                "workflow_id": workflow_run.workflow_id,
                "status": workflow_run.status,
                "duration_ms": duration_ms,
                "telemetry_summary": workflow_run.telemetry_summary,
            },
        )
        return workflow_run

    def _fail_workflow(
        self,
        workflow_run: WorkflowRun,
        module_run: ModuleRun,
        message: str,
        started: float,
    ) -> WorkflowRun:
        workflow_run.status = WorkflowRunStatus.FAILED.value
        workflow_run.completed_at = utc_now()
        errors = module_run.validation_errors or [message]
        workflow_run.error_log = "; ".join(errors)
        self._persist(workflow_run)
        duration_ms = int((time.monotonic() - started) * 1000)
        logger.warning(
            "Workflow run %s failed at module %s: %s",
            workflow_run.id,
            module_run.module_id,
            workflow_run.error_log,
            extra={
                "event": "workflow.run.failed",
                "run_id": workflow_run.id,
                "workflow_id": workflow_run.workflow_id,
                "module_id": module_run.module_id,
                "status": workflow_run.status,
                "duration_ms": duration_ms,
            },
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
