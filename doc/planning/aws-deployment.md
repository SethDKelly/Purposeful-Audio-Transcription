# AWS Deployment — RRE Dev Environment

Architecture and integration guide for deploying the Relationship Reasoning Engine to the **personal AWS dev account** managed by [aws-backbone](https://github.com/SethDKelly/aws-backbone).

| | |
|---|---|
| **Account** | `521018312783` |
| **Region** | `us-east-2` (Ohio) |
| **Deploy role** | `arn:aws:iam::521018312783:role/dev-github-deploy` |
| **Branch (initial testing)** | `phase-m0-docs` → PR to `main` when stable |
| **Active plan** | [implementation_plan.md](implementation_plan.md) |

---

## 1. Relationship to aws-backbone

**aws-backbone is not application infrastructure.** It provides:

- GitHub OIDC provider
- `dev-github-deploy` (CI deploy) and `dev-developer` (human MFA access)
- Permission boundaries and cautious IAM denies
- Terraform remote state bucket: `aws-backbone-terraform-state-521018312783`

Application runtime (ECS, RDS, Bedrock, etc.) lives in **this repository** under `infra/dev/`, following the same pattern as MinneAnalytics.

### MinneAnalytics — do not modify

| Resource | Value | Notes |
|----------|-------|-------|
| GitHub repo (OIDC) | `SethDKelly/MinneAnalytics` | Keep in `github_repositories`; do not remove |
| IAM role prefix | `minneanalytics-dev-*` | Keep in `app_deploy_iam.tf` and permission boundaries |
| Terraform state key | `minneanalytics/dev/terraform.tfstate` | Separate from RRE |
| Stack | ECS Fargate + EFS | Managed in MinneAnalytics repo |

RRE additions must be **additive only**.

### RRE naming (new)

| Resource | Suggested value |
|----------|-----------------|
| GitHub repo (OIDC) | `SethDKelly/Purposeful-Audio-Transcription` |
| IAM role prefix | `rre-dev-*` |
| Terraform state key | `purposeful-audio-transcription/dev/terraform.tfstate` |
| ECR repositories | `rre-dev-api`, `rre-dev-ui` |
| ECS cluster | `rre-dev` |
| CloudWatch log groups | `/rre/dev/api`, `/rre/dev/ui` |
| S3 bucket | `rre-dev-uploads-521018312783` (example) |

---

## 2. aws-backbone changes ✓

**Status:** Merged to aws-backbone `main` (PR #1, commit `3d14411`). Terraform apply via backbone CI should have updated live IAM.

Applied changes:

### 2.1 Add GitHub OIDC trust

In `accounts/shared-services/variables.tf`, extend `github_repositories`:

```hcl
default = [
  "SethDKelly/MinneAnalytics",
  "SethDKelly/Purposeful-Audio-Transcription",
]
```

### 2.2 Extend IAM prefix for deploy workflows

Today `modules/dev-iam/main.tf` and `app_deploy_iam.tf` scope IAM mutations to `minneanalytics-dev-*` only. Add **`rre-dev-*`** alongside (not replacing):

- `local.app_deploy_iam_role_arn_prefixes` — list of allowed role ARN patterns
- Update `dev_github_deploy_permission_boundary`, `dev_github_deploy_cautious_deny`, and `AllowAppDeployIamRoles` resources to include both prefixes

**Verify:** MinneAnalytics deploy workflow still passes after apply.

---

## 3. Target architecture (dev)

```text
                    GitHub Actions (phase-m0-docs)
                              │
                              ▼ OIDC
                    dev-github-deploy
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
      ECR push          terraform apply        ECS deploy
         │                    │                    │
         └────────────────────┴────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  ALB (HTTPS)      │
                    └─────────┬─────────┘
              ┌───────────────┴───────────────┐
              ▼                               ▼
      ECS: rre-dev-api                 ECS: rre-dev-ui
      (FastAPI)                        (Streamlit)
              │                               │
              ├─────────── RDS PostgreSQL ────┤
              ├─────────── S3 uploads ────────┤
              ├─────────── Secrets Manager ───┤
              │
              ├── Amazon Bedrock (LLM — module runs, synthesis)
              └── Amazon Transcribe (ASR — audio ingest, phase 2)

VPC: private subnets for tasks; VPC endpoints for AWS API calls.
No public internet egress required during model operations.
```

### Network: no outbound during model operations

| Requirement | Implementation |
|-------------|----------------|
| LLM inference in AWS | Amazon Bedrock via `bedrock-runtime` + **VPC interface endpoint** |
| Speech-to-text in AWS | Amazon Transcribe via VPC endpoint (async jobs) |
| Secrets | Secrets Manager VPC endpoint |
| Logs | CloudWatch Logs VPC endpoint |
| Images | ECR VPC endpoint |
| Uploads | S3 gateway endpoint |
| Block general egress | Private subnets, no NAT (or NAT only for bootstrap/management if required) |

Tasks must not call `ollama_host`, `huggingface.co`, or other external URLs during `/api/transcribe` or workflow/module runs in AWS deploy.

---

## 4. Model strategy — moving away from Ollama

### Current state

- `OllamaService` — direct `ollama` Python client + HTTP health check
- Module YAML `ollama_model` field
- Whisper + pyannote for audio (local ML, HF token, GPU optional)

### Target state (AWS dev)

| Capability | AWS service | Local dev fallback |
|------------|-------------|-------------------|
| **LLM (modules, synthesis, exploration)** | **Amazon Bedrock** — Converse API, model IDs e.g. Claude 3.5 Sonnet, Llama 3.x on Bedrock | Ollama (`LLM_PROVIDER=ollama`) |
| **Audio transcription** | **Amazon Transcribe** — batch, speaker diarization labels | Whisper (`TRANSCRIPTION_PROVIDER=whisper`) |
| **Structured JSON** | Bedrock tool use / response schema; prompt + parser unchanged | Ollama `format=json` |

### Why Bedrock over self-hosted Ollama on ECS

| Factor | Bedrock | Ollama on ECS/EC2 |
|--------|---------|-------------------|
| Ops burden | Low — managed | High — GPU instances, model files, upgrades |
| No-egress | VPC endpoint | Must host Ollama in VPC + model volumes |
| Structured output | Native tool/schema support | JSON mode (model-dependent) |
| Cost model | Per-token | Always-on GPU/CPU |
| Alignment with AWS pivot | Primary | Interim bridge only |

### Provider abstraction (application)

Introduce a thin adapter layer — **no business logic in providers**:

```text
ModuleRunner / WorkflowEngine
        │
        ▼
   LLMProvider (protocol)
        ├── BedrockProvider   ← AWS default
        └── OllamaProvider    ← local dev

TranscriptionProvider (protocol)
        ├── TranscribeProvider  ← AWS default
        └── WhisperProvider     ← local dev
```

Settings (`.env` / Secrets Manager):

| Variable | AWS dev | Local dev |
|----------|---------|-----------|
| `LLM_PROVIDER` | `bedrock` | `ollama` |
| `BEDROCK_MODEL_ID` | e.g. `anthropic.claude-3-5-sonnet-20241022-v2:0` | — |
| `DEFAULT_OLLAMA_MODEL` | — | e.g. `llama3.2` |
| `TRANSCRIPTION_PROVIDER` | `transcribe` | `whisper` |
| `AWS_REGION` | `us-east-2` | — |

Module YAML: rename conceptually to `model_id` (keep `ollama_model` as alias during migration).

### Bedrock evaluation checklist (spike)

- [ ] Converse API with module system prompt + evidence index (context limits vs Claude/Llama on Bedrock)
- [ ] Structured JSON for `module_output_v1` — tool spec or constrained decoding
- [ ] Retry behavior on malformed JSON (same as `OutputParser` today)
- [ ] `meta_synthesis` on Bedrock — higher token output
- [ ] IAM: task role `bedrock:InvokeModel` scoped to model ARNs
- [ ] Latency and cost estimate for Quick Review vs Full MVP

### Transcribe evaluation checklist

- [ ] Speaker diarization / max speaker labels vs pyannote quality
- [ ] Async job polling from API
- [ ] Map Transcribe output → existing `TranscriptParser` labeled turns
- [ ] S3 upload path for audio files

---

## 5. Observability & debugging

### Goals

- Every failed workflow/module run is traceable in CloudWatch without SSH
- Logs are structured for Logs Insights queries
- Transcript text and audio content never appear in logs

### Log format (JSON)

```json
{
  "timestamp": "2026-07-11T03:00:00Z",
  "level": "ERROR",
  "logger": "backend.services.module_runner",
  "message": "Module run failed after retries",
  "request_id": "uuid",
  "workflow_run_id": "uuid",
  "module_run_id": "uuid",
  "module_id": "nvc_analysis",
  "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
  "provider": "bedrock",
  "error_type": "OutputParseError",
  "retry_count": 2
}
```

Enable via `LOG_JSON=true` (already in settings).

### Implementation tasks

| Task | Location |
|------|----------|
| Request ID middleware | `backend/main.py` |
| Bind context vars in workflow/module routes | API routes |
| ERROR logs with exception info | `module_runner`, `workflow_engine`, `output_parser` |
| Terraform: log groups + retention (14–30 days dev) | `infra/dev/` |
| Runbook: Logs Insights queries | `doc/developer/aws-operations.md` (to create) |

### Example Logs Insights queries

```text
# Failed module runs (last hour)
fields @timestamp, module_id, error_type, workflow_run_id, module_run_id
| filter @message like /Module run failed/
| sort @timestamp desc

# JSON parse failures
fields @timestamp, module_id, module_run_id
| filter error_type = "OutputParseError"
| sort @timestamp desc
```

---

## 6. GitHub Actions deploy workflow

Pattern matches aws-backbone [github-actions.md](https://github.com/SethDKelly/aws-backbone/blob/main/docs/github-actions.md) and MinneAnalytics example.

```yaml
# .github/workflows/deploy-dev.yml (skeleton)
name: Deploy to AWS dev

on:
  push:
    branches: [phase-m0-docs]   # switch to main when stable
  workflow_dispatch:

permissions:
  id-token: write
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[dev]" && pytest tests/ -q

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::521018312783:role/dev-github-deploy
          aws-region: us-east-2
      # build → ECR push → terraform apply → ecs update-service
```

**Do not** store AWS access keys in GitHub Secrets — OIDC only.

---

## 7. Data & secrets

| Secret / config | Store | Notes |
|-----------------|-------|-------|
| `DATABASE_URL` | Secrets Manager | RDS PostgreSQL in AWS |
| `API_KEY` | Secrets Manager | Optional auth |
| `BEDROCK_MODEL_ID` | Env / SSM | Non-secret |
| `HF_TOKEN` | Not used in AWS | Transcribe replaces pyannote |
| Upload storage | S3 | Pre-signed or API proxy; lifecycle expiration |

SQLite is for local dev only; AWS deploy uses PostgreSQL (`ALEMBIC_AUTO_UPGRADE=true`).

---

## 8. Rollout sequence

| Step | Owner | Depends on | Status |
|------|-------|------------|--------|
| 1. Merge aws-backbone PR (OIDC + `rre-dev-*`) | aws-backbone | — | ✓ |
| 2. Architecture sign-off (this doc) | RRE | — | ✓ |
| 3. `LLMProvider` + Bedrock spike | RRE | — | [ ] |
| 4. Dockerfile + local smoke | RRE | — | [ ] |
| 5. `infra/dev/` minimal (ECR, ECS, RDS, ALB, logs) | RRE | Step 1 | [ ] |
| 6. `deploy-dev.yml` on `phase-m0-docs` | RRE | Steps 4–5 | [ ] |
| 7. Quick Review on Bedrock in dev | RRE | Step 6 | [ ] |
| 8. Transcribe path | RRE | Step 7 | [ ] |
| 9. PR `phase-m0-docs` → `main` | RRE | Stable dev | [ ] |

---

## 9. Open questions

| Question | Options | Decision by |
|----------|---------|-------------|
| ECS Fargate vs EC2 GPU for interim Whisper | Fargate only if Transcribe is fast-follow | After Transcribe spike |
| Single vs split ECS services (API + UI) | Split recommended (independent scale/restart) | Infra PR |
| Bedrock model default | Claude 3.5 Sonnet vs Llama 3.1 70B | After JSON spike |
| Public ALB vs VPN-only | ALB + API key for dev; document IP allowlist | Security preference |
| NAT gateway | Required if tasks need outbound non-AWS; avoid for no-egress goal | Network design |

---

## 10. Related documents

- [implementation_plan.md](implementation_plan.md) — prioritized P0-AWS tasks
- [aws-backbone architecture](https://github.com/SethDKelly/aws-backbone/blob/main/docs/architecture.md)
- [aws-backbone GitHub Actions guide](https://github.com/SethDKelly/aws-backbone/blob/main/docs/github-actions.md)
- [../user/deployment.md](../user/deployment.md) — legacy local deployment
