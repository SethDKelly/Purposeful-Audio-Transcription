"""Dedicated workflow worker process.

Polls the database for CREATED workflow runs and executes them outside the API
request lifecycle. Run with:

    python -m backend.worker

On AWS ECS, the worker task uses this entrypoint (same image as Dockerfile.cloud)
while the API sets WORKFLOW_WORKER_ENABLED=true so it only queues jobs.
"""

from __future__ import annotations

import logging
import signal
import time

from backend.core.logging_config import configure_logging
from backend.db.base import init_db
from backend.domain.enums import WorkflowRunStatus
from backend.services.workflow_job_service import workflow_job_service
from config.settings import settings

logger = logging.getLogger(__name__)

_stop = False


def _handle_signal(signum, _frame) -> None:  # noqa: ANN001
    global _stop
    logger.info("Worker received signal %s; shutting down", signum)
    _stop = True


def main() -> None:
    configure_logging()
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    init_db()
    poll = max(0.5, float(settings.workflow_worker_poll_seconds or 2.0))
    logger.info(
        "Workflow worker started (poll=%.1fs, timeout=%ss, max_attempts=%s)",
        poll,
        settings.workflow_job_timeout_seconds,
        settings.workflow_job_max_attempts,
        extra={"event": "worker.started"},
    )

    resumed = 0
    for run in workflow_job_service._engine.list_incomplete():
        if run.status == WorkflowRunStatus.CREATED.value:
            continue
        workflow_job_service._executor.submit(
            workflow_job_service._run_claimed,
            run.id,
            run.workflow_id,
            run.transcript_id,
            run.model_used,
        )
        resumed += 1
    if resumed:
        logger.info("Worker resumed %s in-flight run(s)", resumed)

    while not _stop:
        try:
            started = workflow_job_service.poll_once()
            if started:
                logger.info("Worker claimed %s job(s)", started)
        except Exception:  # noqa: BLE001
            logger.exception("Worker poll failed")
        time.sleep(poll)

    workflow_job_service.shutdown()
    logger.info("Workflow worker stopped", extra={"event": "worker.stopped"})


if __name__ == "__main__":
    main()
