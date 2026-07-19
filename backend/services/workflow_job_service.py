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
    def __init__(
        self,
        engine: WorkflowEngine | None = None,
        max_workers: int | None = None,
    ) -> None:
        self._engine = engine or workflow_engine
        workers = max_workers
        if workers is None:
            workers = max(1, int(settings.workflow_worker_max_in_flight or 2))
        self._executor = ThreadPoolExecutor(
            max_workers=workers,
            thread_name_prefix="workflow-job",
        )
        self._in_flight: set[Future] = set()
        self._active_run_ids: set[str] = set()

    def _prune_in_flight(self) -> None:
        done = {fut for fut in self._in_flight if fut.done()}
        self._in_flight -= done

    @property
    def in_flight_count(self) -> int:
        self._prune_in_flight()
        return len(self._in_flight)

    @property
    def active_run_ids(self) -> set[str]:
        return set(self._active_run_ids)

    def _submit_tracked(
        self,
        fn,
        *args,
        track_run_id: str | None = None,
        **kwargs,
    ) -> Future:  # noqa: ANN001
        if track_run_id:
            self._active_run_ids.add(track_run_id)

        def _wrapped():
            try:
                return fn(*args, **kwargs)
            finally:
                if track_run_id:
                    self._active_run_ids.discard(track_run_id)

        fut = self._executor.submit(_wrapped)
        self._in_flight.add(fut)
        fut.add_done_callback(lambda f: self._in_flight.discard(f))
        return fut

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
        return self._submit_tracked(
            self._execute_job,
            run_id,
            workflow_id,
            transcript_id,
            model,
            track_run_id=run_id,
        )

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
                    run.error_log = f"Retry exhausted after {max_attempts} attempt(s): {error}"
                    self._engine._repository.save(session, run)
                    logger.warning(
                        "Workflow run %s exhausted retries (%s)",
                        run_id,
                        max_attempts,
                        extra={
                            "event": "workflow.run.retry_exhausted",
                            "run_id": run_id,
                            "max_attempts": max_attempts,
                        },
                    )

    def poll_once(self) -> int:
        """Claim and execute queued runs (dedicated worker). Returns jobs started."""
        self._prune_in_flight()
        max_in_flight = max(1, int(settings.workflow_worker_max_in_flight or 1))
        max_claim = max(1, int(settings.workflow_worker_max_claim_per_poll or 1))
        capacity = max_in_flight - len(self._in_flight)
        if capacity <= 0:
            logger.debug(
                "Worker at max in-flight (%s); skipping claim",
                max_in_flight,
                extra={"event": "worker.claim.skipped", "reason": "max_in_flight"},
            )
            return 0

        claim_limit = min(max_claim, capacity)
        queued = self._engine.list_queued()
        started = 0
        for run in queued:
            if started >= claim_limit:
                break
            claimed = self._engine.claim_queued(run.id)
            if claimed is None:
                continue
            started += 1
            self._submit_tracked(
                self._run_claimed,
                claimed.id,
                claimed.workflow_id,
                claimed.transcript_id,
                claimed.model_used,
                track_run_id=claimed.id,
            )
        return started

    def queue_stats(self) -> dict[str, object]:
        stats = dict(self._engine.queue_stats())
        stats["worker_in_flight"] = self.in_flight_count
        stats["worker_max_in_flight"] = max(1, int(settings.workflow_worker_max_in_flight or 1))
        stats["worker_mode"] = self.worker_mode
        return stats

    def list_failed(self, *, limit: int = 50) -> list[WorkflowRun]:
        return self._engine.list_failed(limit=limit)

    def recover_stale(self, *, exclude_run_ids: set[str] | None = None) -> int:
        """Requeue or fail RUNNING jobs abandoned after a worker crash."""
        stale_after = float(settings.workflow_job_stale_seconds or 0)
        if stale_after <= 0:
            return 0
        exclude = exclude_run_ids if exclude_run_ids is not None else self.active_run_ids
        max_attempts = max(1, int(settings.workflow_job_max_attempts or 1))
        recovered = 0
        now = utc_now()
        for run in self._engine.list_incomplete():
            if run.id in exclude:
                continue
            if run.status == WorkflowRunStatus.CREATED.value:
                continue
            started = run.started_at
            if started.tzinfo is None:
                from datetime import UTC

                started = started.replace(tzinfo=UTC)
            age = (now - started).total_seconds()
            if age < stale_after:
                continue
            with get_session() as session:
                current = self._engine._repository.get(session, run.id)
                if current.status == WorkflowRunStatus.CREATED.value:
                    continue
                if current.attempt_count < max_attempts:
                    current.status = WorkflowRunStatus.CREATED.value
                    current.completed_at = None
                    current.error_log = (
                        f"Requeued after stale recovery (age={int(age)}s, "
                        f"attempt {current.attempt_count}/{max_attempts})"
                    )
                    self._engine._repository.save(session, current)
                    logger.warning(
                        "Stale run %s requeued (age=%ss)",
                        run.id,
                        int(age),
                        extra={"event": "workflow.run.stale_requeued", "run_id": run.id},
                    )
                else:
                    current.status = WorkflowRunStatus.FAILED.value
                    current.completed_at = utc_now()
                    current.error_log = (
                        f"Stale recovery exhausted retries after {int(age)}s "
                        f"({max_attempts} attempt(s))"
                    )
                    self._engine._repository.save(session, current)
                    logger.warning(
                        "Stale run %s failed after exhausted retries",
                        run.id,
                        extra={"event": "workflow.run.stale_failed", "run_id": run.id},
                    )
            recovered += 1
        return recovered

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
                self._submit_tracked(
                    self._engine.run,
                    workflow_run.workflow_id,
                    workflow_run.transcript_id,
                    workflow_run.model_used,
                    run_id=workflow_run.id,
                    track_run_id=workflow_run.id,
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
