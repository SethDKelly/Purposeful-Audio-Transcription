#!/usr/bin/env python3
"""Force ECS services onto the latest task definition after terraform apply.

Only runs when recovery is needed: legacy IAM task role, failed rollout, or a
stale task-definition revision. Skips the common case so we do not stack a
second deployment on top of terraform's own service update.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

_LEGACY_TASK_ROLE_SUFFIX = ":role/rre-dev-ecs-task"


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


def task_def_role_arn(task_def_arn: str) -> str | None:
    result = run_aws(
        [
            "ecs",
            "describe-task-definition",
            "--task-definition",
            task_def_arn,
            "--query",
            "taskDefinition.taskRoleArn",
            "--output",
            "text",
        ],
        check=False,
    )
    role = (result.stdout or "").strip()
    if result.returncode != 0 or role in ("", "None"):
        return None
    return role


def latest_task_def_arn(family: str) -> str:
    result = run_aws(
        [
            "ecs",
            "describe-task-definition",
            "--task-definition",
            family,
            "--query",
            "taskDefinition.taskDefinitionArn",
            "--output",
            "text",
        ]
    )
    return (result.stdout or "").strip()


def needs_force_deploy(service: str, svc: dict) -> tuple[bool, str]:
    current_arn = (svc.get("taskDefinition") or "").strip()
    if not current_arn:
        return False, "no task definition registered"

    latest_arn = latest_task_def_arn(service)
    if latest_arn and current_arn != latest_arn:
        return True, f"stale task def ({current_arn} -> {latest_arn})"

    role_arn = task_def_role_arn(current_arn)
    if role_arn and role_arn.endswith(_LEGACY_TASK_ROLE_SUFFIX):
        return True, f"legacy task role {role_arn}"

    for dep in svc.get("deployments") or []:
        if dep.get("rolloutState") == "FAILED":
            return True, "failed rollout on service"

    return False, "already on latest revision"


def force_service(cluster: str, service: str) -> None:
    data = describe_services(cluster, [service])
    svcs = data.get("services") or []
    if not svcs or svcs[0].get("status") == "INACTIVE":
        log(f"{service}: inactive or missing; skip force deploy")
        return

    svc = svcs[0]
    needed, reason = needs_force_deploy(service, svc)
    if not needed:
        log(f"{service}: skip force deploy ({reason})")
        return

    log(f"{service}: force-new-deployment ({reason})")
    run_aws(
        [
            "ecs",
            "update-service",
            "--cluster",
            cluster,
            "--service",
            service,
            "--task-definition",
            service,
            "--force-new-deployment",
            "--deployment-configuration",
            "minimumHealthyPercent=0,maximumPercent=200",
            "--no-cli-pager",
        ]
    )


def main() -> int:
    cluster = sys.argv[1] if len(sys.argv) > 1 else "rre-dev-cluster"
    services = sys.argv[2:] or ["rre-dev-api", "rre-dev-ui", "rre-dev-worker"]
    if os.environ.get("ECS_FORCE_DEPLOY") == "0":
        log("ECS_FORCE_DEPLOY=0; skipping force deploy")
        return 0

    log(f"Checking ECS services for force deploy: cluster={cluster} services={services}")
    for name in services:
        force_service(cluster, name)
    log("ECS force deploy check complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
