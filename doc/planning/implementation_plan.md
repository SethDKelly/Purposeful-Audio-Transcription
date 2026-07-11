# Implementation Plan

Active plan for the **Relationship Reasoning Engine (RRE)**. This document supersedes the forward-looking sections of [18_post_v0.3_plan.md](18_post_v0.3_plan.md).

| | |
|---|---|
| **Status** | **v0.5.0 AWS pivot in progress** on branch `phase-m0-docs` |
| **Strategy** | **AWS dev deployment** (account `521018312783`, `us-east-2`) via [aws-backbone](https://github.com/SethDKelly/aws-backbone); local path for prompt/module dev only |
| **Baseline** | MVP (A–G) + post-MVP (H–L) in **v0.3.0**; audio/diarization (M, M1.5, M2 core) + Ollama JSON fixes on branch |
| **Tests** | 144 passing |
| **Nice-to-have backlog** | [backlog.md](backlog.md) |
| **AWS detail** | [aws-deployment.md](aws-deployment.md) |
| **Design anchors** | [../design/01_product_vision_and_scope.md](../design/01_product_vision_and_scope.md) · [15_future_roadmap.md](15_future_roadmap.md) |
| **Deploy (legacy local)** | [../user/deployment.md](../user/deployment.md) · [../user/model-setup.md](../user/model-setup.md) |

**Scope rule:** Items here **need to ship** or **materially improve** reliability, deployability, or core product value. Speculative enhancements, alternate UIs, and local-only polish live in [backlog.md](backlog.md).

---

## Document map

| Document | Purpose |
|----------|---------|
| **This document** | Prioritized implementation plan (critical → important → deferred) |
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

Application feature work (workflows, ontology, cases) is **paused** until P0-AWS deploy substrate is green and Bedrock path is proven.

---

## 2. Platform reality

### Local (dev-only)

Transcript-first workflows remain viable locally for prompt/module development. Full audio ingest on native Windows is **not** a primary path. Optional local Docker guidance is in [backlog.md](backlog.md).

### AWS dev (primary)

| Layer | aws-backbone today | RRE must add (app repo) |
|-------|-------------------|-------------------------|
| **Identity / CI** | `dev-github-deploy`, GitHub OIDC, permission boundaries | ✓ Repo in `github_repositories`; `rre-dev-*` IAM prefix |
| **Runtime** | — | ECS Fargate, ALB, ECR images |
| **Data** | Terraform state S3 only | RDS PostgreSQL, S3 uploads, Secrets Manager |
| **LLM** | — | Amazon Bedrock (target); Ollama local dev only |
| **ASR / diarization** | — | Amazon Transcribe (target); Whisper/pyannote interim |
| **Logging** | — | CloudWatch Logs, structured JSON, correlation IDs |
| **Network** | — | VPC private subnets + VPC endpoints; block egress during inference |

**Constraint:** During transcript analysis, transcription, and synthesis, the application must **not** call external APIs (Ollama off-host, Hugging Face, public model registries). All model operations use AWS services or in-VPC endpoints.

### Hybrid cloud/local (target)

One codebase; **two runtime profiles** via env + **two API images** (see [aws-deployment.md §5–6](aws-deployment.md)):

| Profile | API image | LLM | Audio ingest |
|---------|-----------|-----|--------------|
| **Local** | `Dockerfile` (full) | Ollama | Whisper + pyannote + ffmpeg |
| **Cloud (target)** | `Dockerfile.cloud` (slim) | Bedrock | Amazon Transcribe |
| **Cloud (interim)** | `Dockerfile` (full) | Bedrock when wired | Whisper/pyannote until Transcribe |

Multi-container on ECS: **api** + **ui** (already split). No third ML worker in cloud once Transcribe is live.

---

## 3. Priority framework

| Level | Meaning | When |
|-------|---------|------|
| **Critical (P0-AWS)** | Deploy foundation — blocks cloud testing and Bedrock validation | **Now** |
| **Important (P1)** | Core product on AWS dev — inference migration, trust, workflows | After first green deploy |
| **Deferred (P2)** | Application depth — ontology, cases, customization | After Quick Review + Full MVP on Bedrock |
| **Backlog** | [backlog.md](backlog.md) — alternate UIs, local polish, research tooling | Pull in only when validated |

---

## 4. Implementation plan (priority order)

Work top to bottom within each tier.

---

### P0-AWS-1 — Architecture & model strategy

**Goal:** Written target architecture and inference decisions before provider code lands.

| # | Task | Status |
|---|------|--------|
| AWS-1a | Publish [aws-deployment.md](aws-deployment.md) — VPC, ECS, RDS, S3, Bedrock, Transcribe, audio decode, hybrid profiles | ✓ |
| AWS-1b | **LLM evaluation:** Bedrock Converse API + structured JSON vs alternatives | [ ] |
| AWS-1c | **ASR evaluation:** Amazon Transcribe (+ speaker labels) vs containerized Whisper/pyannote | [ ] |
| AWS-1d | Define **no-egress** network model — VPC endpoints for Bedrock, Transcribe, S3, Secrets Manager, CloudWatch, ECR | [ ] |
| AWS-1e | Decision: Ollama adapter for local dev only; Bedrock as AWS default | ✓ (documented) |

**Acceptance:** AWS service map agreed; adapter boundaries documented.

---

### P0-AWS-2 — aws-backbone integration ✓

**Goal:** Enable GitHub Actions deploy for RRE **without modifying MinneAnalytics settings**.

| # | Task | Status |
|---|------|--------|
| AWS-2a | Add `SethDKelly/Purposeful-Audio-Transcription` to `github_repositories` | ✓ |
| AWS-2b | Extend IAM with **`rre-dev-*`** prefix (keep `minneanalytics-dev-*` unchanged) | ✓ |
| AWS-2c | Document backbone changes in [aws-deployment.md](aws-deployment.md) | ✓ |
| AWS-2d | Merge backbone PR to `main` before first RRE deploy | ✓ |

**Merged:** aws-backbone `main` @ `3d14411`.

---

### P0-AWS-3 — Observability & debuggability

**Goal:** Errors in AWS are logged, searchable, and actionable without transcript leakage.

| # | Task | Status |
|---|------|--------|
| AWS-3a | Structured JSON logs (`LOG_JSON=true`): `request_id`, `workflow_run_id`, `module_run_id`, `module_id`, `error_type` | [ ] |
| AWS-3b | Middleware: propagate **`X-Request-ID`** / generate UUID per request | [ ] |
| AWS-3c | Log exception chains in `module_runner`, `workflow_engine`, `output_parser` at ERROR (model id, retry count — not prompt text) | [ ] |
| AWS-3d | CloudWatch log groups `/rre/dev/{service}` | ✓ (Terraform) |
| AWS-3e | Document **CloudWatch Logs Insights** queries for common failures | [ ] |
| AWS-3f | Deploy smoke: ECS task + ALB target health beyond `/api/health` | [ ] |

**Acceptance:** Operator traces a failed Quick Review from ALB → API log → `module_run_id` → error class without SSH.

---

### P0-AWS-4 — Containerization for ECS ✓

**Goal:** Production-style images; no host venv on AWS.

| # | Task | Status |
|---|------|--------|
| AWS-4a | `Dockerfile` — API (FastAPI + uvicorn), system ffmpeg | ✓ |
| AWS-4b | `Dockerfile.ui` — Streamlit | ✓ |
| AWS-4c | Diarization deps in core image (pyannote + torch) | ✓ |
| AWS-4d | `.dockerignore`, healthcheck endpoints | ✓ |
| AWS-4e | ECR repositories `rre-dev-api`, `rre-dev-ui` (Terraform) | ✓ |

---

### P0-AWS-5 — `infra/dev/` Terraform

**Goal:** RRE-owned infrastructure; separate state from backbone and MinneAnalytics.

| # | Task | Status |
|---|------|--------|
| AWS-5a | Terraform root `infra/dev/` — backend key `purposeful-audio-transcription/dev/terraform.tfstate` | ✓ |
| AWS-5b | VPC (default), security groups, ALB | ✓ |
| AWS-5c | ECS cluster + Fargate services, `rre-dev-*` execution/task roles | ✓ |
| AWS-5d | RDS PostgreSQL (dev sizing) | ✓ |
| AWS-5e | S3 bucket for uploads / temp (lifecycle delete) | ✓ |
| AWS-5f | Secrets Manager: `DATABASE_URL` | ✓ |
| AWS-5g | Secrets Manager: `HF_TOKEN` (interim pyannote until Transcribe) | [ ] |
| AWS-5h | VPC endpoints — Bedrock, Transcribe, S3, Secrets Manager, CloudWatch, ECR | [ ] |
| AWS-5i | IAM task role: scoped `bedrock:InvokeModel`, Transcribe, S3 | [ ] |
| AWS-5j | CloudWatch log groups + retention | ✓ |

**Acceptance:** `terraform apply` creates dev stack; API reachable via ALB; no-egress path for inference once 5g–5i complete.

---

### P0-AWS-6 — GitHub Actions deploy

**Goal:** Push to `phase-m0-docs` deploys to AWS dev for testing.

| # | Task | Status |
|---|------|--------|
| AWS-6a | `.github/workflows/deploy-dev.yml` — OIDC → `dev-github-deploy` | ✓ |
| AWS-6b | Jobs: test → build/push ECR → terraform apply → ECS stable wait | ✓ |
| AWS-6c | Trigger: `push` to `phase-m0-docs` + `workflow_dispatch` | ✓ |
| AWS-6d | Smoke step: `GET /api/health` via ALB | ✓ |
| AWS-6e | First **green** workflow run on `phase-m0-docs` | [ ] |
| AWS-6f | Switch default branch trigger to `main` after stable | [ ] |

---

### P0-AWS-7 — LLM provider abstraction & Bedrock

**Goal:** Replace direct Ollama coupling; prove Quick Review on Bedrock in dev.

| # | Task | Status |
|---|------|--------|
| AWS-7a | `LLMProvider` protocol — `chat()`, `stream()`, `health_check()` | [ ] |
| AWS-7b | `OllamaProvider` — wrap existing `OllamaService` (local dev) | [ ] |
| AWS-7c | `BedrockProvider` — boto3 `bedrock-runtime` Converse API; JSON via tool/schema or prompt | [ ] |
| AWS-7d | Settings: `LLM_PROVIDER=ollama|bedrock`, `BEDROCK_MODEL_ID`, region | [ ] |
| AWS-7e | Spike: run `relationship_conversation_analysis` on Bedrock in dev | [ ] |
| AWS-7f | Map module YAML `ollama_model` → generic `model_id` (backward compatible) | [ ] |

**Acceptance:** Quick Review completes in AWS dev using Bedrock; no HTTP calls outside VPC during module run.

---

### P1-1 — ASR migration (Amazon Transcribe)

**Goal:** Remove runtime dependency on Whisper/pyannote/Hugging Face in AWS.

| # | Task | Status |
|---|------|--------|
| P1-1a | `TranscriptionProvider` abstraction | [ ] |
| P1-1b | Amazon Transcribe adapter — async job, speaker labels | [ ] |
| P1-1c | S3 upload → Transcribe → labeled turns → existing ingest | [ ] |
| P1-1d | Keep Whisper path for local dev only (`TRANSCRIPTION_PROVIDER=whisper`) | [ ] |

**Audio decode:** [aws-deployment.md §5](aws-deployment.md) — ffmpeg CLI locally/interim; Transcribe in cloud.

---

### P1-2 — Slim cloud API image (hybrid build)

**Goal:** Shrink ECS API container after Bedrock + Transcribe; keep full `Dockerfile` for local.

| # | Task | Status |
|---|------|--------|
| P1-2a | `Dockerfile.cloud` — API without torch, pyannote, faster-whisper | [ ] |
| P1-2b | CI: build/push cloud image for AWS; full image for local/dev tests | [ ] |
| P1-2c | Terraform/ECS env: `LLM_PROVIDER=bedrock`, `TRANSCRIPTION_PROVIDER=transcribe` | [ ] |
| P1-2d | Reduce Fargate task size after slim cutover | [ ] |
| P1-2e | Document local vs cloud profile in [model-setup.md](../user/model-setup.md) | [ ] |

**Depends on:** P0-AWS-7, P1-1

---

### P1-3 — Data handling & trust

**Goal:** Sensitive data lifecycle and logging boundaries on AWS dev.

| # | Task | Status |
|---|------|--------|
| P1-3a | Temp audio deletion — S3 lifecycle + app `finally` | [ ] |
| P1-3b | `DELETE /api/transcripts/{id}` cascade | [ ] |
| P1-3c | Log redaction — no transcript body in CloudWatch | [ ] |
| P1-3d | Privacy copy updated for AWS (data stays in account/VPC) | [ ] |

---

### P1-4 — Workflow completeness (Phase N)

**Goal:** Full multidisciplinary + research workflows validated on AWS dev.

| # | Task | Status |
|---|------|--------|
| P1-4a | `full_multidisciplinary.yaml` + `research_oriented.yaml` | [ ] |
| P1-4b | Background default for long workflows; sync module limit | [ ] |
| P1-4c | Burn-in on AWS dev with Bedrock | [ ] |

**Depends on:** P0-AWS-7

---

### P1-5 — CI & deploy reliability

**Goal:** Reproducible builds and provider testing without live Ollama/Bedrock in every CI run.

| # | Task | Status |
|---|------|--------|
| P1-5a | Pinned lockfile (`uv.lock` or equivalent) in CI and Docker builds | [ ] |
| P1-5b | Golden LLM output fixtures — record/replay for integration tests | [ ] |
| P1-5c | Container smoke test in CI — health + one mocked module run | [ ] |

---

### P2 — Deferred application features

Resume after AWS dev is stable and Quick Review + Full MVP pass on Bedrock. Detail in [18_post_v0.3_plan.md](18_post_v0.3_plan.md).

| Phase | Focus | Key deliverables |
|-------|-------|------------------|
| **P2-O** | Ontology & constructs | Construct population in module outputs; richer knowledge graph |
| **P2-P** | Cases & session series | Case files, cross-session progress, comparative analysis over time |
| **P2-Q** | Custom workflows | User-defined module chains, depth/tone toggles |
| **P2-R** | Streamlit polish | Finding feedback UI, workflow cancellation, UX gaps |

Nice-to-have variants (React UI, advanced redaction rules, eval dashboards) stay in [backlog.md](backlog.md).

---

## 5. Suggested release milestones

| Release | Theme |
|---------|--------|
| **v0.4.x** (branch today) | Diarization, sliced transcription, Ollama JSON fixes |
| **v0.5.0** | AWS dev deploy — ECS, Bedrock spike, CloudWatch, GitHub Actions |
| **v0.5.1** | Transcribe + slim cloud API image |
| **v0.6.0** | Full multidisciplinary workflow on AWS; data handling & trust |
| **v0.7.0** | Ontology + cases (P2-O, P2-P) |
| **v1.0.0** | Stable `main` deploy + API contract |

---

## 6. Explicitly out of scope

- Modifying **MinneAnalytics** IAM, state, or deploy workflows in aws-backbone
- Multi-user SaaS, billing, RBAC beyond API key
- Production AWS account / `prod-github-deploy` (deferred in aws-backbone roadmap)
- Runtime Hugging Face or public model downloads in AWS deploy (target state)
- Hardcoded per-model branches (use provider + `model_id` config)
- torchcodec migration (see [aws-deployment.md §5](aws-deployment.md))

---

## 7. Decision log

| Decision | Rationale |
|----------|-----------|
| **AWS over local Windows** | ML stack fragility; personal AWS account + backbone already exists |
| **Bedrock over Ollama (AWS)** | Native AWS, VPC endpoints, no self-hosted LLM ops; no-egress fit |
| **Transcribe over Whisper (AWS)** | Removes GPU/container ASR burden and HF token dependency |
| **Ollama retained for local dev** | Fast iteration on prompts/modules without AWS cost |
| **`phase-m0-docs` until stable** | Safe AWS testing before `main` PR |
| **`rre-dev-*` IAM prefix** | Isolation from MinneAnalytics |
| **Hybrid profiles** | Slim cloud API + full local Docker; providers via env |
| **Audio decode** | ffmpeg CLI local/interim; Transcribe in cloud |
| **App infra in RRE repo** | aws-backbone is IAM/OIDC only |
| **Pause app features until P0-AWS green** | Deploy substrate blocks meaningful cloud validation |
| **M2 UI polish → backlog** | Local/interim only; Transcribe path is cloud priority |

---

## 8. Next steps

```text
[x] aws-backbone merged — OIDC + rre-dev-* IAM prefix
[x] Dockerfile + Dockerfile.ui + infra/dev/ Terraform + deploy-dev.yml
[ ] First successful GitHub Actions deploy on phase-m0-docs
[ ] P0-AWS-3 — LOG_JSON, request_id middleware, error context
[ ] P0-AWS-5g–5i — HF_TOKEN secret, VPC endpoints, Bedrock/Transcribe IAM
[ ] P0-AWS-7 — LLMProvider + BedrockProvider spike
[ ] P1-1 → P1-2 — Transcribe then slim cloud image
```

---

## Appendix — completed phases

### MVP (Phases A–G) ✓ · Post-MVP (H–L) ✓ · M0 ✓

Domain, modules, workflows, synthesis, exports, PostgreSQL option, exploration APIs.

### Phase M / M1.5 / M2 core ✓ · Ollama reliability ✓

Diarization, timeline smoothing, sliced transcription mode, JSON mode fixes.

### Superseded (local-first P0)

Windows troubleshooting, local Ollama tuning, local Docker Compose, air-gapped local deploy — see [backlog.md](backlog.md).
