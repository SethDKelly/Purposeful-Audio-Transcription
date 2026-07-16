"""Background workflow execution, cancel, retries, and worker handoff."""

from __future__ import annotations

import logging
from concurrent.futures import Future, ThreadPoolExecutor

from backend.core.exceptions import WorkflowRunCancelled, WorkflowRunTimeout
from backend.db.base import get_session
from backend.domain.enums import WorkflowRunStatus
from backend.domain.workflow import WorkflowRun
from backend.repositories.workflow_run_repository import utc_now
from backend.services.workflow_engine import WorkflowEngine, workflow_engine
from config.settings import settings

logger = logging.getLogger(__name__)


class WorkflowJobService:
    def __init__(self, engine: WorkflowEngine | None = None, max_workers: int = 2) -> None:
        self._engine = engine or workflow_engine
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="workflow-job",
        )

    @property
    def worker_mode(self) -> bool:
        return bool(settings.workflow_worker_enabled)

    def start_background_run(
        self,
        workflow_id: str,
        transcript_id: str,
        model: str | None = None,
        safety_mode: bool = False,
    ) -> WorkflowRun:
        workflow_run = self._engine.create_run(
            workflow_id=workflow_id,
            transcript_id=transcript_id,
            model=model,
            queued=True,
            safety_mode=safety_mode,
        )
        if self.worker_mode:
            logger.info(
                "Queued workflow run %s for dedicated worker",
                workflow_run.id,
                extra={
                    "event": "workflow.run.queued",
                    "run_id": workflow_run.id,
                    "workflow_id": workflow_id,
                    "mode": "worker",
                },
            )
            return workflow_run

        self.submit_existing_run(
            workflow_id=workflow_id,
            transcript_id=transcript_id,
            run_id=workflow_run.id,
            model=model,
        )
        return workflow_run

    def submit_existing_run(
        self,
        *,
        workflow_id: str,
        transcript_id: str,
        run_id: str,
        model: str | None = None,
    ) -> Future:
        logger.info(
            "Queued workflow run %s for background execution",
            run_id,
            extra={
                "event": "workflow.run.queued",
                "run_id": run_id,
                "workflow_id": workflow_id,
                "mode": "inline",
            },
        )
        return self._executor.submit(self._execute_job, run_id, workflow_id, transcript_id, model)

    def _execute_job(
        self,
        run_id: str,
        workflow_id: str,
        transcript_id: str,
        model: str | None,
    ) -> WorkflowRun | None:
        claimed = self._engine.claim_queued(run_id)
        if claimed is None:
            # Already claimed, cancelled, or not queued — try resume path.
            current = self._engine.get(run_id)
            if current.status in {
                WorkflowRunStatus.CANCELLED.value,
                WorkflowRunStatus.COMPLETED.value,
                WorkflowRunStatus.FAILED.value,
            }:
                return current
            if current.cancel_requested:
                return self._engine.request_cancel(run_id)
        else:
            current = claimed

        try:
            return self._engine.run(
                workflow_id,
                transcript_id,
                model or current.model_used,
                run_id=run_id,
            )
        except (WorkflowRunCancelled, WorkflowRunTimeout):
            return self._engine.get(run_id)
        except Exception as exc:  # noqa: BLE001
            logger.exception(
                "Background workflow run %s failed",
                run_id,
                extra={"event": "workflow.run.failed", "run_id": run_id},
            )
            self._maybe_requeue(run_id, str(exc))
            return self._engine.get(run_id)

    def _maybe_requeue(self, run_id: str, error: str) -> None:
        max_attempts = max(1, int(settings.workflow_job_max_attempts or 1))
        with get_session() as session:
            run = self._engine._repository.get(session, run_id)
            if run.cancel_requested:
                run.status = WorkflowRunStatus.CANCELLED.value
                run.completed_at = utc_now()
                run.error_log = error
                self._engine._repository.save(session, run)
                return
            if run.attempt_count < max_attempts:
                run.status = WorkflowRunStatus.CREATED.value
                run.completed_at = None
                run.error_log = f"Retrying after failure (attempt {run.attempt_count}): {error}"
                self._engine._repository.save(session, run)
                logger.info(
                    "Requeued workflow run %s (attempt %s/%s)",
                    run_id,
                    run.attempt_count,
                    max_attempts,
                    extra={"event": "workflow.run.requeued", "run_id": run_id},
                )
                if not self.worker_mode:
                    self.submit_existing_run(
                        workflow_id=run.workflow_id,
                        transcript_id=run.transcript_id,
                        run_id=run.id,
                        model=run.model_used,
                    )
            else:
                if run.status not in {
                    WorkflowRunStatus.FAILED.value,
                    WorkflowRunStatus.CANCELLED.value,
                }:
                    run.status = WorkflowRunStatus.FAILED.value
                    run.completed_at = utc_now()
                    run.error_log = error
                    self._engine._repository.save(session, run)

    def poll_once(self) -> int:
        """Claim and execute queued runs (dedicated worker). Returns jobs started."""
        queued = self._engine.list_queued()
        started = 0
        for run in queued:
            claimed = self._engine.claim_queued(run.id)
            if claimed is None:
                continue
            started += 1
            self._executor.submit(
                self._run_claimed,
                claimed.id,
                claimed.workflow_id,
                claimed.transcript_id,
                claimed.model_used,
            )
        return started

    def _run_claimed(
        self,
        run_id: str,
        workflow_id: str,
        transcript_id: str,
        model: str | None,
    ) -> WorkflowRun | None:
        try:
            return self._engine.run(workflow_id, transcript_id, model, run_id=run_id)
        except (WorkflowRunCancelled, WorkflowRunTimeout):
            return self._engine.get(run_id)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Worker job %s failed", run_id)
            self._maybe_requeue(run_id, str(exc))
            return self._engine.get(run_id)

    def resume_incomplete(self) -> int:
        if self.worker_mode:
            # Dedicated worker owns queue recovery; avoid double execution from API.
            logger.info(
                "Skipping API resume_incomplete; WORKFLOW_WORKER_ENABLED is set",
                extra={"event": "workflow.run.resume_skipped"},
            )
            return 0
        incomplete = self._engine.list_incomplete()
        for workflow_run in incomplete:
            if workflow_run.status == WorkflowRunStatus.CREATED.value:
                self.submit_existing_run(
                    workflow_id=workflow_run.workflow_id,
                    transcript_id=workflow_run.transcript_id,
                    run_id=workflow_run.id,
                    model=workflow_run.model_used,
                )
            else:
                # In-flight resume: re-enter run() which skips completed modules.
                self._executor.submit(
                    self._engine.run,
                    workflow_run.workflow_id,
                    workflow_run.transcript_id,
                    workflow_run.model_used,
                    run_id=workflow_run.id,
                )
        if incomplete:
            logger.info(
                "Resumed %s incomplete workflow run(s) after startup",
                len(incomplete),
                extra={"event": "workflow.run.resumed", "status": "queued"},
            )
        return len(incomplete)

    def shutdown(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=True)


workflow_job_service = WorkflowJobService()
