"""EventBridge scheduled idle checker — sleep the stack when API reports idle."""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from typing import Any

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

POWER_STATE_PK = "POWER#STATE"

TABLE = os.environ["POWER_STATE_TABLE"]
REGION = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "us-east-2"
API_BASE_URL = (os.environ.get("API_BASE_URL") or "").rstrip("/")
API_KEY = (os.environ.get("API_KEY") or "").strip()
CODEBUILD_PROJECT = (os.environ.get("CODEBUILD_PROJECT_NAME") or "").strip()

_ddb = boto3.resource("dynamodb", region_name=REGION)
_table = _ddb.Table(TABLE)
_codebuild = boto3.client("codebuild", region_name=REGION)


def _get_state() -> dict[str, Any]:
    resp = _table.get_item(Key={"pk": POWER_STATE_PK})
    return resp.get("Item") or {}


def _fetch_idle_status() -> dict[str, Any] | None:
    if not API_BASE_URL or not API_KEY:
        logger.warning("API_BASE_URL or API_KEY unset")
        return None
    url = f"{API_BASE_URL}/api/v1/ops/power/idle-status"
    req = urllib.request.Request(
        url,
        headers={"X-API-Key": API_KEY, "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        logger.info("API unreachable or idle-status failed: %s", exc)
        return None


def _start_sleep() -> None:
    if not CODEBUILD_PROJECT:
        logger.error("CODEBUILD_PROJECT_NAME unset; cannot sleep")
        return
    _codebuild.start_build(
        projectName=CODEBUILD_PROJECT,
        environmentVariablesOverride=[
            {"name": "POWER_MODE", "value": "sleep", "type": "PLAINTEXT"},
        ],
    )
    logger.info("Started CodeBuild sleep project=%s", CODEBUILD_PROJECT)


def handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    item = _get_state()
    state = str(item.get("state") or "asleep")
    if state != "awake":
        logger.info("Skip idle check; state=%s", state)
        return {"skipped": True, "reason": "not_awake", "state": state}

    idle = _fetch_idle_status()
    if idle is None:
        # Treat unreachable API as already asleep / not ready to decide.
        return {"skipped": True, "reason": "api_unreachable"}

    if not idle.get("should_sleep"):
        return {
            "skipped": True,
            "reason": "not_idle",
            "idle_for_seconds": idle.get("idle_for_seconds"),
            "active_jobs": idle.get("active_jobs"),
        }

    item["state"] = "sleeping"
    _table.put_item(Item={**item, "pk": POWER_STATE_PK})
    _start_sleep()
    return {"started_sleep": True}
