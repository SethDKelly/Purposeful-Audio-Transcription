#!/usr/bin/env python3
"""Force ECS services onto the latest task definition revision after terraform apply.

After an IAM task-role split, circuit-breaker rollback can leave a service
deploying a pre-split revision whose taskRoleArn (rre-dev-ecs-task) no longer
exists. Terraform registers new revisions but may not start a fresh deployment
while the service is rolled back — this script forces one.
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


def force_service(cluster: str, service: str) -> None:
    data = describe_services(cluster, [service])
    svcs = data.get("services") or []
    if not svcs or svcs[0].get("status") == "INACTIVE":
        log(f"{service}: inactive or missing; skip force deploy")
        return

    current_arn = (svcs[0].get("taskDefinition") or "").strip()
    role_arn = task_def_role_arn(current_arn) if current_arn else None
    if role_arn and role_arn.endswith(_LEGACY_TASK_ROLE_SUFFIX):
        log(
            f"{service}: current task def uses legacy role {role_arn}; "
            "forcing latest revision"
        )

    # Family name resolves to the newest ACTIVE revision for this stack.
    log(f"{service}: force-new-deployment (task-definition family={service})")
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

    log(f"Forcing ECS redeploy: cluster={cluster} services={services}")
    for name in services:
        force_service(cluster, name)
    log("ECS force deploy requested for all services")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
