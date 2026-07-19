#!/usr/bin/env bash
# Post-deploy smoke beyond GET /api/health.
# Expects AWS CLI credentials and terraform outputs from infra/dev.
# Respects DEPLOY_COMPONENT=all|api|ui|worker (default: all).
set -euo pipefail

TF_DIR="${TF_WORKING_DIR:-infra/dev}"
CLUSTER="${ECS_CLUSTER:-rre-dev-cluster}"
API_SERVICE="${ECS_API_SERVICE:-rre-dev-api}"
UI_SERVICE="${ECS_UI_SERVICE:-rre-dev-ui}"
WORKER_SERVICE="${ECS_WORKER_SERVICE:-rre-dev-worker}"
DEPLOY_COMPONENT="${DEPLOY_COMPONENT:-all}"
MAX_ATTEMPTS="${SMOKE_MAX_ATTEMPTS:-10}"
SLEEP_SECS="${SMOKE_SLEEP_SECS:-30}"

cd "$TF_DIR"
ALB_URL=$(terraform output -raw alb_url)
API_TG=$(terraform output -raw api_target_group_arn)
UI_TG=$(terraform output -raw ui_target_group_arn)
API_LOG_GROUP=$(terraform output -raw api_log_group)
UI_LOG_GROUP=$(terraform output -raw ui_log_group)
WORKER_LOG_GROUP=$(terraform output -raw worker_log_group 2>/dev/null || true)
NO_EGRESS=$(terraform output -raw no_egress_networking_enabled)

need_api=0
need_ui=0
need_worker=0
case "$DEPLOY_COMPONENT" in
  all) need_api=1; need_ui=1; need_worker=1 ;;
  api) need_api=1 ;;
  ui) need_ui=1 ;;
  worker) need_worker=1 ;;
  *)
    echo "::error::Unknown DEPLOY_COMPONENT=$DEPLOY_COMPONENT (expected all|api|ui|worker)"
    exit 1
    ;;
esac

echo "ALB URL: $ALB_URL"
echo "no_egress_networking: $NO_EGRESS"
echo "deploy_component: $DEPLOY_COMPONENT"

wait_http() {
  local path="$1"
  local label="$2"
  local i
  for i in $(seq 1 "$MAX_ATTEMPTS"); do
    if curl -sf --max-time 20 "${ALB_URL}${path}" >/tmp/rre-smoke-body.json; then
      echo "$label OK (${path})"
      return 0
    fi
    echo "Waiting for ${label}... ($i/$MAX_ATTEMPTS)"
    sleep "$SLEEP_SECS"
  done
  echo "::error::${label} failed after ${MAX_ATTEMPTS} attempts: ${ALB_URL}${path}"
  return 1
}

API_KEY_HEADER=()
if [ "$need_api" = "1" ] || [ "$need_ui" = "1" ]; then
  API_KEY_SECRET_ARN=$(terraform output -raw api_key_secret_arn 2>/dev/null || true)
  if [ -n "${API_KEY_SECRET_ARN}" ] && [ "${API_KEY_SECRET_ARN}" != "None" ]; then
    API_KEY=$(aws secretsmanager get-secret-value --secret-id "$API_KEY_SECRET_ARN" \
      --query 'SecretString' --output text | python3 -c 'import json,sys; print(json.load(sys.stdin).get("api_key",""))')
    if [ -n "$API_KEY" ]; then
      API_KEY_HEADER=(-H "X-API-Key: ${API_KEY}")
      echo "Using API key from Secrets Manager for authenticated smoke checks"
    fi
  fi
fi

wait_http_auth() {
  local path="$1"
  local label="$2"
  local i
  for i in $(seq 1 "$MAX_ATTEMPTS"); do
    if curl -sf --max-time 60 "${API_KEY_HEADER[@]}" "${ALB_URL}${path}" >/tmp/rre-smoke-body.json; then
      echo "$label OK (${path})"
      return 0
    fi
    echo "Waiting for ${label}... ($i/$MAX_ATTEMPTS)"
    sleep "$SLEEP_SECS"
  done
  echo "::error::${label} failed after ${MAX_ATTEMPTS} attempts: ${ALB_URL}${path}"
  return 1
}

if [ "$need_api" = "1" ] || [ "$need_ui" = "1" ]; then
  echo "== HTTP checks =="
  # ALB / ECS use /api/live; full /api/health can be slow while Bedrock warms.
  # UI-only deploys still require a live API behind the ALB.
  wait_http "/api/live" "API live"
fi

if [ "$need_api" = "1" ]; then
  wait_http_auth "/api/health" "API health"

  python3 - <<'PY'
import json, sys
with open("/tmp/rre-smoke-body.json", encoding="utf-8") as f:
    h = json.load(f)
errors = []
if h.get("status") != "ok":
    errors.append(f"status={h.get('status')!r}")
if h.get("llm_provider") != "bedrock":
    errors.append(f"llm_provider={h.get('llm_provider')!r} (expected bedrock)")
if h.get("llm_available") is not True:
    errors.append(f"llm_available={h.get('llm_available')!r}")
if h.get("database_available") is not True:
    errors.append(f"database_available={h.get('database_available')!r}")
if errors:
    print("Health payload failed:", "; ".join(errors), file=sys.stderr)
    print(json.dumps(h, indent=2), file=sys.stderr)
    sys.exit(1)
print(
    "Health payload OK:",
    f"llm_provider={h['llm_provider']}",
    f"llm_available={h['llm_available']}",
    f"database_available={h['database_available']}",
    f"diarization_ready={h.get('diarization_ready')}",
)
PY

  wait_http_auth "/api/workflows" "API workflows"
  python3 - <<'PY'
import json, sys
with open("/tmp/rre-smoke-body.json", encoding="utf-8") as f:
    body = json.load(f)
workflows = body.get("workflows") or []
ids = {w.get("id") for w in workflows}
if "quick_review" not in ids:
    print(f"workflows missing quick_review; got {sorted(ids)}", file=sys.stderr)
    sys.exit(1)
print(f"Workflows OK: {len(workflows)} listed (includes quick_review)")
PY

  wait_http_auth "/api/queue/stats" "API queue stats"
  python3 - <<'PY'
import json, sys
with open("/tmp/rre-smoke-body.json", encoding="utf-8") as f:
    body = json.load(f)
if "queue_depth" not in body:
    print("queue stats missing queue_depth", file=sys.stderr)
    sys.exit(1)
print(
    "Queue stats OK:",
    f"depth={body.get('queue_depth')}",
    f"running={body.get('running_count')}",
    f"oldest_age={body.get('oldest_queued_age_seconds')}",
)
PY
fi

if [ "$need_ui" = "1" ]; then
  wait_http "/_stcore/health" "UI health"
fi

echo "== ECS services =="
SERVICES=()
[ "$need_api" = "1" ] && SERVICES+=("$API_SERVICE")
[ "$need_ui" = "1" ] && SERVICES+=("$UI_SERVICE")
[ "$need_worker" = "1" ] && SERVICES+=("$WORKER_SERVICE")

SERVICES_JSON=$(aws ecs describe-services --cluster "$CLUSTER" --services "${SERVICES[@]}" --output json)
python3 - "$SERVICES_JSON" <<'PY'
import json, sys
data = json.loads(sys.argv[1])
failed = False
for svc in data.get("services", []):
    name = svc["serviceName"]
    desired = svc.get("desiredCount", 0)
    running = svc.get("runningCount", 0)
    pending = svc.get("pendingCount", 0)
    print(f"{name}: desired={desired} running={running} pending={pending}")
    if desired != running or pending:
        print(f"::error::{name} not stable (desired!=running or pending>0)", file=sys.stderr)
        failed = True
    for event in (svc.get("events") or [])[:5]:
        msg = event.get("message", "")
        if "CannotPullContainerError" in msg:
            print(f"::error::{name} recent CannotPullContainerError: {msg}", file=sys.stderr)
            failed = True
if failed:
    sys.exit(1)
PY

echo "== ALB target health =="
check_tg() {
  local arn="$1"
  local label="$2"
  local attempt
  for attempt in $(seq 1 6); do
    local health
    health=$(aws elbv2 describe-target-health --target-group-arn "$arn" --output json)
    if python3 - "$label" "$health" <<'PY'
import json, sys
label, raw = sys.argv[1], sys.argv[2]
data = json.loads(raw)
descs = data.get("TargetHealthDescriptions") or []
if not descs:
    print(f"::error::{label}: no registered targets", file=sys.stderr)
    sys.exit(2)

# Rolling deploys leave old tasks as "draining" while the new task is healthy.
# Pass when at least one target is healthy; ignore draining/initial.
healthy = []
transitional = []
bad = []
for d in descs:
    state = (d.get("TargetHealth") or {}).get("State") or "unknown"
    reason = (d.get("TargetHealth") or {}).get("Reason", "")
    target = (d.get("Target") or {}).get("Id", "?")
    print(f"{label}: {target} -> {state}" + (f" ({reason})" if reason else ""))
    if state == "healthy":
        healthy.append(target)
    elif state in ("draining", "initial"):
        transitional.append(f"{target}:{state}")
    else:
        bad.append(f"{target}:{state}")

if healthy:
    if transitional:
        print(f"{label}: OK ({len(healthy)} healthy; ignoring transitional {', '.join(transitional)})")
    elif bad:
        # Unhealthy siblings during replace — still OK if traffic has a healthy target.
        print(f"{label}: OK ({len(healthy)} healthy; other states: {', '.join(bad)})")
    else:
        print(f"{label}: OK ({len(healthy)} healthy)")
    sys.exit(0)

if transitional and not bad:
    print(f"{label}: waiting for healthy target (transitional: {', '.join(transitional)})", file=sys.stderr)
    sys.exit(1)

print(
    f"::error::{label}: no healthy targets"
    + (f"; bad={', '.join(bad)}" if bad else "")
    + (f"; transitional={', '.join(transitional)}" if transitional else ""),
    file=sys.stderr,
)
sys.exit(2)
PY
    then
      return 0
    fi
    local rc=$?
    if [ "$rc" -eq 2 ]; then
      return 1
    fi
    echo "Waiting for ${label} healthy target... ($attempt/6)"
    sleep 15
  done
  echo "::error::${label}: no healthy targets after retries"
  return 1
}

if [ "$need_api" = "1" ]; then
  check_tg "$API_TG" "API TG"
fi
if [ "$need_ui" = "1" ]; then
  check_tg "$UI_TG" "UI TG"
fi
if [ "$need_worker" = "1" ] && [ "$need_api" != "1" ] && [ "$need_ui" != "1" ]; then
  echo "Worker-only deploy: skipping ALB target groups (worker is not ALB-attached)"
fi

echo "== CloudWatch log groups =="
LOG_GROUPS=()
[ "$need_api" = "1" ] && LOG_GROUPS+=("$API_LOG_GROUP")
[ "$need_ui" = "1" ] && LOG_GROUPS+=("$UI_LOG_GROUP")
if [ "$need_worker" = "1" ] && [ -n "${WORKER_LOG_GROUP}" ] && [ "${WORKER_LOG_GROUP}" != "None" ]; then
  LOG_GROUPS+=("$WORKER_LOG_GROUP")
fi
for group in "${LOG_GROUPS[@]}"; do
  streams=$(aws logs describe-log-streams --log-group-name "$group" --order-by LastEventTime --descending --max-items 1 \
    --query 'logStreams[0].logStreamName' --output text 2>/dev/null || true)
  if [ -z "$streams" ] || [ "$streams" = "None" ]; then
    echo "::warning::No recent log streams in $group (new deploy may still be flushing)"
  else
    echo "$group: recent stream $streams"
  fi
done

echo "AWS-3f smoke passed (component=$DEPLOY_COMPONENT)"
