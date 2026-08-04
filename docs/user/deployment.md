# Deployment — AWS only

The Relationship Reasoning Engine runs on **AWS ECS** (API + UI), **RDS PostgreSQL**, **Amazon Bedrock**, and **Amazon Transcribe**. There is no supported on-laptop product runtime.

| Topic | Document |
|-------|----------|
| Architecture & Terraform | [../planning/aws-deployment.md](../planning/aws-deployment.md) |
| Deploy / pause / logs | [../developer/aws-operations.md](../developer/aws-operations.md) |
| Infra README | [../../infra/dev/README.md](../../infra/dev/README.md) |
| Day-one usage | [getting-started.md](getting-started.md) |

## Baseline

| Item | Value |
|------|-------|
| App baseline | **v1.0.0** on `main` |
| Runtime | `Dockerfile.cloud` (API) · `Dockerfile.ui` (Streamlit) |
| LLM | Bedrock (`LLM_PROVIDER=bedrock`) |
| ASR | Amazon Transcribe (`TRANSCRIPTION_PROVIDER=transcribe`) |
| Database | RDS PostgreSQL (`DATABASE_URL` from Secrets Manager) |
| Workflows | `quick_review`, `full_mvp`, `conflict_coaching`, `mediation_brief`, `clinical_exploration`, `research_oriented`, `full_multidisciplinary` |

## Operator checklist

- [ ] Deploy for minor-version releases (tag or manual); wake via **`/login`** when asleep (v2.1)
- [ ] Confirm SES OTP arrives (verified `ses_from_email` / Actions var `SES_FROM_EMAIL`)
- [ ] Confirm `/api/live` then `/api/health` → Bedrock + Transcribe + database available
- [ ] Prepare transcript → Ready to Analyze → trial Quick Review
- [ ] Pause / idle sleep when done (ECS 0 + VPC endpoints deleted + RDS stopped; ALB kept)
- [ ] Prefer Insights by `module_run_id` (log redaction on)

## Runtime configuration (ECS)

Set in Terraform / task definitions (see `infra/dev/`). Common variables:

| Variable | Role |
|----------|------|
| `LLM_PROVIDER` | `bedrock` |
| `BEDROCK_MODEL_ID` | Default chat model ID |
| `TRANSCRIPTION_PROVIDER` | `transcribe` |
| `UPLOADS_BUCKET` | S3 for Transcribe I/O |
| `DATABASE_URL` | Postgres (secret) |
| `LOG_JSON` / `LOG_REDACT` | Structured, scrubbed CloudWatch logs |
| `TRANSCRIPT_RETENTION_DAYS` | Optional startup purge |
| `WORKFLOW_SYNC_MODULE_LIMIT` | Default `6` — longer suites background |
| `SESSION_AUTH_REQUIRED` | `true` — product session cookie gate (v2.1) |
| `EMAIL_DELIVERY` / `SES_FROM_EMAIL` | `ses` + verified From identity for OTP |
| `API_KEY` | Break-glass `X-API-Key` (Secrets Manager on ECS) |
| `POWER_CONTROL_ENABLED` / `POWER_STATE_TABLE` | Idle power plane |
| `ACM_CERTIFICATE_ARN` | Optional — enables ALB HTTPS when set in Terraform |

Auth / wake runbook: [../developer/auth-and-power.md](../developer/auth-and-power.md).

Developer `.env` / SQLite are for **pytest and tooling only**, not a supported local server.

## Related

- [user-guide.md](user-guide.md) · [model-setup.md](model-setup.md)
- [../planning/implementing.md](../planning/implementing.md)
- API: [../developer/api-reference.md](../developer/api-reference.md)
