# AWS operations — RRE dev

CloudWatch log groups for the dev stack:

| Service | Log group |
|---------|-----------|
| API | `/rre/dev/api` |
| UI | `/rre/dev/ui` |

Structured JSON logs (`LOG_JSON=true`) include correlation fields:

| Field | Source |
|-------|--------|
| `request_id` | `X-Request-ID` header or generated per HTTP request |
| `workflow_run_id` | Active workflow run context |
| `module_run_id` | Active module run context |
| `module_id` | Module being executed |
| `error_type` | Exception class or failure category |
| `event` | Semantic event name (e.g. `module.run.failed`) |

## CloudWatch Logs Insights queries

Run in **Logs Insights** against `/rre/dev/api`.

### Failed module runs (last hour)

```text
fields @timestamp, module_id, error_type, workflow_run_id, module_run_id, message
| filter event = "module.run.failed"
| sort @timestamp desc
| limit 50
```

### JSON parse failures

```text
fields @timestamp, module_id, module_run_id, workflow_run_id, retry_count, message
| filter event = "module.run.parse_error"
| sort @timestamp desc
| limit 50
```

### Trace a request by ID

```text
fields @timestamp, event, module_id, workflow_run_id, module_run_id, error_type, message
| filter request_id = "YOUR-REQUEST-UUID"
| sort @timestamp asc
```

### Failed workflows

```text
fields @timestamp, workflow_id, run_id, error_type, message
| filter event = "workflow.run.failed"
| sort @timestamp desc
| limit 50
```

### LLM errors

```text
fields @timestamp, module_id, module_run_id, model_id, message
| filter error_type = "LLMError"
| sort @timestamp desc
| limit 50
```

## Bedrock dev settings

| Variable | ECS value (dev) |
|----------|-----------------|
| `LLM_PROVIDER` | `bedrock` |
| `BEDROCK_MODEL_ID` | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` |

Ensure the ECS task role includes Bedrock invoke + Marketplace subscribe-via-Bedrock (see `infra/dev/iam.tf`). Evaluation note: [llm-evaluation-bedrock.md](../planning/llm-evaluation-bedrock.md).

## Deploy wait pattern

After a push that rebuilds images / applies Terraform:

1. Wait **20 minutes**
2. Check health + ECS stability
3. If not ready, up to **three** rechecks at **2-minute** intervals

## Post-deploy smoke (AWS-3f checklist)

Beyond `GET /api/health`. Automated in CI via `scripts/aws-deploy-smoke.sh` after ECS is stable.

| Check | How |
|-------|-----|
| Health payload | `GET /api/health` — `status=ok`, `llm_provider=bedrock`, `llm_available=true`, `database_available=true` |
| ALB liveness | API TG uses `GET /api/live` (no Bedrock/HF); UI uses `/_stcore/health` |
| ALB → API | `http://<alb>/api/health` and `http://<alb>/api/workflows` (includes `quick_review`) |
| ALB → UI | `http://<alb>/_stcore/health` |
| ECS services | Desired == running; fail on recent `CannotPullContainerError` |
| Target groups | ≥1 **healthy** target per API/UI TG (`describe-target-health`; ignore `draining`/`initial` during roll) |
| Logs | Recent streams under `/rre/dev/api` and `/rre/dev/ui` (warn if missing) |
| Bedrock path | Optional manual: Quick Review on a short paste transcript |

Local (from repo root, with AWS + terraform state access):

```bash
./scripts/aws-deploy-smoke.sh
```

## Pause / resume (when idle)

**Standing practice:** If the AWS dev stack is not in active use (no deploy, burn-in, or demo in progress), pause it to avoid Fargate and RDS compute charges.

| Action | How |
|--------|-----|
| **Pause** | GitHub Actions → **Pause AWS dev** → Run workflow |
| **Resume** | GitHub Actions → **Deploy to AWS dev** → Run workflow (`workflow_dispatch`) |

Pause sets ECS desired count to **0** and stops RDS `rre-dev-postgres`. Full steps, residual costs (ALB, ECR, Secrets Manager, RDS storage), and CLI equivalents: [infra/dev/README.md](../../infra/dev/README.md).
