"""Background workflow execution and restart recovery."""

import logging
from concurrent.futures import Future, ThreadPoolExecutor

from backend.domain.workflow import WorkflowRun
from backend.services.workflow_engine import WorkflowEngine, workflow_engine

logger = logging.getLogger(__name__)


class WorkflowJobService:
    def __init__(self, engine: WorkflowEngine | None = None, max_workers: int = 2) -> None:
        self._engine = engine or workflow_engine
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="workflow-job",
        )

    def start_background_run(
        self,
        workflow_id: str,
        transcript_id: str,
        model: str | None = None,
    ) -> WorkflowRun:
        workflow_run = self._engine.create_run(
            workflow_id=workflow_id,
            transcript_id=transcript_id,
            model=model,
        )
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
            },
        )
        return self._executor.submit(
            self._engine.run,
            workflow_id,
            transcript_id,
            model,
            run_id=run_id,
        )

    def resume_incomplete(self) -> int:
        incomplete = self._engine.list_incomplete()
        for workflow_run in incomplete:
            self.submit_existing_run(
                workflow_id=workflow_run.workflow_id,
                transcript_id=workflow_run.transcript_id,
                run_id=workflow_run.id,
                model=workflow_run.model_used,
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
