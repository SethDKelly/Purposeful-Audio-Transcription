# AWS Deployment — RRE Dev Environment

Architecture and integration guide for deploying the Relationship Reasoning Engine to the **personal AWS dev account** managed by [aws-backbone](https://github.com/SethDKelly/aws-backbone).

| | |
|---|---|
| **Account** | `521018312783` |
| **Region** | `us-east-2` (Ohio) |
| **Deploy role** | `arn:aws:iam::521018312783:role/dev-github-deploy` |
| **Release baseline** | **v1.0.0** (worker + DAG + custom workflows) |
| **Deploy** | Version tags `v*.*.*` (all components) or **workflow_dispatch** with `component=all\|api\|ui\|worker` |
| **Active plan** | [phases/01_v1_1_operational_hardening.md](../planning/phases/01_v1_1_operational_hardening.md) |

### Data residency (privacy)

On AWS, audio objects, transcripts, and analysis results stay in **this account** (S3, RDS, ECS in VPC). Inference uses **Amazon Bedrock** and **Amazon Transcribe** — no off-account LLM/ASR APIs. Operators should pause the stack when idle ([aws-operations.md](aws-operations.md)). This product is **AWS-only** (no local Whisper/Ollama runtime).

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
| ECR repositories | `rre-dev-api`, `rre-dev-ui` (worker reuses API image) |
| ECS cluster | `rre-dev-cluster` |
| ECS services | `rre-dev-api`, `rre-dev-ui`, `rre-dev-worker` |
| CloudWatch log groups | `/rre/dev/api`, `/rre/dev/ui`, `/rre/dev/worker` |
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
           GitHub Actions (tag v*.*.* | workflow_dispatch + component)
                              │
                              ▼ OIDC
                    dev-github-deploy
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
      ECR push          terraform apply        ECS update-service
   (api and/or ui)            │              (api / ui / worker)
         └────────────────────┴────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  ALB (HTTP; HTTPS optional) │
                    └─────────┬─────────┘
              ┌───────────────┴───────────────┐
              ▼                               ▼
      ECS: rre-dev-api                 ECS: rre-dev-ui
      (FastAPI)                        (Streamlit → API)
              │
              │  queues jobs (CREATED)
              ▼
      ECS: rre-dev-worker
      (same cloud image; RRE_PROCESS=worker)
              │
              ├── RDS PostgreSQL
              ├── S3 uploads
              ├── Secrets Manager
              ├── Amazon Bedrock (LLM — module runs, synthesis)
              └── Amazon Transcribe (ASR)

VPC: private subnets for tasks; VPC endpoints for AWS API calls.
No public internet egress required during model operations.
```

### Service topology

| Service | Image | Role | ALB |
|---------|-------|------|-----|
| `rre-dev-api` | `rre-dev-api` (`Dockerfile.cloud`) | HTTP API, job enqueue, health | Yes (`/api/*`) |
| `rre-dev-ui` | `rre-dev-ui` (`Dockerfile.ui`) | Streamlit admin/eval client via `RRE_API_BASE_URL` | Yes (`/` + `/_stcore/health`) |
| `rre-dev-web` _(v1.3)_ | `frontend-react/Dockerfile` (nginx static) | React product UI → `/api/v1` | Optional separate listener/path; ECS wiring in v1.4 |
| `rre-dev-worker` | **same** `rre-dev-api` image | Poll/claim jobs; Bedrock/Transcribe/workflows | No (ECS + `/rre/dev/worker` logs) |

Today API/UI/worker use **separate** ECS task roles and a dedicated UI execution role (v1.1 Workstream D):

| Role | Used by | Notable allows / denies |
|------|---------|-------------------------|
| `rre-dev-ecs-execution-ui` | UI | Secrets: `API_KEY` only (no `DATABASE_URL`) |
| `rre-dev-ecs-execution` | API, worker | Secrets: `DATABASE_URL` + `API_KEY` |
| `rre-dev-ecs-task-ui` | UI | No Bedrock / Transcribe / S3 |
| `rre-dev-ecs-task-api` | API | Bedrock catalog (health), S3 uploads, Transcribe; **no** `InvokeModel` |
| `rre-dev-ecs-task-worker` | Worker | `InvokeModel`, Marketplace subscribe, S3, Transcribe |

Validate UI cannot read the DB secret: its execution role policy resources list must omit the database secret ARN (see `infra/dev/iam.tf`).

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

Formal notes: [../evaluation/llm-evaluation-bedrock.md](../evaluation/llm-evaluation-bedrock.md) · [../evaluation/asr-evaluation-transcribe.md](../evaluation/asr-evaluation-transcribe.md).

Local Ollama / Whisper / pyannote stacks are **removed** from the product (P1-7).

---

## 5. Audio ingest

Amazon Transcribe owns decode and speaker labeling. The API uploads to S3, polls the job, and maps speaker segments to existing turn / evidence-quote shapes. **No ffmpeg / torch** in the cloud API image.

---

## 6. Runtime images

| Image | Contents | Used by |
|-------|----------|---------|
| `Dockerfile.cloud` → ECR `rre-dev-api` | Slim API — FastAPI, boto3, SQLAlchemy; Bedrock + Transcribe | `rre-dev-api`, `rre-dev-worker` |
| `Dockerfile.ui` → ECR `rre-dev-ui` | Streamlit only → ALB `/` | `rre-dev-ui` |

```text
ALB → rre-dev-ui (Streamlit) + rre-dev-api (enqueue + HTTP)
Worker (no ALB) → same cloud image; claims jobs; Bedrock + Transcribe + RDS + S3
```

CI builds/pushes images based on **`component`**:

| `component` | Builds | Forces ECS update |
|-------------|--------|-------------------|
| `all` | API + UI | api, ui, worker |
| `api` | API | api |
| `ui` | UI | ui |
| `worker` | API (shared image) | worker |

Tag pushes always use `component=all`. Path-filtered auto-deploy on `main` is **not** used (cost/control: tags or manual only).

Developer loop: `pip install -e ".[dev]"` + `python -m pytest` (SQLite) + Deploy.

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
| Runbook: Logs Insights queries | [aws-operations.md](aws-operations.md) |

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
# .github/workflows/deploy-dev.yml (current)
name: Deploy to AWS dev

on:
  workflow_dispatch:
    inputs:
      component:
        type: choice
        options: [all, api, ui, worker]
  push:
    tags:
      - "v*.*.*"
```

Ordinary pushes to `main` do **not** deploy. Use a version tag (`all`) or **workflow_dispatch** with a component.

Flow: test (`python -m pytest`) → OIDC → ensure RDS → build selected image(s) → terraform apply → `ecs update-service` for selected services → wait stable → `scripts/aws-deploy-smoke.sh` (scoped by `DEPLOY_COMPONENT`).

**Smoke by component**

| Component | Checks |
|-----------|--------|
| `api` | `/api/live`, `/api/health`, `/api/workflows`, API ECS + TG, `/rre/dev/api` |
| `ui` | `/api/live` (dependency), `/_stcore/health`, UI ECS + TG, `/rre/dev/ui` |
| `worker` | Worker ECS desired=running, `/rre/dev/worker` (no ALB) |
| `all` | Union of the above |

**Do not** store AWS access keys in GitHub Secrets — OIDC only.

### Per-service rollback

ECS keeps previous task definition revisions. To roll back one service without rebuilding others:

```bash
# Example: roll API back to a prior revision (replace N)
aws ecs update-service --cluster rre-dev-cluster --service rre-dev-api \
  --task-definition rre-dev-api:N --force-new-deployment

# UI / worker similarly: rre-dev-ui:N / rre-dev-worker:N
```

Or re-run **Deploy to AWS dev** with `component=api|ui|worker` after fixing the image/tag. Worker shares the API image digest; rolling worker alone redeploys the last pushed `rre-dev-api` image with `RRE_PROCESS=worker`.

**Cost control:** When the stack is idle, run **Pause AWS dev** (`pause-dev.yml`) to scale ECS (api/ui/worker) to 0 and stop RDS. Resume with **Deploy to AWS dev**. Standing practice: [deferred_backlog.md](../planning/deferred_backlog.md) and [aws-operations.md](aws-operations.md).

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
| 3. Bedrock + Transcribe on AWS | RRE | — | ✓ |
| 4. Split ECS API + UI | RRE | — | ✓ |
| 5. Dedicated worker (`rre-dev-worker`) | RRE | v1.0 | ✓ |
| 6. Tag / manual deploy (not every `main` push) | RRE | — | ✓ |
| 7. Selective `component` deploy + scoped smoke | RRE | v1.1 C | ✓ |
| 8. Service-specific IAM roles | RRE | v1.1 D | ✓ |

---

## 11. Open questions

| Question | Status |
|----------|--------|
| Public ALB vs VPN-only | Today: shared API key; optional ACM HTTPS when cert set. Domain + TLS before broad external UAT |
| NAT gateway | Avoid for no-egress goal; VPC endpoints cover AWS APIs |
| Split task IAM (UI vs API vs worker) | v1.1 Workstream D |
| Path-filtered auto-deploy on `main` | Declined — tags + `workflow_dispatch` only |

---

## 12. Related documents

- [phases/01_v1_1_operational_hardening.md](../planning/phases/01_v1_1_operational_hardening.md) — current phase
- [deferred_backlog.md](../planning/deferred_backlog.md) — prioritized deferred work
- [aws-operations.md](aws-operations.md) — deploy / pause / Logs Insights
- [../releases/v1.0.0.md](../releases/v1.0.0.md) — current release notes
- [../archived/planning/executive_roadmap.md](../archived/planning/executive_roadmap.md) — completed program roadmap
- [aws-backbone architecture](https://github.com/SethDKelly/aws-backbone/blob/main/docs/architecture.md)
- [aws-backbone GitHub Actions guide](https://github.com/SethDKelly/aws-backbone/blob/main/docs/github-actions.md)
- [../user/deployment.md](../user/deployment.md) — operator deployment pointers
