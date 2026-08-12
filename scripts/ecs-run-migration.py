#!/usr/bin/env python3
"""Run Alembic upgrade head in a one-off ECS task (same image/secrets as API)."""

from __future__ import annotations

import json
import subprocess
import sys
import time

MIGRATION_COMMAND = [
    "python",
    "-c",
    "from backend.db.migrations import upgrade_head; upgrade_head(); print('alembic upgrade head OK')",
]


def log(msg: str) -> None:
    print(msg, flush=True)


def run_aws(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["aws", *args],
        check=check,
        capture_output=True,
        text=True,
    )


def main() -> int:
    if len(sys.argv) != 3:
        log(f"Usage: {sys.argv[0]} <cluster> <api-service-name>")
        return 2

    cluster, service = sys.argv[1], sys.argv[2]
    desc = json.loads(
        run_aws(
            [
                "ecs",
                "describe-services",
                "--cluster",
                cluster,
                "--services",
                service,
                "--output",
                "json",
            ]
        ).stdout
    )
    svc = desc["services"][0]
    task_def = svc["taskDefinition"]
    net = svc["networkConfiguration"]["awsvpcConfiguration"]
    subnets = net["subnets"]
    security_groups = net["securityGroups"]
    assign_public_ip = net.get("assignPublicIp", "DISABLED")

    overrides = json.dumps(
        {"containerOverrides": [{"name": "api", "command": MIGRATION_COMMAND}]}
    )

    log(f"Running Alembic migration: cluster={cluster} taskDefinition={task_def}")
    run_result = json.loads(
        run_aws(
            [
                "ecs",
                "run-task",
                "--cluster",
                cluster,
                "--task-definition",
                task_def,
                "--launch-type",
                "FARGATE",
                "--network-configuration",
                (
                    f"awsvpcConfiguration={{subnets=[{','.join(subnets)}],"
                    f"securityGroups=[{','.join(security_groups)}],"
                    f"assignPublicIp={assign_public_ip}}}"
                ),
                "--overrides",
                overrides,
                "--output",
                "json",
            ]
        ).stdout
    )

    tasks = run_result.get("tasks") or []
    if not tasks:
        failures = run_result.get("failures") or []
        log(f"Migration task failed to start: {failures}")
        return 1

    task_arn = tasks[0]["taskArn"]
    task_id = task_arn.rsplit("/", 1)[-1]
    log(f"Migration task started: {task_id}")

    max_attempts = int(__import__("os").environ.get("ECS_MIGRATE_MAX_ATTEMPTS", "60"))
    sleep_secs = float(__import__("os").environ.get("ECS_MIGRATE_SLEEP_SECS", "5"))

    for attempt in range(1, max_attempts + 1):
        time.sleep(sleep_secs)
        task = json.loads(
            run_aws(
                [
                    "ecs",
                    "describe-tasks",
                    "--cluster",
                    cluster,
                    "--tasks",
                    task_arn,
                    "--output",
                    "json",
                ]
            ).stdout
        )["tasks"][0]
        last = task.get("lastStatus")
        if last != "STOPPED":
            log(f"Migration task {task_id}: status={last} (attempt {attempt}/{max_attempts})")
            continue

        containers = task.get("containers") or []
        exit_code = containers[0].get("exitCode") if containers else None
        reason = task.get("stoppedReason") or containers[0].get("reason") if containers else None
        if exit_code == 0:
            log(f"Migration task {task_id} completed successfully")
            return 0

        log(f"Migration task {task_id} failed: exitCode={exit_code} reason={reason}")
        return 1

    log(f"Migration task {task_id} timed out after {max_attempts} polls")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
