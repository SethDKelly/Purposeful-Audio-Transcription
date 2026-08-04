"""Power / idle control plane helpers (activity clock, DynamoDB state)."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from config.settings import settings

logger = logging.getLogger(__name__)

POWER_STATE_PK = "POWER#STATE"


def _utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _iso(dt: datetime | None = None) -> str:
    value = dt or _utc_now()
    return value.replace(tzinfo=UTC).isoformat().replace("+00:00", "Z")


@dataclass
class PowerStatus:
    state: str  # asleep | waking | awake | sleeping
    last_activity_at: str | None
    idle_timer_started_at: str | None
    active_jobs: int
    wake_requested_at: str | None = None
    message: str | None = None


class PowerStateStore:
    """DynamoDB-backed power state. No-ops when power control is disabled."""

    def __init__(self) -> None:
        self._table_name = (settings.power_state_table or "").strip()
        self._client = None

    @property
    def enabled(self) -> bool:
        return bool(settings.power_control_enabled and self._table_name)

    def _table(self):
        if self._client is None:
            import boto3

            self._client = boto3.resource(
                "dynamodb", region_name=settings.resolved_aws_region
            )
        return self._client.Table(self._table_name)

    def get_raw(self) -> dict[str, Any]:
        if not self.enabled:
            return {
                "pk": POWER_STATE_PK,
                "state": "awake",
                "last_activity_at": _iso(),
                "idle_timer_started_at": None,
                "active_jobs": 0,
            }
        resp = self._table().get_item(Key={"pk": POWER_STATE_PK})
        item = resp.get("Item") or {}
        if not item:
            return {
                "pk": POWER_STATE_PK,
                "state": "asleep",
                "last_activity_at": None,
                "idle_timer_started_at": None,
                "active_jobs": 0,
            }
        return item

    def put_raw(self, item: dict[str, Any]) -> None:
        if not self.enabled:
            return
        item = {**item, "pk": POWER_STATE_PK}
        self._table().put_item(Item=item)

    def touch_activity(self, *, reset_idle_timer: bool = True) -> None:
        if not self.enabled:
            return
        # Atomic attribute updates avoid lost writes vs idle-checker / set_active_jobs.
        expr = "SET last_activity_at = :la"
        values: dict[str, Any] = {":la": _iso()}
        if reset_idle_timer:
            expr += " REMOVE idle_timer_started_at"
        try:
            self._table().update_item(
                Key={"pk": POWER_STATE_PK},
                UpdateExpression=expr,
                ExpressionAttributeValues=values,
            )
        except Exception:  # noqa: BLE001
            # Table may be empty on first boot — fall back to put.
            item = self.get_raw()
            item["last_activity_at"] = values[":la"]
            if reset_idle_timer:
                item["idle_timer_started_at"] = None
            self.put_raw(item)

    def start_idle_timer(self) -> None:
        if not self.enabled:
            return
        now = _iso()
        try:
            self._table().update_item(
                Key={"pk": POWER_STATE_PK},
                UpdateExpression=(
                    "SET idle_timer_started_at = if_not_exists(idle_timer_started_at, :now), "
                    "last_activity_at = if_not_exists(last_activity_at, :now)"
                ),
                ExpressionAttributeValues={":now": now},
            )
        except Exception:  # noqa: BLE001
            item = self.get_raw()
            if not item.get("idle_timer_started_at"):
                item["idle_timer_started_at"] = now
                item["last_activity_at"] = item.get("last_activity_at") or now
                self.put_raw(item)

    def set_state(self, state: str, **extra: Any) -> None:
        if not self.enabled:
            return
        names: dict[str, str] = {"#s": "state"}
        values: dict[str, Any] = {":s": state}
        parts = ["#s = :s"]
        for idx, (key, value) in enumerate(extra.items()):
            # Allow only simple attribute keys (no path injection).
            if not str(key).replace("_", "").isalnum():
                continue
            nk = f"#k{idx}"
            vk = f":v{idx}"
            names[nk] = str(key)
            values[vk] = value
            parts.append(f"{nk} = {vk}")
        try:
            self._table().update_item(
                Key={"pk": POWER_STATE_PK},
                UpdateExpression="SET " + ", ".join(parts),
                ExpressionAttributeNames=names,
                ExpressionAttributeValues=values,
            )
        except Exception:  # noqa: BLE001
            item = self.get_raw()
            item["state"] = state
            item.update(extra)
            self.put_raw(item)

    def set_active_jobs(self, count: int) -> None:
        if not self.enabled:
            return
        try:
            self._table().update_item(
                Key={"pk": POWER_STATE_PK},
                UpdateExpression="SET active_jobs = :n",
                ExpressionAttributeValues={":n": int(count)},
            )
        except Exception:  # noqa: BLE001
            item = self.get_raw()
            item["active_jobs"] = int(count)
            self.put_raw(item)


power_state_store = PowerStateStore()


def mint_handoff_token(*, user_id: str, email: str, ttl_seconds: int = 900) -> str:
    secret = (settings.power_handoff_secret or settings.api_key or "dev-handoff").encode()
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": int(time.time()) + ttl_seconds,
        "nonce": uuid.uuid4().hex,
    }
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    sig = hmac.new(secret, body.encode(), hashlib.sha256).hexdigest()
    raw = f"{body}.{sig}"
    import base64

    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")


def parse_handoff_token(token: str) -> dict[str, Any]:
    import base64

    secret = (settings.power_handoff_secret or settings.api_key or "dev-handoff").encode()
    pad = "=" * (-len(token) % 4)
    raw = base64.urlsafe_b64decode(token + pad).decode()
    body, sig = raw.rsplit(".", 1)
    expected = hmac.new(secret, body.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        raise ValueError("Invalid handoff signature")
    payload = json.loads(body)
    if int(payload.get("exp", 0)) < int(time.time()):
        raise ValueError("Handoff token expired")
    return payload


# Process-local fallback when DynamoDB power control is disabled (pytest / local).
_consumed_handoff_nonces: set[str] = set()


def consume_handoff_nonce(nonce: str, *, ttl_seconds: int = 900) -> bool:
    """Mark a handoff nonce as used. Returns False on replay.

    When power control DynamoDB is enabled, uses a conditional PutItem so
    concurrent API tasks cannot both exchange the same wake token.
    """
    cleaned = (nonce or "").strip()
    if not cleaned:
        return False

    if power_state_store.enabled:
        try:
            from botocore.exceptions import ClientError

            table = power_state_store._table()
            expires = int(time.time()) + max(60, int(ttl_seconds))
            table.put_item(
                Item={
                    "pk": f"HANDOFF#{cleaned}",
                    "consumed_at": _iso(),
                    "ttl": expires,
                },
                ConditionExpression="attribute_not_exists(pk)",
            )
            return True
        except ClientError as exc:
            code = (exc.response or {}).get("Error", {}).get("Code", "")
            if code == "ConditionalCheckFailedException":
                return False
            logger.exception("Handoff nonce consume failed; rejecting token")
            return False
        except Exception:  # noqa: BLE001
            logger.exception("Handoff nonce consume failed; rejecting token")
            return False

    if cleaned in _consumed_handoff_nonces:
        return False
    _consumed_handoff_nonces.add(cleaned)
    return True


def count_active_jobs() -> int:
    from sqlalchemy import func, select

    from backend.db.base import get_session
    from backend.db.models import WorkflowRunRow

    active = {"created", "queued", "running", "pending"}
    with get_session() as session:
        n = session.scalar(
            select(func.count())
            .select_from(WorkflowRunRow)
            .where(WorkflowRunRow.status.in_(tuple(active)))
        )
        return int(n or 0)


def idle_status_payload() -> dict[str, Any]:
    raw = power_state_store.get_raw()
    active_jobs = count_active_jobs()
    if power_state_store.enabled:
        power_state_store.set_active_jobs(active_jobs)

    last_activity = raw.get("last_activity_at")
    idle_started = raw.get("idle_timer_started_at")
    state = str(raw.get("state") or "awake")

    idle_for = 0.0
    reference = idle_started or last_activity
    if reference:
        try:
            ref_dt = datetime.fromisoformat(str(reference).replace("Z", "+00:00"))
            if ref_dt.tzinfo is not None:
                ref_dt = ref_dt.astimezone(UTC).replace(tzinfo=None)
            idle_for = (_utc_now() - ref_dt).total_seconds()
        except ValueError:
            idle_for = 0.0

    should_sleep = (
        state == "awake"
        and active_jobs == 0
        and idle_for >= float(settings.idle_sleep_after_seconds)
    )
    return {
        "state": state,
        "active_jobs": active_jobs,
        "last_activity_at": last_activity,
        "idle_timer_started_at": idle_started,
        "idle_for_seconds": int(idle_for),
        "idle_sleep_after_seconds": int(settings.idle_sleep_after_seconds),
        "should_sleep": should_sleep,
        "kill_long_jobs_enabled": bool(settings.kill_long_jobs_enabled),
        "kill_long_jobs_seconds": int(settings.kill_long_jobs_seconds),
    }
