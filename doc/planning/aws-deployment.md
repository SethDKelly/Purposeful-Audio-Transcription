# AWS Deployment — RRE Dev Environment

Architecture and integration guide for deploying the Relationship Reasoning Engine to the **personal AWS dev account** managed by [aws-backbone](https://github.com/SethDKelly/aws-backbone).

| | |
|---|---|
| **Account** | `521018312783` |
| **Region** | `us-east-2` (Ohio) |
| **Deploy role** | `arn:aws:iam::521018312783:role/dev-github-deploy` |
| **Branch** | `main` @ **v0.5.1** (canonical) |
| **Deploy** | Path-filtered push to `main` + `workflow_dispatch` |
| **Active plan** | [implementing.md](implementing.md) |

### Data residency (privacy)

On AWS, audio objects, transcripts, and analysis results stay in **this account** (S3, RDS, ECS in VPC). Inference uses **Amazon Bedrock** and **Amazon Transcribe** — no off-account LLM/ASR APIs. Operators should pause the stack when idle ([aws-operations.md](../developer/aws-operations.md)). This product is **AWS-only** (no local Whisper/Ollama runtime).

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
                    GitHub Actions (push main / workflow_dispatch)
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
                    │  ALB (HTTP today; HTTPS backlog) │
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
| Images | ECR API + ECR DKR interface endpoints **and** S3 gateway (image layers) |
| Uploads | S3 gateway endpoint |
| STS | Interface endpoint (task credentials without public egress) |
| Block general egress | Private tasks / no public IP + tightened SGs (phased — see below) |

Tasks must not call `ollama_host`, `huggingface.co`, or other external URLs during `/api/transcribe` or workflow/module runs in AWS deploy (target state).

#### Staged no-egress (AWS-1d / AWS-5h)

Default VPC public subnets + Fargate **without** a public IP cannot reach the internet via the IGW. ECR image **layers** are fetched from S3; if the S3 gateway route is missing or incomplete, pulls fail with `CannotPullContainerError` / `dial tcp …:443: i/o timeout`.

| Stage | Terraform flags | Behavior |
|-------|-----------------|----------|
| **A — Endpoints only** | `enable_vpc_endpoints=true`, `enable_no_egress_networking=false` | Interface + S3 gateway endpoints; tasks keep public IPs (rollback if Stage B pull fails) |
| **B — Strict no-egress (current default)** | both `true` | `assign_public_ip=false`, tightened SGs, UI→API via Cloud Map (`api.rre-dev.local:8000`) |

**Stage B SG requirements (learned from failed first attempt):**

1. S3 gateway on **every** route table used by task subnets (default VPC: query all RTs — subnets often lack explicit associations).
2. Task SG egress **443 to the S3 prefix list** (`com.amazonaws.<region>.s3`) — gateway traffic targets public S3 IPs, not VPC CIDR.
3. Task SG egress **53/udp+tcp to VPC CIDR** for AmazonProvidedDNS (private DNS for interface endpoints).
4. ECR `api` + `dkr` interface endpoints with `private_dns_enabled=true`.

**Interim conflict:** pyannote / Hugging Face still needs egress until P1-1 Transcribe. Paste/upload + Bedrock analysis is the no-egress-compatible path today.

See `infra/dev/vpc_endpoints.tf`, `infra/dev/alb.tf`, `infra/dev/README.md`.

---

## 4. Model strategy (AWS only)

| Capability | Service |
|------------|---------|
| **LLM** | Amazon Bedrock (Converse API) |
| **ASR** | Amazon Transcribe (speaker labels → turns) |
| **Structured JSON** | Prompt + `OutputParser` (+ coercion) |

```text
ModuleRunner / WorkflowEngine
        │
   BedrockProvider
AmazonTranscribeProvider  ← S3 uploads bucket
```

| Variable | ECS value |
|----------|-----------|
| `LLM_PROVIDER` | `bedrock` |
| `BEDROCK_MODEL_ID` | e.g. `us.anthropic.claude-sonnet-4-5-20250929-v1:0` |
| `TRANSCRIPTION_PROVIDER` | `transcribe` |
| `UPLOADS_BUCKET` | `rre-dev-uploads-…` |
| `AWS_REGION` | `us-east-2` |

Formal notes: [llm-evaluation-bedrock.md](llm-evaluation-bedrock.md) · [asr-evaluation-transcribe.md](asr-evaluation-transcribe.md).

Local Ollama / Whisper / pyannote stacks are **removed** from the product (P1-7).

---

## 5. Audio ingest

Amazon Transcribe owns decode and speaker labeling. The API uploads to S3, polls the job, and maps speaker segments to existing turn / evidence-quote shapes. **No ffmpeg / torch** in the cloud API image.

---

## 6. Runtime images

| Image | Contents |
|-------|----------|
| `Dockerfile.cloud` | Slim API — FastAPI, boto3, SQLAlchemy; Bedrock + Transcribe |
| `Dockerfile.ui` | Streamlit only → ALB `/api` |

```text
ALB → rre-dev-ui (Streamlit) + rre-dev-api (Bedrock + Transcribe + RDS + S3)
```

CI builds and pushes **cloud + UI** only. Developer loop: `pip install -e ".[dev]"` + pytest (SQLite) + Deploy.

Scale Fargate for Python/JSON, not model weights.

---

## 7. Observability & debugging

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
| Runbook: Logs Insights queries | [doc/developer/aws-operations.md](../developer/aws-operations.md) |

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

## 8. GitHub Actions deploy workflow

Pattern matches aws-backbone [github-actions.md](https://github.com/SethDKelly/aws-backbone/blob/main/docs/github-actions.md) and MinneAnalytics example.

```yaml
# .github/workflows/deploy-dev.yml (skeleton)
name: Deploy to AWS dev

on:
  push:
    branches: [main]
    paths-ignore:
      - "**/*.md"
      - "doc/**"
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

**Cost control:** When the stack is idle, run **Pause AWS dev** (`pause-dev.yml`) to scale ECS to 0 and stop RDS. Resume with **Deploy to AWS dev**. Standing practice is documented in [implementing.md](implementing.md) and [../developer/aws-operations.md](../developer/aws-operations.md).

---

## 9. Data & secrets

| Secret / config | Store | Notes |
|-----------------|-------|-------|
| `DATABASE_URL` | Secrets Manager | RDS PostgreSQL in AWS |
| `API_KEY` | Secrets Manager | Optional auth |
| `BEDROCK_MODEL_ID` | Env / SSM | Non-secret |
| `HF_TOKEN` | Not used in AWS | Transcribe replaces pyannote |
| Upload storage | S3 | Pre-signed or API proxy; lifecycle expiration |

SQLite is for local dev only; AWS deploy uses PostgreSQL (`ALEMBIC_AUTO_UPGRADE=true`).

---

## 10. Rollout sequence

| Step | Owner | Depends on | Status |
|------|-------|------------|--------|
| 1. Merge aws-backbone PR (OIDC + `rre-dev-*`) | aws-backbone | — | ✓ |
| 2. Architecture sign-off (this doc) | RRE | — | ✓ |
| 3. `LLMProvider` + Bedrock spike | RRE | — | ✓ |
| 4. Dockerfile + local smoke | RRE | — | ✓ |
| 5. `infra/dev/` minimal (ECR, ECS, RDS, ALB, logs) | RRE | Step 1 | ✓ |
| 6. `deploy-dev.yml` | RRE | Steps 4–5 | ✓ (push `main` + `workflow_dispatch`) |
| 7. Quick Review on Bedrock in dev | RRE | Step 6 | ✓ |
| 8. Transcribe path | RRE | Step 7 | ✓ (slim + Stage B burn-in 2026-07-14) |
| 9. PR `phase-m0-docs` → `main` / **v0.5.1 release** | RRE | Stable dev | ✓ |

---

## 11. Open questions

| Question | Options | Decision by |
|----------|---------|-------------|
| ECS Fargate vs EC2 GPU for interim Whisper | Fargate only if Transcribe is fast-follow | After Transcribe spike |
| Single vs split ECS services (API + UI) | Split recommended (independent scale/restart) | Infra PR |
| Bedrock model default | Claude 3.5 Sonnet vs Llama 3.1 70B | After JSON spike |
| Public ALB vs VPN-only | Today: public HTTP ALB, optional API key unused. Target: ACM HTTPS + API key (+ IP allowlist/VPN) — [backlog HTTPS/TLS](backlog.md) | Before external sensitive UAT |
| NAT gateway | Required if tasks need outbound non-AWS; avoid for no-egress goal | Network design |
| Slim cloud image cutover | After Bedrock only vs after Transcribe too | After P1-1 spike |
| `Dockerfile.cloud` naming | Separate file vs multi-stage `target` | Infra PR |

---

## 12. Related documents

- [implementing.md](implementing.md) — active priorities (critical → significant → materially important)
- [aws-backbone architecture](https://github.com/SethDKelly/aws-backbone/blob/main/docs/architecture.md)
- [aws-backbone GitHub Actions guide](https://github.com/SethDKelly/aws-backbone/blob/main/docs/github-actions.md)
- [../user/deployment.md](../user/deployment.md) — legacy local deployment
