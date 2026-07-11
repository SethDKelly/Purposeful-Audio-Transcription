# Implementation Plan

Active plan for the **Relationship Reasoning Engine (RRE)**. This document supersedes the forward-looking sections of [18_post_v0.3_plan.md](18_post_v0.3_plan.md).

| | |
|---|---|
| **Status** | **v0.5.0 AWS pivot in progress** on branch `phase-m0-docs` |
| **Strategy** | **AWS dev deployment** (account `521018312783`, `us-east-2`) via [aws-backbone](https://github.com/SethDKelly/aws-backbone); local Windows path demoted to dev-only |
| **Baseline** | MVP (A–G) + post-MVP (H–L) in **v0.3.0**; audio/diarization (M, M1.5, M2 core) + Ollama JSON fixes on branch |
| **Tests** | 144 passing |
| **Nice-to-have backlog** | [backlog.md](backlog.md) |
| **AWS detail** | [aws-deployment.md](aws-deployment.md) |
| **Design anchors** | [../design/01_product_vision_and_scope.md](../design/01_product_vision_and_scope.md) · [15_future_roadmap.md](15_future_roadmap.md) |
| **Deploy (legacy local)** | [../user/deployment.md](../user/deployment.md) · [../user/model-setup.md](../user/model-setup.md) |

---

## Document map

| Document | Purpose |
|----------|---------|
| **This document** | Prioritized implementation plan (critical → important) |
| [aws-deployment.md](aws-deployment.md) | AWS architecture, backbone integration, model/logging strategy |
| [backlog.md](backlog.md) | Nice-to-have and deferred enhancements |
| [18_post_v0.3_plan.md](18_post_v0.3_plan.md) | Historical post-v0.3.0 phase detail (M–U) |
| [12_mvp_build_plan.md](12_mvp_build_plan.md) | Original MVP phase definitions |
| [15_future_roadmap.md](15_future_roadmap.md) | Long-term strategic direction |
| **aws-backbone** (separate repo) | IAM, OIDC, `dev-github-deploy` — not application runtime |

---

## 1. Where the project is today

### Delivered (application)

| Area | Status |
|------|--------|
| Transcript paste / upload + evidence index (`Q001…`) | ✓ |
| 13 modules + prompt compiler + structured JSON output | ✓ |
| 5 workflows + synthesis + safety validation | ✓ |
| Exploration APIs + Streamlit Explore tab + exports | ✓ |
| PostgreSQL option, Alembic, background jobs, API key auth | ✓ |
| Speaker diarization + timeline smoothing + sliced transcription (core) | ✓ |
| Ollama reliability fixes — `think=false`, JSON mode, nested JSON parser | ✓ |

### Strategic shift (July 2026)

Local deployment on **native Windows** proved unreliable for the ML stack (Whisper, pyannote, Ollama, GPU/torch). The project now targets **AWS dev deployment** using the personal account managed by **aws-backbone**, with:

- **Models and inference inside AWS** — no outbound calls during model operations
- **GitHub Actions** for deploy (OIDC → `dev-github-deploy`)
- **CloudWatch** for accessible, debuggable error logs
- **Gradual move away from Ollama** toward AWS-native inference (Bedrock primary candidate)
- **Branch `phase-m0-docs`** for initial AWS testing; PR to `main` when stable
- **MinneAnalytics untouched** — separate IAM prefix, state key, and OIDC entry (see [aws-deployment.md](aws-deployment.md))

Application feature work (workflows, ontology, cases) is **paused** until P0-AWS items below are underway and the dev environment accepts a first deploy.

---

## 2. Platform reality

### Local Windows (demoted — dev-only)

Transcript-first workflows remain viable locally for prompt/module development. Audio ingest, diarization, and long Ollama sessions on native Windows are **unsupported as a primary path**. See [backlog.md](backlog.md) for optional local Docker guidance.

### AWS dev (primary)

| Layer | aws-backbone today | RRE must add (app repo) |
|-------|-------------------|-------------------------|
| **Identity / CI** | `dev-github-deploy`, GitHub OIDC, permission boundaries | Add repo to `github_repositories`; `rre-dev-*` IAM prefix |
| **Runtime** | — | ECS (Fargate or EC2+GPU), ALB, ECR images |
| **Data** | Terraform state S3 only | RDS PostgreSQL, S3 uploads, Secrets Manager |
| **LLM** | — | Amazon Bedrock (target); Ollama-on-ECS interim optional |
| **ASR / diarization** | — | Amazon Transcribe (target); Whisper/pyannote interim in container |
| **Logging** | — | CloudWatch Logs, structured JSON, correlation IDs |
| **Network** | — | VPC private subnets + VPC endpoints; block egress during inference |

**Constraint:** During transcript analysis, transcription, and synthesis, the application must **not** call external APIs (Ollama off-host, Hugging Face, public model registries). All model operations use AWS services or in-VPC endpoints with pre-provisioned models.

---

## 3. Priority framework

| Level | Meaning | This sprint |
|-------|---------|-------------|
| **Critical (P0-AWS)** | AWS deploy foundation — blocks cloud testing | **This week** — complete before app feature work |
| **Important (P1)** | Product completeness on AWS dev | After first successful deploy |
| **Deferred (P2)** | Enhancements once AWS path is stable | Cases, ontology, custom workflows |
| **Nice-to-have** | [backlog.md](backlog.md) | React UI, local Docker Compose, Helm |

---

## 4. Implementation plan (priority order)

Work top to bottom. **Do not start P1 application features until P0-AWS-1 through P0-AWS-6 have a documented target and at least one deploy attempt.**

---

### P0-AWS-1 — Architecture & model strategy (this week)

**Goal:** Written target architecture and inference decisions before code changes.

| # | Task | Priority | Status |
|---|------|----------|--------|
| AWS-1a | Publish [aws-deployment.md](aws-deployment.md) — VPC, ECS, RDS, S3, Bedrock, Transcribe | Critical | [ ] |
| AWS-1b | **LLM evaluation:** Amazon Bedrock (Converse API, structured JSON) vs SageMaker vs in-VPC Ollama | Critical | [ ] |
| AWS-1c | **ASR evaluation:** Amazon Transcribe (+ speaker labels) vs containerized Whisper/pyannote | Critical | [ ] |
| AWS-1d | Define **no-egress** network model — VPC endpoints for Bedrock, Transcribe, S3, Secrets Manager, CloudWatch, ECR | Critical | [ ] |
| AWS-1e | Decision: keep Ollama adapter for local dev only; Bedrock as AWS default | Critical | [ ] |

**Acceptance:** Team agrees on AWS service map; module runner has a documented adapter boundary.

**Effort:** 2–3 days

---

### P0-AWS-2 — aws-backbone integration ✓

**Goal:** Enable GitHub Actions deploy for RRE **without modifying MinneAnalytics settings**.

| # | Task | Priority | Status |
|---|------|----------|--------|
| AWS-2a | **aws-backbone PR:** add `SethDKelly/Purposeful-Audio-Transcription` to `github_repositories` | Critical | ✓ |
| AWS-2b | **aws-backbone PR:** extend `app_deploy_iam.tf` + permission boundaries with **`rre-dev-*`** prefix (keep `minneanalytics-dev-*` unchanged) | Critical | ✓ |
| AWS-2c | Document backbone changes in [aws-deployment.md](aws-deployment.md) § Backbone | Critical | ✓ |
| AWS-2d | Merge backbone PR to `main` (auto-apply) before first RRE deploy workflow run | Critical | ✓ |

**Merged:** aws-backbone `main` @ `3d14411` (PR #1, July 2026). CI apply should have updated `dev-github-deploy` trust and IAM policies.

**Do not:** change MinneAnalytics OIDC subjects, `minneanalytics-dev-*` ARNs, or MinneAnalytics Terraform state.

**Acceptance:** `dev-github-deploy` trust includes RRE repo; deploy workflow can create `rre-dev-*` ECS task/execution roles.

**Effort:** 1 day (backbone) + review

---

### P0-AWS-3 — Observability & debuggability (this week)

**Goal:** Errors in AWS are logged, searchable, and actionable without transcript leakage.

| # | Task | Priority | Status |
|---|------|----------|--------|
| AWS-3a | Enable **structured JSON logs** (`LOG_JSON=true`) with standard fields: `request_id`, `workflow_run_id`, `module_run_id`, `module_id`, `error_type` | Critical | [ ] |
| AWS-3b | Middleware: propagate **`X-Request-ID`** / generate UUID per request | Critical | [ ] |
| AWS-3c | Log **exception chains** in `module_runner`, `workflow_engine`, `output_parser` at ERROR with context (model id, retry count — not prompt text) | Critical | [ ] |
| AWS-3d | CloudWatch log group naming convention: `/rre/dev/{service}` | Critical | [ ] |
| AWS-3e | Document **CloudWatch Logs Insights** queries for common failures (JSON parse, empty LLM, transcribe timeout) | Critical | [ ] |
| AWS-3f | Optional: ECS task health + ALB target health in deploy smoke test | Important | [ ] |

**Acceptance:** Operator can trace a failed Quick Review from ALB → API log → module_run_id → error class without SSH.

**Effort:** 2–3 days

---

### P0-AWS-4 — Containerization for ECS ✓

**Goal:** Production-style images; no host venv on AWS.

| # | Task | Priority | Status |
|---|------|----------|--------|
| AWS-4a | `Dockerfile` — API (FastAPI + uvicorn), system ffmpeg | Critical | ✓ |
| AWS-4b | `Dockerfile.ui` — Streamlit | Critical | ✓ |
| AWS-4c | Diarization deps in core image (pyannote + torch) | Important | ✓ |
| AWS-4d | `.dockerignore`, healthcheck endpoints | Critical | ✓ |
| AWS-4e | ECR repositories `rre-dev-api`, `rre-dev-ui` (Terraform) | Critical | ✓ |

**Acceptance:** Image builds in CI; runs locally with `docker run` against mock env; health check passes.

**Effort:** 2–4 days

---

### P0-AWS-5 — `infra/dev/` Terraform ✓

**Goal:** RRE-owned infrastructure in app repo; separate state from backbone and MinneAnalytics.

| # | Task | Priority | Status |
|---|------|----------|--------|
| AWS-5a | Terraform root `infra/dev/` — backend key `purposeful-audio-transcription/dev/terraform.tfstate` | Critical | ✓ |
| AWS-5b | VPC (default), security groups, ALB | Critical | ✓ |
| AWS-5c | ECS cluster + Fargate services, `rre-dev-*` execution/task roles | Critical | ✓ |
| AWS-5d | RDS PostgreSQL (dev sizing) | Critical | ✓ |
| AWS-5e | S3 bucket for uploads / temp (lifecycle delete) | Critical | ✓ |
| AWS-5f | Secrets Manager: DATABASE_URL | Critical | ✓ |
| AWS-5g | VPC endpoints (Bedrock, Transcribe, …) | Critical | deferred |
| AWS-5h | CloudWatch log groups + retention | Critical | ✓ |
| AWS-5i | IAM task role: Bedrock/Transcribe/S3 (scoped) | Critical | deferred |

**Acceptance:** `terraform apply` from `infra/dev/` creates dev stack; API reachable via ALB; logs appear in CloudWatch.

**Effort:** 1–2 weeks

---

### P0-AWS-6 — GitHub Actions deploy ✓

**Goal:** Push to `phase-m0-docs` deploys to AWS dev for testing.

| # | Task | Priority | Status |
|---|------|----------|--------|
| AWS-6a | `.github/workflows/deploy-dev.yml` — OIDC → `dev-github-deploy` | Critical | ✓ |
| AWS-6b | Jobs: test → build/push ECR → terraform apply → ECS stable wait | Critical | ✓ |
| AWS-6c | Trigger: `push` to `phase-m0-docs` + `workflow_dispatch` | Critical | ✓ |
| AWS-6d | Smoke step: `GET /api/health` via ALB | Critical | ✓ |
| AWS-6e | Switch default branch trigger to `main` after stable | Important | [ ] |

**Acceptance:** Push to `phase-m0-docs` updates dev ECS service; health check green.

**Pending:** First successful workflow run after push.

---

### P0-AWS-7 — LLM provider abstraction & Bedrock spike (this week)

**Goal:** Replace direct Ollama coupling with a provider interface; prove one module on Bedrock.

| # | Task | Priority | Status |
|---|------|----------|--------|
| AWS-7a | Introduce `LLMProvider` protocol — `chat()`, `stream()`, `health_check()` | Critical | [ ] |
| AWS-7b | `OllamaProvider` — wrap existing `OllamaService` (local dev) | Critical | [ ] |
| AWS-7c | `BedrockProvider` — boto3 `bedrock-runtime` Converse API; JSON via tool/schema or prompt | Critical | [ ] |
| AWS-7d | Settings: `LLM_PROVIDER=ollama|bedrock`, `BEDROCK_MODEL_ID`, region | Critical | [ ] |
| AWS-7e | Spike: run `relationship_conversation_analysis` on Bedrock in dev | Critical | [ ] |
| AWS-7f | Map module YAML `ollama_model` → generic `model_id` (backward compatible) | Important | [ ] |

**Acceptance:** Quick Review completes in AWS dev using Bedrock; no HTTP calls outside VPC during module run.

**Effort:** 3–5 days

---

### P1-1 — ASR migration (Amazon Transcribe)

**Goal:** Remove runtime dependency on Whisper/pyannote/Hugging Face in AWS.

| # | Task | Priority | Status |
|---|------|----------|--------|
| P1-1a | `TranscriptionProvider` abstraction | Important | [ ] |
| P1-1b | Amazon Transcribe adapter — async job, speaker labels | Important | [ ] |
| P1-1c | S3 upload → Transcribe → labeled turns → existing ingest | Important | [ ] |
| P1-1d | Keep Whisper path for local dev only (`TRANSCRIPTION_PROVIDER=whisper`) | Important | [ ] |

**Effort:** 1 week

---

### P1-2 — Workflow completeness (Phase N)

**Goal:** Full multidisciplinary + research workflows on AWS dev.

| # | Task | Priority | Status |
|---|------|----------|--------|
| P1-2a | `full_multidisciplinary.yaml` + `research_oriented.yaml` | Important | [ ] |
| P1-2b | Background default for long workflows; sync module limit | Important | [ ] |
| P1-2c | Burn-in on AWS dev with Bedrock | Important | [ ] |

**Effort:** 2–3 days (after P0-AWS-7)

---

### P1-3 — Data handling & trust

| # | Task | Priority | Status |
|---|------|----------|--------|
| P1-3a | Temp audio deletion (S3 lifecycle + app `finally`) | Important | [ ] |
| P1-3b | `DELETE /api/transcripts/{id}` cascade | Important | [ ] |
| P1-3c | Log redaction — no transcript body in CloudWatch | Important | [ ] |
| P1-3d | Privacy copy updated for AWS (data stays in your account/VPC) | Important | [ ] |

**Effort:** 2–3 days

---

### P1-4 — M2 polish (sliced transcription — local/interim only)

Remaining sliced-transcription UI progress and fixture validation. **Lower priority** once Transcribe path exists.

| # | Task | Status |
|---|------|--------|
| P1-4a | Streamlit progress for diarize → transcribe | [ ] |
| P1-4b | Fixture audio validation | [ ] |

---

### P2 — Deferred application features

Ontology & constructs (Phase O), cases (P), custom workflows (Q), Streamlit polish (R). See prior plan and [backlog.md](backlog.md). Resume after AWS dev is stable and Quick Review + Full MVP pass on Bedrock.

---

## 5. Suggested release milestones

| Release | Theme |
|---------|--------|
| **v0.4.x** (branch today) | Diarization, sliced transcription, Ollama JSON fixes |
| **v0.5.0** | AWS dev deploy — ECS, Bedrock, CloudWatch, GitHub Actions |
| **v0.5.1** | Amazon Transcribe path; Whisper optional for local dev |
| **v0.6.0** | Full multidisciplinary workflow on AWS |
| **v0.7.0** | Ontology + cases |
| **v1.0.0** | Stable `main` deploy + API contract |

---

## 6. Explicitly out of scope

- Modifying **MinneAnalytics** IAM, state, or deploy workflows in aws-backbone
- Multi-user SaaS, billing, RBAC beyond API key
- Production AWS account / `prod-github-deploy` (deferred in aws-backbone roadmap)
- Runtime Hugging Face or public model downloads in AWS deploy
- Hardcoded per-model branches (use provider + `model_id` config)

---

## 7. Decision log

| Decision | Rationale |
|----------|-----------|
| **AWS over local Windows** | ML stack fragility; personal AWS account + backbone already exists |
| **Bedrock over Ollama (AWS)** | Native AWS, VPC endpoints, no self-hosted LLM ops; better fit for no-egress |
| **Transcribe over Whisper (AWS)** | Removes GPU/container ASR burden and HF token dependency |
| **Ollama retained for local dev** | Fast iteration on prompts/modules without AWS cost |
| **`phase-m0-docs` until stable** | Safe AWS testing before `main` PR |
| **`rre-dev-*` IAM prefix** | Isolation from MinneAnalytics `minneanalytics-dev-*` |
| **Backbone merged (PR #1)** | `dev-github-deploy` trusts RRE repo; IAM scoped to `rre-dev-*` |
| **App infra in RRE repo** | aws-backbone is IAM/OIDC only (same pattern as MinneAnalytics) |
| **Pause app features until P0-AWS** | Deploy substrate blocks meaningful cloud validation |
| **CloudWatch-first observability** | Required for debugging remote failures |

---

## 8. Next steps (this week)

**P0-AWS-2 complete. P0-AWS-4/5/6 implemented — awaiting first deploy run.**

```text
[x] aws-backbone merged — OIDC + rre-dev-* IAM prefix
[x] Dockerfile + Dockerfile.ui + infra/dev/ Terraform + deploy-dev.yml
[ ] First successful GitHub Actions deploy on phase-m0-docs
[ ] P0-AWS-3 — LOG_JSON, request_id middleware, error context in module_runner
[ ] P0-AWS-7 — LLMProvider + BedrockProvider spike
[ ] VPC endpoints + Bedrock IAM (after first deploy green)
```

---

## Appendix — completed phases

### MVP (Phases A–G) ✓ · Post-MVP (H–L) ✓ · M0 ✓

See prior revisions. Domain, modules, workflows, synthesis, exports, PostgreSQL option, exploration APIs.

### Phase M / M1.5 / M2 core ✓ · Ollama reliability ✓

Diarization, timeline smoothing, sliced transcription mode, JSON mode fixes. M2 UI polish deferred to P1-4.

### Superseded priorities (local-first P0)

Windows troubleshooting (P0-1), local Ollama tuning (P0-2), local Docker Compose (P0-4), air-gapped local deploy (P2-5) — moved to [backlog.md](backlog.md) or folded into AWS equivalents.
