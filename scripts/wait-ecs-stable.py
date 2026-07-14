#!/usr/bin/env python3
"""Poll ECS until services are steady (desired==running, pending==0, one deployment)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time


def log(msg: str) -> None:
    print(msg, flush=True)


def describe_services(cluster: str, services: list[str]) -> dict:
    result = subprocess.run(
        [
            "aws",
            "ecs",
            "describe-services",
            "--cluster",
            cluster,
            "--services",
            *services,
            "--output",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def is_stable(data: dict) -> tuple[bool, bool]:
    """Return (stable, failed_rollout)."""
    ok = True
    failed = False
    for svc in data.get("services", []):
        name = svc["serviceName"]
        desired = int(svc.get("desiredCount") or 0)
        running = int(svc.get("runningCount") or 0)
        pending = int(svc.get("pendingCount") or 0)
        deployments = svc.get("deployments") or []
        primary = next((d for d in deployments if d.get("status") == "PRIMARY"), None)
        rollout = (primary or {}).get("rolloutState", "n/a")
        log(
            f"{name}: desired={desired} running={running} pending={pending} "
            f"deployments={len(deployments)} rollout={rollout}"
        )
        if rollout == "FAILED":
            failed = True
        if desired != running or pending != 0 or len(deployments) != 1:
            ok = False
        elif rollout not in ("COMPLETED", "n/a"):
            # Single deployment still rolling out.
            ok = False
    return ok, failed


def task_arns_from_list_output(raw: str) -> list[str]:
    """Parse list-tasks text output; drop pagination tokens and junk."""
    arns: list[str] = []
    for token in (raw or "").split():
        if token.startswith("arn:aws:ecs:") and ":task/" in token:
            arns.append(token)
    return arns


def dump_failure(cluster: str, services: list[str]) -> None:
    print("::error::ECS services did not stabilize", file=sys.stderr, flush=True)
    data = describe_services(cluster, services)
    summary = []
    for svc in data.get("services", []):
        summary.append(
            {
                "name": svc.get("serviceName"),
                "running": svc.get("runningCount"),
                "desired": svc.get("desiredCount"),
                "pending": svc.get("pendingCount"),
                "events": (svc.get("events") or [])[:8],
            }
        )
    log(json.dumps(summary, indent=2, default=str))
    for svc in services:
        stopped = subprocess.run(
            [
                "aws",
                "ecs",
                "list-tasks",
                "--cluster",
                cluster,
                "--service-name",
                svc,
                "--desired-status",
                "STOPPED",
                "--max-items",
                "3",
                "--query",
                "taskArns",
                "--output",
                "text",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        arns = task_arns_from_list_output(stopped.stdout or "")
        if not arns:
            continue
        log(f"--- Stopped tasks for {svc} ---")
        detail = subprocess.run(
            [
                "aws",
                "ecs",
                "describe-tasks",
                "--cluster",
                cluster,
                "--tasks",
                *arns,
                "--query",
                "tasks[].{task:taskArn,stoppedReason:stoppedReason,"
                "containers:containers[].{name:name,exitCode:exitCode,reason:reason}}",
                "--output",
                "json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        log(detail.stdout or detail.stderr or "")


def main() -> int:
    cluster = sys.argv[1] if len(sys.argv) > 1 else "rre-dev-cluster"
    services = sys.argv[2:] or ["rre-dev-api", "rre-dev-ui"]
    max_attempts = int(os.environ.get("ECS_WAIT_MAX_ATTEMPTS", "40"))
    sleep_secs = int(os.environ.get("ECS_WAIT_SLEEP_SECS", "30"))

    for attempt in range(1, max_attempts + 1):
        data = describe_services(cluster, services)
        stable, failed = is_stable(data)
        if failed:
            print("::error::ECS deployment rollout FAILED", file=sys.stderr, flush=True)
            dump_failure(cluster, services)
            return 1
        if stable:
            log("ECS services stable")
            return 0
        log(f"Waiting for ECS steady state... ({attempt}/{max_attempts})")
        time.sleep(sleep_secs)

    dump_failure(cluster, services)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
