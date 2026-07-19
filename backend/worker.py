"""Dedicated workflow worker process.

Polls the database for CREATED workflow runs and executes them outside the API
request lifecycle. Run with:

    python -m backend.worker

On AWS ECS, the worker task uses this entrypoint (same image as Dockerfile.cloud)
while the API sets WORKFLOW_WORKER_ENABLED=true so it only queues jobs.
"""

from __future__ import annotations

import json
import logging
import signal
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from backend.core.logging_config import configure_logging
from backend.db.base import init_db
from backend.domain.enums import WorkflowRunStatus
from backend.services.workflow_job_service import workflow_job_service
from config.settings import settings

logger = logging.getLogger(__name__)

_stop = False
_METRIC_NAMESPACE = "RRE/Dev"


def _handle_signal(signum, _frame) -> None:  # noqa: ANN001
    global _stop
    logger.info("Worker received signal %s; shutting down", signum)
    _stop = True


class _WorkerHealthHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def do_GET(self) -> None:  # noqa: N802
        if self.path not in {"/health", "/live", "/"}:
            self.send_response(404)
            self.end_headers()
            return
        body = {
            "status": "ok",
            "process": "worker",
            "in_flight": workflow_job_service.in_flight_count,
            "max_in_flight": max(1, int(settings.workflow_worker_max_in_flight or 1)),
            "active_run_ids": sorted(workflow_job_service.active_run_ids),
        }
        payload = json.dumps(body).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def _start_health_server(port: int) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer(("0.0.0.0", port), _WorkerHealthHandler)
    thread = threading.Thread(target=server.serve_forever, name="worker-health", daemon=True)
    thread.start()
    logger.info("Worker health listening on :%s", port, extra={"event": "worker.health.started"})
    return server


def _publish_queue_metrics(stats: dict[str, object]) -> None:
    try:
        import boto3
    except ImportError:
        return
    try:
        cw = boto3.client("cloudwatch", region_name=settings.resolved_aws_region)
        depth = int(stats.get("queue_depth") or 0)
        oldest = stats.get("oldest_queued_age_seconds")
        oldest_val = float(oldest) if oldest is not None else 0.0
        in_flight = int(stats.get("worker_in_flight") or 0)
        cw.put_metric_data(
            Namespace=_METRIC_NAMESPACE,
            MetricData=[
                {"MetricName": "QueueDepth", "Value": depth, "Unit": "Count"},
                {
                    "MetricName": "OldestQueuedJobAgeSeconds",
                    "Value": oldest_val,
                    "Unit": "Seconds",
                },
                {"MetricName": "WorkerInFlight", "Value": in_flight, "Unit": "Count"},
                {"MetricName": "WorkerHealthy", "Value": 1.0, "Unit": "Count"},
            ],
        )
    except Exception:  # noqa: BLE001
        logger.debug("CloudWatch metric publish skipped/failed", exc_info=True)


def main() -> None:
    configure_logging()
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    init_db()
    health_port = int(getattr(settings, "workflow_worker_health_port", 8080) or 8080)
    health_server = _start_health_server(health_port)

    poll = max(0.5, float(settings.workflow_worker_poll_seconds or 2.0))
    logger.info(
        "Workflow worker started (poll=%.1fs, timeout=%ss, max_attempts=%s)",
        poll,
        settings.workflow_job_timeout_seconds,
        settings.workflow_job_max_attempts,
        extra={"event": "worker.started"},
    )

    resumed = 0
    max_in_flight = max(1, int(settings.workflow_worker_max_in_flight or 1))
    for run in workflow_job_service._engine.list_incomplete():
        if run.status == WorkflowRunStatus.CREATED.value:
            continue
        if workflow_job_service.in_flight_count >= max_in_flight:
            logger.warning(
                "Deferred resume of remaining in-flight runs; at max_in_flight=%s",
                max_in_flight,
                extra={"event": "worker.resume.capped"},
            )
            break
        workflow_job_service._submit_tracked(
            workflow_job_service._run_claimed,
            run.id,
            run.workflow_id,
            run.transcript_id,
            run.model_used,
            track_run_id=run.id,
        )
        resumed += 1
    if resumed:
        logger.info("Worker resumed %s in-flight run(s)", resumed)

    while not _stop:
        try:
            recovered = workflow_job_service.recover_stale()
            if recovered:
                logger.info(
                    "Recovered %s stale job(s)",
                    recovered,
                    extra={"event": "worker.stale_recovered", "count": recovered},
                )
            started = workflow_job_service.poll_once()
            if started:
                logger.info("Worker claimed %s job(s)", started)
            stats = workflow_job_service.queue_stats()
            logger.info(
                "Worker heartbeat queue_depth=%s oldest_age=%s in_flight=%s",
                stats.get("queue_depth"),
                stats.get("oldest_queued_age_seconds"),
                stats.get("worker_in_flight"),
                extra={
                    "event": "worker.heartbeat",
                    "queue_depth": stats.get("queue_depth"),
                    "oldest_queued_age_seconds": stats.get("oldest_queued_age_seconds"),
                    "in_flight": stats.get("worker_in_flight"),
                },
            )
            _publish_queue_metrics(stats)
        except Exception:  # noqa: BLE001
            logger.exception("Worker poll failed")
        time.sleep(poll)

    health_server.shutdown()
    workflow_job_service.shutdown()
    logger.info("Workflow worker stopped", extra={"event": "worker.stopped"})


if __name__ == "__main__":
    main()
