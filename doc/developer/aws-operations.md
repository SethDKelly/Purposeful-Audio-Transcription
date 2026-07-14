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

## Log redaction (what you will / won't see)

With `LOG_REDACT` auto-on for Bedrock / PostgreSQL (or `LOG_REDACT=true`):

| You **will** see | You **won't** see |
|------------------|-------------------|
| `request_id`, `workflow_run_id`, `module_run_id`, `module_id` | Transcript / turn bodies |
| `error_type`, `event`, counts (`turn_count`, `quote_count`) | Prompt payloads / compiled messages |
| Status, duration, model id | Full LLM completions (`raw_output`) |
| Audit events: `transcript.ingest`, `.export`, `.delete`, `.purge` | Secrets (`DATABASE_URL`, tokens) |

DB remains the store of record. Prefer Insights queries by ID, not free-text search on dialogue.

Design: [log-redaction.md](../planning/log-redaction.md).

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

### Audit events (ingest / export / delete)

```text
fields @timestamp, event, transcript_id, export_format, purged_count, message
| filter event like /transcript\.(ingest|export|delete|purge)/
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
| ALB liveness | API TG uses `GET /api/live` (no Bedrock); UI uses `/_stcore/health` |
| ALB → API | `http://<alb>/api/health` and `http://<alb>/api/workflows` |
| ALB → UI | `http://<alb>/_stcore/health` |
| ECS services | Desired == running; fail on recent `CannotPullContainerError` |
| Target groups | ≥1 **healthy** target per API/UI TG |
| Logs | Recent streams under `/rre/dev/api` and `/rre/dev/ui` |
| Bedrock path | Optional: Quick Review or `scripts/p1_4f_burnin.py` |

## Long-suite burn-in (P1-4f)

Prefer **background** workflows. Do **not** Deploy mid-burn-in.

```powershell
.\.venv\Scripts\python.exe -u scripts\p1_4f_burnin.py http://<alb-dns>
```

Expect: `research_oriented` (6 modules) then `full_multidisciplinary` (13). Script **fails** if synthesis has zero findings. ALB unhealthy_threshold is intentionally soft (10); API image runs **2 uvicorn workers** so `/api/live` stays up during Converse.

## Pause / resume (when idle)

**Standing practice:** Pause AWS when the stack is idle. Deploy does **not** run on docs-only pushes to `main` (path filters). Resume via **Deploy to AWS dev** (`workflow_dispatch`) or a runtime/infra push.

| Action | How |
|--------|-----|
| **Pause** | GitHub Actions → **Pause AWS dev** → Run workflow (`workflow_dispatch` works once `pause-dev.yml` is on `main`) |
| **Resume** | Actions → **Deploy to AWS dev** (`workflow_dispatch`), or push changes under runtime/infra paths (not docs-only) |

Pause sets ECS desired count to **0** and stops RDS `rre-dev-postgres`. Full steps, residual costs (ALB, ECR, Secrets Manager, RDS storage), and CLI equivalents: [infra/dev/README.md](../../infra/dev/README.md).

**Note:** Local `ops-admin` cannot update ECS/RDS; use the GitHub workflow (OIDC `dev-github-deploy`).
