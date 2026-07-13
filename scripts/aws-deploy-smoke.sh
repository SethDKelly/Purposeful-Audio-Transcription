#!/usr/bin/env bash
# P0-AWS-3f â€” post-deploy smoke beyond GET /api/health.
# Expects AWS CLI credentials and terraform outputs from infra/dev.
set -euo pipefail

TF_DIR="${TF_WORKING_DIR:-infra/dev}"
CLUSTER="${ECS_CLUSTER:-rre-dev-cluster}"
API_SERVICE="${ECS_API_SERVICE:-rre-dev-api}"
UI_SERVICE="${ECS_UI_SERVICE:-rre-dev-ui}"
MAX_ATTEMPTS="${SMOKE_MAX_ATTEMPTS:-10}"
SLEEP_SECS="${SMOKE_SLEEP_SECS:-30}"

cd "$TF_DIR"
ALB_URL=$(terraform output -raw alb_url)
API_TG=$(terraform output -raw api_target_group_arn)
UI_TG=$(terraform output -raw ui_target_group_arn)
API_LOG_GROUP=$(terraform output -raw api_log_group)
UI_LOG_GROUP=$(terraform output -raw ui_log_group)
NO_EGRESS=$(terraform output -raw no_egress_networking_enabled)

echo "ALB URL: $ALB_URL"
echo "no_egress_networking: $NO_EGRESS"

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

echo "== HTTP checks =="
wait_http "/api/health" "API health"

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

wait_http "/api/workflows" "API workflows"
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

wait_http "/_stcore/health" "UI health"

echo "== ECS services =="
SERVICES_JSON=$(aws ecs describe-services --cluster "$CLUSTER" --services "$API_SERVICE" "$UI_SERVICE" --output json)
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
  local health
  health=$(aws elbv2 describe-target-health --target-group-arn "$arn" --output json)
  python3 - "$label" "$health" <<'PY'
import json, sys
label, raw = sys.argv[1], sys.argv[2]
data = json.loads(raw)
descs = data.get("TargetHealthDescriptions") or []
if not descs:
    print(f"::error::{label}: no registered targets", file=sys.stderr)
    sys.exit(1)
bad = []
for d in descs:
    state = (d.get("TargetHealth") or {}).get("State")
    reason = (d.get("TargetHealth") or {}).get("Reason", "")
    target = (d.get("Target") or {}).get("Id", "?")
    print(f"{label}: {target} -> {state}" + (f" ({reason})" if reason else ""))
    if state != "healthy":
        bad.append(f"{target}:{state}")
if bad:
    print(f"::error::{label} unhealthy targets: {', '.join(bad)}", file=sys.stderr)
    sys.exit(1)
PY
}

check_tg "$API_TG" "API TG"
check_tg "$UI_TG" "UI TG"

echo "== CloudWatch log groups =="
for group in "$API_LOG_GROUP" "$UI_LOG_GROUP"; do
  streams=$(aws logs describe-log-streams --log-group-name "$group" --order-by LastEventTime --descending --max-items 1 \
    --query 'logStreams[0].logStreamName' --output text 2>/dev/null || true)
  if [ -z "$streams" ] || [ "$streams" = "None" ]; then
    echo "::warning::No recent log streams in $group (new deploy may still be flushing)"
  else
    echo "$group: recent stream $streams"
  fi
done

echo "AWS-3f smoke passed"
