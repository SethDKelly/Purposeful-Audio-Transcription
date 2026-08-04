"""ALB Lambda target: power-control login + OTP wake auth."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import os
import secrets
import time
import uuid
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

POWER_STATE_PK = "POWER#STATE"
OTP_TTL_MINUTES = 10
OTP_MAX_ATTEMPTS = 5
HANDOFF_TTL_SECONDS = 900

TABLE = os.environ["POWER_STATE_TABLE"]
REGION = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "us-east-2"
SES_FROM = (os.environ.get("SES_FROM_EMAIL") or "").strip()
HANDOFF_SECRET = (os.environ.get("POWER_HANDOFF_SECRET") or "dev-handoff").encode()
CODEBUILD_PROJECT = (os.environ.get("CODEBUILD_PROJECT_NAME") or "").strip()

_ddb = boto3.resource("dynamodb", region_name=REGION)
_table = _ddb.Table(TABLE)
_ses = boto3.client("ses", region_name=REGION)
_codebuild = boto3.client("codebuild", region_name=REGION)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _iso(dt: datetime | None = None) -> str:
    value = dt or _utc_now()
    return value.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


def _hash_secret(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _response(
    status: int,
    body: str | dict | list,
    *,
    content_type: str | None = None,
) -> dict[str, Any]:
    if isinstance(body, (dict, list)):
        payload = json.dumps(body, separators=(",", ":"))
        ctype = content_type or "application/json"
    else:
        payload = body
        ctype = content_type or "text/html; charset=utf-8"
    descriptions = {
        200: "200 OK",
        400: "400 Bad Request",
        401: "401 Unauthorized",
        404: "404 Not Found",
        405: "405 Method Not Allowed",
        500: "500 Internal Server Error",
    }
    return {
        "statusCode": status,
        "statusDescription": descriptions.get(status, f"{status} OK"),
        "headers": {
            "Content-Type": ctype,
            "Cache-Control": "no-store",
        },
        "body": payload,
        "isBase64Encoded": False,
    }


def _json_body(event: dict[str, Any]) -> dict[str, Any]:
    raw = event.get("body") or ""
    if event.get("isBase64Encoded"):
        raw = base64.b64decode(raw).decode("utf-8")
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # ALB may forward form-encoded bodies
        parsed = parse_qs(raw, keep_blank_values=True)
        return {k: (v[0] if len(v) == 1 else v) for k, v in parsed.items()}
    return data if isinstance(data, dict) else {}


def _get_power_state() -> dict[str, Any]:
    resp = _table.get_item(Key={"pk": POWER_STATE_PK})
    item = resp.get("Item") or {}
    if not item:
        return {
            "pk": POWER_STATE_PK,
            "state": "asleep",
            "last_activity_at": None,
            "idle_timer_started_at": None,
            "active_jobs": 0,
            "wake_requested_at": None,
        }
    return item


def _put_power_state(item: dict[str, Any]) -> None:
    item = {**item, "pk": POWER_STATE_PK}
    _table.put_item(Item=item)


def _mint_handoff_token(*, user_id: str, email: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": int(time.time()) + HANDOFF_TTL_SECONDS,
        "nonce": uuid.uuid4().hex,
    }
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    sig = hmac.new(HANDOFF_SECRET, body.encode(), hashlib.sha256).hexdigest()
    raw = f"{body}.{sig}"
    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")


def _parse_handoff_token(token: str) -> dict[str, Any]:
    pad = "=" * (-len(token) % 4)
    raw = base64.urlsafe_b64decode(token + pad).decode()
    body, sig = raw.rsplit(".", 1)
    expected = hmac.new(HANDOFF_SECRET, body.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        raise ValueError("Invalid handoff signature")
    payload = json.loads(body)
    if int(payload.get("exp", 0)) < int(time.time()):
        raise ValueError("Handoff token expired")
    return payload


def _start_codebuild(mode: str) -> None:
    if not CODEBUILD_PROJECT:
        logger.warning("CODEBUILD_PROJECT_NAME unset; skip start_build mode=%s", mode)
        return
    _codebuild.start_build(
        projectName=CODEBUILD_PROJECT,
        environmentVariablesOverride=[
            {"name": "POWER_MODE", "value": mode, "type": "PLAINTEXT"},
        ],
    )
    logger.info("Started CodeBuild %s mode=%s", CODEBUILD_PROJECT, mode)


def _set_waking() -> dict[str, Any]:
    item = _get_power_state()
    state = str(item.get("state") or "asleep")
    if state in {"awake", "waking"}:
        return item
    item["state"] = "waking"
    item["wake_requested_at"] = _iso()
    item["idle_timer_started_at"] = None
    _put_power_state(item)
    return item


LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>RRE — Wake / Sign in</title>
<style>
  :root { color-scheme: light; --fg:#1a1a1a; --muted:#5c5c5c; --bg:#f7f5f2; --accent:#2c5f4e; --line:#d8d2c8; }
  * { box-sizing: border-box; }
  body { margin:0; font-family: Georgia, "Times New Roman", serif; background: linear-gradient(160deg,#f7f5f2 0%,#ebe6dc 55%,#dfe8e3 100%); color:var(--fg); min-height:100vh; display:grid; place-items:center; padding:1.5rem; }
  main { width:min(420px,100%); }
  h1 { font-size:1.75rem; font-weight:600; margin:0 0 .35rem; letter-spacing:-.02em; }
  p.lead { margin:0 0 1.25rem; color:var(--muted); font-size:.95rem; }
  label { display:block; font-size:.8rem; margin:0 0 .35rem; color:var(--muted); }
  input { width:100%; padding:.65rem .75rem; border:1px solid var(--line); border-radius:4px; font:inherit; background:#fff; margin-bottom:.85rem; }
  button { width:100%; padding:.7rem; border:0; border-radius:4px; background:var(--accent); color:#fff; font:inherit; cursor:pointer; }
  button:disabled { opacity:.55; cursor:default; }
  button.secondary { background:transparent; color:var(--accent); border:1px solid var(--accent); margin-top:.5rem; }
  .msg { min-height:1.25rem; margin:.75rem 0 0; font-size:.9rem; color:var(--muted); }
  .status { margin-top:1rem; padding:.75rem; border-top:1px solid var(--line); font-size:.85rem; color:var(--muted); }
  #code-block { display:none; }
</style>
</head>
<body>
<main>
  <h1>Purposeful Audio</h1>
  <p class="lead">Sign in to wake the environment.</p>
  <form id="email-form">
    <label for="email">Email</label>
    <input id="email" name="email" type="email" autocomplete="username" required/>
    <button type="submit" id="request-btn">Send code</button>
  </form>
  <form id="code-block">
    <label for="code">One-time code</label>
    <input id="code" name="code" inputmode="numeric" autocomplete="one-time-code" required/>
    <button type="submit" id="verify-btn">Verify &amp; wake</button>
  </form>
  <p class="msg" id="msg"></p>
  <div class="status" id="status">Checking power status…</div>
</main>
<script>
const msg = document.getElementById('msg');
const statusEl = document.getElementById('status');
let handoff = sessionStorage.getItem('handoff_token') || '';
let pollTimer = null;

async function getStatus() {
  const r = await fetch('/api/v1/ops/power/status');
  return r.json();
}

function renderStatus(s) {
  const state = s.state || 'unknown';
  statusEl.textContent = 'Power: ' + state + (s.active_jobs != null ? ' · jobs ' + s.active_jobs : '');
  if (state === 'awake' && handoff) {
    const u = new URL('/', location.origin);
    u.searchParams.set('handoff', handoff);
    location.href = u.toString();
  }
}

async function poll() {
  try { renderStatus(await getStatus()); } catch (e) { statusEl.textContent = 'Status unavailable'; }
}

document.getElementById('email-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  msg.textContent = '';
  const email = document.getElementById('email').value.trim();
  const btn = document.getElementById('request-btn');
  btn.disabled = true;
  try {
    const r = await fetch('/api/v1/ops/power/auth/request-code', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({email})
    });
    const data = await r.json();
    msg.textContent = data.message || 'If that account exists, a code was sent.';
    document.getElementById('code-block').style.display = 'block';
  } catch (err) {
    msg.textContent = 'Could not request code.';
  } finally { btn.disabled = false; }
});

document.getElementById('code-block').addEventListener('submit', async (e) => {
  e.preventDefault();
  msg.textContent = '';
  const email = document.getElementById('email').value.trim();
  const code = document.getElementById('code').value.trim();
  const btn = document.getElementById('verify-btn');
  btn.disabled = true;
  try {
    const r = await fetch('/api/v1/ops/power/auth/verify-code', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({email, code})
    });
    const data = await r.json();
    if (!r.ok) { msg.textContent = data.detail || data.message || 'Verification failed'; return; }
    handoff = data.handoff_token || '';
    if (handoff) sessionStorage.setItem('handoff_token', handoff);
    msg.textContent = 'Verified. Waking environment…';
    renderStatus(data);
    if (!pollTimer) pollTimer = setInterval(poll, 5000);
  } catch (err) {
    msg.textContent = 'Verification failed.';
  } finally { btn.disabled = false; }
});

poll();
setInterval(poll, 8000);
</script>
</body>
</html>
"""


def handle_login(_event: dict[str, Any]) -> dict[str, Any]:
    return _response(200, LOGIN_HTML)


def handle_status(_event: dict[str, Any]) -> dict[str, Any]:
    item = _get_power_state()
    return _response(
        200,
        {
            "state": item.get("state") or "asleep",
            "last_activity_at": item.get("last_activity_at"),
            "idle_timer_started_at": item.get("idle_timer_started_at"),
            "active_jobs": int(item.get("active_jobs") or 0),
            "wake_requested_at": item.get("wake_requested_at"),
        },
    )


def handle_request_code(event: dict[str, Any]) -> dict[str, Any]:
    body = _json_body(event)
    email = _normalize_email(str(body.get("email") or ""))
    generic = {
        "status": "ok",
        "message": "If that account exists, a code was sent.",
    }
    if "@" not in email or "." not in email.split("@")[-1]:
        return _response(200, generic)

    user = _table.get_item(Key={"pk": f"USER#{email}"}).get("Item")
    if not user or not user.get("is_active"):
        logger.info("request-code skipped email=%s", email)
        return _response(200, generic)

    code = f"{secrets.randbelow(1_000_000):06d}"
    expires_ts = int(time.time()) + OTP_TTL_MINUTES * 60
    _table.put_item(
        Item={
            "pk": f"OTP#{email}",
            "code_hash": _hash_secret(code),
            "expires_at": _iso(
                datetime.fromtimestamp(expires_ts, tz=timezone.utc).replace(tzinfo=None)
            ),
            "attempt_count": 0,
            "ttl": expires_ts,
        }
    )

    if not SES_FROM:
        logger.error("SES_FROM_EMAIL unset; cannot send OTP")
        return _response(500, {"detail": "Email delivery not configured"})

    _ses.send_email(
        Source=SES_FROM,
        Destination={"ToAddresses": [email]},
        Message={
            "Subject": {"Data": "Your RRE wake code", "Charset": "UTF-8"},
            "Body": {
                "Text": {
                    "Data": (
                        f"Your one-time wake code is: {code}\n\n"
                        f"It expires in {OTP_TTL_MINUTES} minutes.\n"
                        "If you did not request this, ignore this email.\n"
                    ),
                    "Charset": "UTF-8",
                }
            },
        },
    )
    logger.info("OTP sent email=%s", email)
    return _response(200, generic)


def handle_verify_code(event: dict[str, Any]) -> dict[str, Any]:
    body = _json_body(event)
    email = _normalize_email(str(body.get("email") or ""))
    code = str(body.get("code") or "").strip()
    if len(code) < 4 or "@" not in email:
        return _response(400, {"detail": "Invalid email or code"})

    otp = _table.get_item(Key={"pk": f"OTP#{email}"}).get("Item")
    if not otp:
        return _response(401, {"detail": "Invalid or expired login code"})

    try:
        exp = datetime.fromisoformat(str(otp["expires_at"]).replace("Z", "+00:00"))
        if exp.tzinfo is not None:
            exp = exp.astimezone(timezone.utc).replace(tzinfo=None)
    except (KeyError, ValueError):
        return _response(401, {"detail": "Invalid or expired login code"})

    if exp < _utc_now():
        return _response(401, {"detail": "Login code has expired"})

    attempts = int(otp.get("attempt_count") or 0)
    if attempts >= OTP_MAX_ATTEMPTS:
        return _response(401, {"detail": "Login code locked after too many attempts"})

    if not secrets.compare_digest(str(otp.get("code_hash") or ""), _hash_secret(code)):
        otp["attempt_count"] = attempts + 1
        _table.put_item(Item=otp)
        return _response(401, {"detail": "Invalid or expired login code"})

    _table.delete_item(Key={"pk": f"OTP#{email}"})

    user = _table.get_item(Key={"pk": f"USER#{email}"}).get("Item")
    if not user or not user.get("is_active"):
        return _response(401, {"detail": "Account is not registered"})

    user_id = str(user.get("user_id") or "")
    token = _mint_handoff_token(user_id=user_id, email=email)
    item = _set_waking()
    try:
        _start_codebuild("wake")
    except Exception:
        logger.exception("CodeBuild start failed after verify")
        return _response(500, {"detail": "Failed to start wake"})

    return _response(
        200,
        {
            "status": item.get("state") or "waking",
            "handoff_token": token,
            "user": {
                "id": user_id,
                "email": email,
                "display_name": user.get("display_name"),
                "is_admin": bool(user.get("is_admin")),
            },
        },
    )


def handle_wake(event: dict[str, Any]) -> dict[str, Any]:
    """Idempotent wake; optional handoff token from a prior verify."""
    body = _json_body(event)
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    token = (
        str(body.get("handoff_token") or body.get("token") or "").strip()
        or (headers.get("authorization") or "").removeprefix("Bearer ").strip()
    )
    if token:
        try:
            _parse_handoff_token(token)
        except ValueError as exc:
            return _response(401, {"detail": str(exc)})

    item = _get_power_state()
    state = str(item.get("state") or "asleep")
    if state in {"awake", "waking"}:
        return _response(200, {"status": state, "message": "already in progress"})

    item = _set_waking()
    try:
        _start_codebuild("wake")
    except Exception:
        logger.exception("CodeBuild start failed on wake")
        return _response(500, {"detail": "Failed to start wake"})
    return _response(200, {"status": item.get("state") or "waking"})


ROUTES = {
    ("GET", "/login"): handle_login,
    ("GET", "/api/v1/ops/power/status"): handle_status,
    ("POST", "/api/v1/ops/power/auth/request-code"): handle_request_code,
    ("POST", "/api/v1/ops/power/auth/verify-code"): handle_verify_code,
    ("POST", "/api/v1/ops/power/wake"): handle_wake,
}


def handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    method = (event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method") or "GET").upper()
    path = event.get("path") or event.get("rawPath") or "/"
    # Strip trailing slash except root
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    route = ROUTES.get((method, path))
    if route is None:
        # Allow /login/ for ALB path patterns
        if method == "GET" and path.startswith("/login"):
            return handle_login(event)
        return _response(404, {"detail": "Not found"})

    try:
        return route(event)
    except Exception:
        logger.exception("Unhandled error method=%s path=%s", method, path)
        return _response(500, {"detail": "Internal server error"})
