#!/usr/bin/env python3
"""Scale ECS services to 0 and wait until no tasks remain before a fresh deploy.

For desired_count=1 Fargate + ALB, overlapping replace is brittle: the old task
still serves (or fails) health checks while the new task boots. Clearing first
avoids dual-target drain races and connection storms on RDS.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time


def log(msg: str) -> None:
    print(msg, flush=True)


def run_aws(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["aws", *args],
        check=check,
        capture_output=True,
        text=True,
    )


def describe_services(cluster: str, services: list[str]) -> dict:
    result = run_aws(
        [
            "ecs",
            "describe-services",
            "--cluster",
            cluster,
            "--services",
            *services,
            "--output",
            "json",
        ]
    )
    return json.loads(result.stdout)


def scale_to_zero(cluster: str, services: list[str]) -> None:
    for name in services:
        # Ignore Missing/inactive services on first-ever apply (pre-terraform).
        exists = run_aws(
            [
                "ecs",
                "describe-services",
                "--cluster",
                cluster,
                "--services",
                name,
                "--query",
                "services[0].status",
                "--output",
                "text",
            ],
            check=False,
        )
        status = (exists.stdout or "").strip()
        if exists.returncode != 0 or status in ("", "None", "INACTIVE"):
            log(f"{name}: not active yet; skip scale-down")
            continue
        log(f"{name}: setting desiredCount=0")
        run_aws(
            [
                "ecs",
                "update-service",
                "--cluster",
                cluster,
                "--service",
                name,
                "--desired-count",
                "0",
                "--no-cli-pager",
            ]
        )


def stop_running_tasks(cluster: str, services: list[str]) -> None:
    """Force-stop any lingering RUNNING tasks after desired=0 (faster than drain)."""
    for name in services:
        listed = run_aws(
            [
                "ecs",
                "list-tasks",
                "--cluster",
                cluster,
                "--service-name",
                name,
                "--desired-status",
                "RUNNING",
                "--output",
                "json",
            ],
            check=False,
        )
        if listed.returncode != 0:
            continue
        arns = json.loads(listed.stdout or "{}").get("taskArns") or []
        for arn in arns:
            log(f"{name}: stop-task {arn.rsplit('/', 1)[-1]}")
            run_aws(
                [
                    "ecs",
                    "stop-task",
                    "--cluster",
                    cluster,
                    "--task",
                    arn,
                    "--reason",
                    "clear-before-deploy",
                    "--no-cli-pager",
                ],
                check=False,
            )


def fully_drained(data: dict) -> bool:
    for svc in data.get("services", []):
        name = svc.get("serviceName")
        status = svc.get("status")
        if status == "INACTIVE":
            continue
        desired = int(svc.get("desiredCount") or 0)
        running = int(svc.get("runningCount") or 0)
        pending = int(svc.get("pendingCount") or 0)
        deployments = svc.get("deployments") or []
        log(
            f"{name}: desired={desired} running={running} pending={pending} "
            f"deployments={len(deployments)}"
        )
        if desired != 0 or running != 0 or pending != 0:
            return False
    return True


def main() -> int:
    cluster = sys.argv[1] if len(sys.argv) > 1 else "rre-dev-cluster"
    services = sys.argv[2:] or ["rre-dev-api", "rre-dev-ui"]
    max_attempts = int(os.environ.get("ECS_CLEAR_MAX_ATTEMPTS", "40"))
    sleep_secs = int(os.environ.get("ECS_CLEAR_SLEEP_SECS", "15"))

    log(f"Clearing ECS services before deploy: cluster={cluster} services={services}")
    scale_to_zero(cluster, services)
    # Give the scheduler a moment, then force-stop so ALB targets drop quickly.
    time.sleep(5)
    stop_running_tasks(cluster, services)

    for attempt in range(1, max_attempts + 1):
        data = describe_services(cluster, services)
        if fully_drained(data):
            log("ECS services cleared (desired=0, no running/pending tasks)")
            return 0
        log(f"Waiting for clear... ({attempt}/{max_attempts})")
        time.sleep(sleep_secs)
        if attempt in (5, 15, 25):
            stop_running_tasks(cluster, services)

    print("::error::Timed out waiting for ECS clear before deploy", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
