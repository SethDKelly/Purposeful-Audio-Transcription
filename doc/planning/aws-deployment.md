# AWS Deployment — RRE Dev Environment

Architecture and integration guide for deploying the Relationship Reasoning Engine to the **personal AWS dev account** managed by [aws-backbone](https://github.com/SethDKelly/aws-backbone).

| | |
|---|---|
| **Account** | `521018312783` |
| **Region** | `us-east-2` (Ohio) |
| **Deploy role** | `arn:aws:iam::521018312783:role/dev-github-deploy` |
| **Branch (initial testing)** | `phase-m0-docs` → PR to `main` when stable |
| **Active plan** | [implementing.md](implementing.md) |

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
| `BEDROCK_MODEL_ID` | e.g. `us.anthropic.claude-sonnet-4-5-20250929-v1:0` | — |
| `DEFAULT_OLLAMA_MODEL` | — | e.g. `llama3.2` |
| `TRANSCRIPTION_PROVIDER` | `transcribe` | `whisper` |
| `AWS_REGION` | `us-east-2` | — |

Module YAML: rename conceptually to `model_id` (keep `ollama_model` as alias during migration).

### Bedrock evaluation checklist (spike)

Formal note: [llm-evaluation-bedrock.md](llm-evaluation-bedrock.md) (AWS-1b).

- [x] Converse API with module system prompt + evidence index
- [x] Structured JSON for `module_output_v1` — prompt + `OutputParser` (+ coercion)
- [x] Retry behavior on malformed JSON
- [ ] `meta_synthesis` on Bedrock — higher token output (Full MVP burn-in)
- [x] IAM: task role invoke + Marketplace via Bedrock
- [ ] Latency and cost estimate for Quick Review vs Full MVP (instrument)

### Transcribe evaluation checklist

Formal note: [asr-evaluation-transcribe.md](asr-evaluation-transcribe.md) (AWS-1c).

- [ ] Speaker diarization / max speaker labels vs pyannote quality
- [ ] Async job polling from API
- [ ] Map Transcribe output → existing labeled turns
- [ ] S3 upload path for audio files
- [ ] VPC endpoint smoke under Stage B no-egress (pending green deploy after SG + RT fixes)

---

## 5. Audio decode strategy

RRE uses **three different decode paths** today. They should not be collapsed into one library without reason.

| Path | Used by | Mechanism | Where |
|------|---------|-----------|-------|
| **ffmpeg CLI** | pyannote diarization (`load_waveform_for_diarization`) | `ffprobe` + `ffmpeg` subprocess → `torch` tensor | Local + current AWS interim image |
| **PyAV / ffmpeg libs** | Whisper (`faster-whisper` `decode_audio`) | Linked libraries via faster-whisper | Local when `TRANSCRIPTION_PROVIDER=whisper` |
| **torchcodec** | pyannote default (not used by RRE) | In-process decode; requires FFmpeg **shared libs** + strict torch pin | Not recommended as primary |

### Decision

| Environment | Primary decode | Notes |
|-------------|----------------|-------|
| **Local (incl. Windows)** | **ffmpeg CLI** for diarization; faster-whisper for Whisper | Avoid torchcodec — DLL/Application Control fragility on Windows |
| **AWS interim** (before Transcribe) | ffmpeg in container + same Python path as local | `apt-get install ffmpeg` on Linux ECS is reliable |
| **AWS target** | **No local decode** for ingest | Amazon Transcribe returns text + speaker labels; API maps to existing turns |

**Do not migrate to torchcodec** to “fix” deployment. torchcodec still depends on FFmpeg shared libraries and adds a **torch ↔ torchcodec version matrix**. It does not improve transcription or diarization quality when the output is the same PCM tensor.

Optional later (Linux only): try torchcodec in-process with **automatic fallback** to ffmpeg CLI if health check fails — not a priority.

### Quality expectation

Decode choice affects **reliability and ops**, not model accuracy. Whisper and pyannote quality depend on model weights, sample rate, and diarization/slicing logic — not subprocess vs in-process decode.

---

## 6. Hybrid cloud/local — compact local, robust cloud

Cloud deployment removes the need to **ship large models in containers**. Bedrock and Transcribe are managed; model size and GPU are AWS’s problem. The goal is **one codebase**, **two runtime profiles**, and **no bloated cloud image** once providers are wired.

### Runtime profiles (same code, different env)

| Setting | **Local profile** | **Cloud profile** |
|---------|-------------------|-------------------|
| `LLM_PROVIDER` | `ollama` | `bedrock` |
| `TRANSCRIPTION_PROVIDER` | `whisper` | `transcribe` |
| `DIARIZATION_ENABLED` | `true` (pyannote) | `false` (Transcribe speaker labels) |
| Models in container | Whisper weights + pyannote via torch/HF | **None** (API clients only) |
| Typical image size | Large (~2–4 GB+) | **Small** (~200–400 MB) |
| HF_TOKEN | Required for pyannote | Not required |

Provider adapters (`LLMProvider`, `TranscriptionProvider`) keep business logic identical; only the env and image change.

### Multi-container strategy (ECS)

Split by **role**, not by duplicating app logic:

```text
                    ALB
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
  rre-dev-ui (slim)           rre-dev-api (profile-dependent)
  Streamlit only              FastAPI + workflow engine
        │                           │
        │                           ├── Cloud: Bedrock + Transcribe + RDS + S3
        └───────────────────────────┴── Local/dev (Dockerfile): Ollama + Whisper + pyannote
                                    └── (optional interim) same fat image until Transcribe ships
```

| Container | Always separate? | Cloud contents | Local contents |
|-----------|------------------|----------------|----------------|
| **ui** | Yes | Streamlit, httpx → ALB `/api` | Same |
| **api** | Yes | Slim: no torch/pyannote/whisper | Full: torch, pyannote, faster-whisper, ffmpeg |

**Do not** add a third “ML worker” container in cloud once Transcribe is live — that would reintroduce ops burden without benefit. A worker container only makes sense as a **temporary** bridge if cloud must run Whisper before Transcribe lands.

### Build strategy — avoid bloat

Use **two Docker build targets** from one repo (not two codebases):

| File / target | Purpose |
|---------------|---------|
| `Dockerfile` / `target: local` | Current full stack — local dev, Windows/WSL, integration testing |
| `Dockerfile.cloud` / `target: cloud` | Slim API — no torch, pyannote, faster-whisper; Bedrock + Transcribe SDK only |
| `Dockerfile.ui` | Unchanged — already slim |

CI/CD for AWS builds and pushes **`rre-dev-api:cloud`** only. Local developers build `Dockerfile` as today.

Example cloud API dependencies (conceptual):

```text
fastapi, uvicorn, sqlalchemy, psycopg, boto3, pydantic-settings, alembic
# NOT: torch, torchaudio, pyannote.audio, faster-whisper
```

### Migration phases

| Phase | API image | Audio ingest | LLM |
|-------|-----------|--------------|-----|
| **Now (interim)** | Fat — torch + pyannote + Whisper | Local ML in container | Ollama off-host or degraded health |
| **P0-AWS-7** | Fat or slim + Bedrock | Still Whisper/pyannote until P1-1 | Bedrock |
| **P1-1 target** | **Slim cloud image** | Amazon Transcribe | Bedrock |
| **Local always** | Fat `Dockerfile` | Whisper + pyannote | Ollama |

Interim fat cloud image is acceptable for **proving ECS deploy**; plan to **shrink** as soon as `TRANSCRIPTION_PROVIDER=transcribe` and `LLM_PROVIDER=bedrock` pass burn-in.

### Simplicity rules

1. **One repo, one workflow engine** — no forked cloud/local business logic.
2. **Providers selected by env** — not by `#ifdef AWS`.
3. **Two API images max** — `local` and `cloud`; UI stays one image.
4. **No model files in cloud image** — use Bedrock model IDs and Transcribe API.
5. **ffmpeg only where needed** — local/interim API; omit from slim cloud image when Transcribe owns ingest.

### Model size in cloud

With Bedrock + Transcribe, cloud can use **larger effective models** (e.g. Claude Sonnet, longer context) without enlarging the container or task memory for weights. Scale Fargate CPU/memory for **Python + JSON**, not for GGUF/Ollama or Whisper checkpoints. Full multidisciplinary workflows become a **cost/latency** question, not a **disk/RAM fit** question.

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
| 3. `LLMProvider` + Bedrock spike | RRE | — | [ ] |
| 4. Dockerfile + local smoke | RRE | — | ✓ |
| 5. `infra/dev/` minimal (ECR, ECS, RDS, ALB, logs) | RRE | Step 1 | ✓ |
| 6. `deploy-dev.yml` on `phase-m0-docs` | RRE | Steps 4–5 | ✓ (pending first run) |
| 7. Quick Review on Bedrock in dev | RRE | Step 6 | [ ] |
| 8. Transcribe path | RRE | Step 7 | [ ] |
| 9. PR `phase-m0-docs` → `main` | RRE | Stable dev | [ ] |

---

## 11. Open questions

| Question | Options | Decision by |
|----------|---------|-------------|
| ECS Fargate vs EC2 GPU for interim Whisper | Fargate only if Transcribe is fast-follow | After Transcribe spike |
| Single vs split ECS services (API + UI) | Split recommended (independent scale/restart) | Infra PR |
| Bedrock model default | Claude 3.5 Sonnet vs Llama 3.1 70B | After JSON spike |
| Public ALB vs VPN-only | ALB + API key for dev; document IP allowlist | Security preference |
| NAT gateway | Required if tasks need outbound non-AWS; avoid for no-egress goal | Network design |
| Slim cloud image cutover | After Bedrock only vs after Transcribe too | After P1-1 spike |
| `Dockerfile.cloud` naming | Separate file vs multi-stage `target` | Infra PR |

---

## 12. Related documents

- [implementing.md](implementing.md) — active priorities (critical → significant → materially important)
- [aws-backbone architecture](https://github.com/SethDKelly/aws-backbone/blob/main/docs/architecture.md)
- [aws-backbone GitHub Actions guide](https://github.com/SethDKelly/aws-backbone/blob/main/docs/github-actions.md)
- [../user/deployment.md](../user/deployment.md) — legacy local deployment
