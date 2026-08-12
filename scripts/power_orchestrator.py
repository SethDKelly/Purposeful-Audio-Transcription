#!/usr/bin/env python3
"""Wake / sleep RRE AWS dev via boto3 (ECS, RDS, VPC endpoints, DynamoDB).

Used by CodeBuild project rre-dev-power-orchestrator. Prefer AWS APIs over
terraform apply inside CodeBuild to avoid remote-state locking. Temporary
drift of VPC endpoints vs infra/dev is expected: the next deploy-dev
terraform apply (enable_vpc_endpoints=true) reconciles TF-managed endpoints.

Usage:
  python power_orchestrator.py wake|sleep|wake-infra
"""

from __future__ import annotations

import os
import sys
import time
from datetime import UTC, datetime
from typing import Any

import boto3

NAME = os.environ.get("NAME_PREFIX", "rre-dev")
REGION = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "us-east-2"
CLUSTER = f"{NAME}-cluster"
RDS_ID = os.environ.get("RDS_INSTANCE_ID", f"{NAME}-postgres")
TABLE = os.environ.get("POWER_STATE_TABLE", f"{NAME}-power-state")
POWER_STATE_PK = "POWER#STATE"
VPC_TAG_PROJECT = "rre"

INTERFACE_SERVICES = [
    "bedrock-runtime",
    "bedrock",
    "transcribe",
    "secretsmanager",
    "logs",
    "ecr.api",
    "ecr.dkr",
    "sts",
    "monitoring",
]

ECS_SERVICES = ("api", "ui", "worker")


def _iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _clients() -> dict[str, Any]:
    return {
        "ecs": boto3.client("ecs", region_name=REGION),
        "rds": boto3.client("rds", region_name=REGION),
        "ec2": boto3.client("ec2", region_name=REGION),
        "ddb": boto3.resource("dynamodb", region_name=REGION),
    }


def _default_vpc_id(ec2) -> str:
    resp = ec2.describe_vpcs(Filters=[{"Name": "isDefault", "Values": ["true"]}])
    vpcs = resp.get("Vpcs") or []
    if not vpcs:
        raise RuntimeError("No default VPC found")
    return vpcs[0]["VpcId"]


def _subnet_ids(ec2, vpc_id: str) -> list[str]:
    resp = ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])
    return [s["SubnetId"] for s in resp.get("Subnets") or []]


def _endpoint_sg_id(ec2, vpc_id: str) -> str | None:
    resp = ec2.describe_security_groups(
        Filters=[
            {"Name": "vpc-id", "Values": [vpc_id]},
            {"Name": "group-name", "Values": [f"{NAME}-vpc-endpoints"]},
        ]
    )
    groups = resp.get("SecurityGroups") or []
    return groups[0]["GroupId"] if groups else None


def _route_table_ids(ec2, vpc_id: str) -> list[str]:
    resp = ec2.describe_route_tables(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])
    return [rt["RouteTableId"] for rt in resp.get("RouteTables") or []]


def _set_power_state(ddb, state: str, **extra: Any) -> None:
    table = ddb.Table(TABLE)
    resp = table.get_item(Key={"pk": POWER_STATE_PK})
    item = dict(resp.get("Item") or {})
    item["pk"] = POWER_STATE_PK
    item["state"] = state
    item.update(extra)
    table.put_item(Item=item)
    print(f"DynamoDB {TABLE} state={state}", flush=True)


def _update_ecs_desired(ecs, desired: int) -> None:
    for svc in ECS_SERVICES:
        name = f"{NAME}-{svc}"
        try:
            ecs.update_service(cluster=CLUSTER, service=name, desiredCount=desired)
            print(f"ECS {name} desiredCount={desired}", flush=True)
        except Exception as exc:  # noqa: BLE001 — continue other services
            print(f"ECS update {name} failed: {exc}", flush=True)


def _wait_rds_available(rds) -> None:
    waiter = rds.get_waiter("db_instance_available")
    print(f"Waiting for RDS {RDS_ID} available...", flush=True)
    waiter.wait(
        DBInstanceIdentifier=RDS_ID,
        WaiterConfig={"Delay": 30, "MaxAttempts": 40},
    )


def _start_rds(rds) -> None:
    try:
        rds.start_db_instance(DBInstanceIdentifier=RDS_ID)
        print(f"RDS start requested: {RDS_ID}", flush=True)
    except Exception as exc:  # noqa: BLE001
        print(f"RDS start (may already be up): {exc}", flush=True)
    _wait_rds_available(rds)


def _stop_rds(rds) -> None:
    try:
        rds.stop_db_instance(DBInstanceIdentifier=RDS_ID)
        print(f"RDS stop requested: {RDS_ID}", flush=True)
    except Exception as exc:  # noqa: BLE001
        print(f"RDS stop (may already be stopped): {exc}", flush=True)


def _existing_endpoints(ec2, vpc_id: str) -> list[dict[str, Any]]:
    resp = ec2.describe_vpc_endpoints(
        Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
    )
    return list(resp.get("VpcEndpoints") or [])


def _endpoint_name(ep: dict[str, Any]) -> str:
    for tag in ep.get("Tags") or []:
        if tag.get("Key") == "Name":
            return str(tag.get("Value") or "")
    return ""


def _ensure_interface_endpoints(ec2) -> None:
    vpc_id = _default_vpc_id(ec2)
    subnet_ids = _subnet_ids(ec2, vpc_id)
    sg_id = _endpoint_sg_id(ec2, vpc_id)
    if not sg_id:
        raise RuntimeError(
            f"Security group {NAME}-vpc-endpoints not found; "
            "run terraform apply with enable_vpc_endpoints=true once first."
        )

    existing = _existing_endpoints(ec2, vpc_id)
    by_service = {
        ep.get("ServiceName"): ep
        for ep in existing
        if ep.get("VpcEndpointType") == "Interface"
        and ep.get("State") not in ("deleting", "deleted")
    }

    for short in INTERFACE_SERVICES:
        service_name = f"com.amazonaws.{REGION}.{short}"
        tag_name = f"{NAME}-{short.replace('.', '-')}"
        if service_name in by_service:
            print(f"Interface endpoint exists: {service_name}", flush=True)
            continue
        print(f"Creating interface endpoint: {service_name}", flush=True)
        ec2.create_vpc_endpoint(
            VpcId=vpc_id,
            ServiceName=service_name,
            VpcEndpointType="Interface",
            SubnetIds=subnet_ids,
            SecurityGroupIds=[sg_id],
            PrivateDnsEnabled=True,
            TagSpecifications=[
                {
                    "ResourceType": "vpc-endpoint",
                    "Tags": [
                        {"Key": "Name", "Value": tag_name},
                        {"Key": "Project", "Value": VPC_TAG_PROJECT},
                    ],
                }
            ],
        )


def _ensure_s3_gateway(ec2) -> None:
    vpc_id = _default_vpc_id(ec2)
    service_name = f"com.amazonaws.{REGION}.s3"
    existing = _existing_endpoints(ec2, vpc_id)
    for ep in existing:
        if (
            ep.get("VpcEndpointType") == "Gateway"
            and ep.get("ServiceName") == service_name
            and ep.get("State") not in ("deleting", "deleted")
        ):
            print(f"S3 gateway endpoint exists: {ep.get('VpcEndpointId')}", flush=True)
            return

    rt_ids = _route_table_ids(ec2, vpc_id)
    print(f"Creating S3 gateway endpoint on {len(rt_ids)} route tables", flush=True)
    ec2.create_vpc_endpoint(
        VpcId=vpc_id,
        ServiceName=service_name,
        VpcEndpointType="Gateway",
        RouteTableIds=rt_ids,
        TagSpecifications=[
            {
                "ResourceType": "vpc-endpoint",
                "Tags": [
                    {"Key": "Name", "Value": f"{NAME}-s3"},
                    {"Key": "Project", "Value": VPC_TAG_PROJECT},
                ],
            }
        ],
    )


def _ensure_dynamodb_gateway(ec2) -> None:
    vpc_id = _default_vpc_id(ec2)
    service_name = f"com.amazonaws.{REGION}.dynamodb"
    existing = _existing_endpoints(ec2, vpc_id)
    for ep in existing:
        if (
            ep.get("VpcEndpointType") == "Gateway"
            and ep.get("ServiceName") == service_name
            and ep.get("State") not in ("deleting", "deleted")
        ):
            print(f"DynamoDB gateway endpoint exists: {ep.get('VpcEndpointId')}", flush=True)
            return

    rt_ids = _route_table_ids(ec2, vpc_id)
    print(f"Creating DynamoDB gateway endpoint on {len(rt_ids)} route tables", flush=True)
    ec2.create_vpc_endpoint(
        VpcId=vpc_id,
        ServiceName=service_name,
        VpcEndpointType="Gateway",
        RouteTableIds=rt_ids,
        TagSpecifications=[
            {
                "ResourceType": "vpc-endpoint",
                "Tags": [
                    {"Key": "Name", "Value": f"{NAME}-dynamodb"},
                    {"Key": "Project", "Value": VPC_TAG_PROJECT},
                ],
            }
        ],
    )


def _ensure_network_infra(ec2) -> None:
    _ensure_s3_gateway(ec2)
    _ensure_dynamodb_gateway(ec2)
    _ensure_interface_endpoints(ec2)


def _delete_managed_endpoints(ec2) -> None:
    """Delete interface endpoints named rre-dev-* and S3 gateway named rre-dev-s3."""
    vpc_id = _default_vpc_id(ec2)
    to_delete: list[str] = []
    for ep in _existing_endpoints(ec2, vpc_id):
        name = _endpoint_name(ep)
        ep_id = ep.get("VpcEndpointId")
        if not ep_id or not name.startswith(f"{NAME}-"):
            continue
        if ep.get("VpcEndpointType") == "Interface":
            to_delete.append(ep_id)
        elif ep.get("VpcEndpointType") == "Gateway" and name == f"{NAME}-s3":
            to_delete.append(ep_id)

    if not to_delete:
        print("No tagged VPC endpoints to delete", flush=True)
        return

    print(f"Deleting VPC endpoints: {to_delete}", flush=True)
    for i in range(0, len(to_delete), 25):
        chunk = to_delete[i : i + 25]
        ec2.delete_vpc_endpoints(VpcEndpointIds=chunk)


def wake(clients: dict[str, Any]) -> None:
    print(f"MODE=wake region={REGION} name={NAME}", flush=True)
    _set_power_state(
        clients["ddb"],
        "waking",
        wake_requested_at=_iso(),
        idle_timer_started_at=None,
    )
    _start_rds(clients["rds"])
    _ensure_network_infra(clients["ec2"])
    # Brief pause so private DNS / ENIs settle before ECS tasks start.
    time.sleep(15)
    _update_ecs_desired(clients["ecs"], 1)
    _set_power_state(
        clients["ddb"],
        "awake",
        last_activity_at=_iso(),
        idle_timer_started_at=None,
        active_jobs=0,
        wake_requested_at=None,
    )
    print("Wake complete", flush=True)


def sleep(clients: dict[str, Any]) -> None:
    print(f"MODE=sleep region={REGION} name={NAME}", flush=True)
    _set_power_state(clients["ddb"], "sleeping")
    _update_ecs_desired(clients["ecs"], 0)
    # Allow tasks to drain briefly before cutting VPC endpoints.
    time.sleep(20)
    _delete_managed_endpoints(clients["ec2"])
    _stop_rds(clients["rds"])
    _set_power_state(
        clients["ddb"],
        "asleep",
        idle_timer_started_at=None,
        active_jobs=0,
    )
    print("Sleep complete", flush=True)


def wake_infra(clients: dict[str, Any]) -> None:
    """Restore VPC endpoints and mark awake without changing ECS desired counts."""
    print(f"MODE=wake-infra region={REGION} name={NAME}", flush=True)
    _ensure_network_infra(clients["ec2"])
    time.sleep(15)
    _set_power_state(
        clients["ddb"],
        "awake",
        last_activity_at=_iso(),
        idle_timer_started_at=None,
        active_jobs=0,
        wake_requested_at=None,
    )
    print("Wake-infra complete", flush=True)


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] not in ("wake", "sleep", "wake-infra"):
        print(
            "Usage: python power_orchestrator.py wake|sleep|wake-infra",
            file=sys.stderr,
        )
        return 2
    clients = _clients()
    if argv[1] == "wake":
        wake(clients)
    elif argv[1] == "wake-infra":
        wake_infra(clients)
    else:
        sleep(clients)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
