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
| App baseline | v0.5.1+ on `main` |
| Runtime | `Dockerfile.cloud` (API) · `Dockerfile.ui` (Streamlit) |
| LLM | Bedrock (`LLM_PROVIDER=bedrock`) |
| ASR | Amazon Transcribe (`TRANSCRIPTION_PROVIDER=transcribe`) |
| Database | RDS PostgreSQL (`DATABASE_URL` from Secrets Manager) |
| Workflows | `quick_review`, `full_mvp`, `conflict_coaching`, `mediation_brief`, `clinical_exploration`, `research_oriented`, `full_multidisciplinary` |

## Operator checklist

- [ ] Deploy when needed; **Pause** when idle
- [ ] Confirm `/api/health` → Bedrock + Transcribe + database available
- [ ] Trial Quick Review on a short transcript
- [ ] Restrict IAM / ALB access for sensitive dialogue
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
| `API_KEY` | Optional `X-API-Key` |

Developer `.env` / SQLite are for **pytest and tooling only**, not a supported local server.

## Related

- [user-guide.md](user-guide.md) · [model-setup.md](model-setup.md)
- [../planning/implementing.md](../planning/implementing.md)
- API: [../developer/api-reference.md](../developer/api-reference.md)
