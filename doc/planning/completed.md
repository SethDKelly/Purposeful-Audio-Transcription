# Completed Work

Record of shipped capabilities for the **Relationship Reasoning Engine (RRE)** through **July 2026**. Active priorities: [implementing.md](implementing.md). Optional future work: [backlog.md](backlog.md).

| | |
|---|---|
| **Current branch** | `phase-m0-docs` (AWS dev testing) |
| **Baseline release** | **v0.3.0** on `main` — MVP + post-MVP |
| **In progress toward** | **v0.5.0** — AWS dev deploy + Bedrock validation |
| **Tests** | 152+ passing (CI) |
| **AWS account** | `521018312783`, `us-east-2` |
| **Architecture detail** | [aws-deployment.md](aws-deployment.md) |

---

## Application — MVP (Phases A–G, v0.2.0)

Original build goal: analyze a transcript with a representative module subset and evidence traceability.

| Area | Delivered |
|------|-----------|
| Transcript paste / upload | Speaker turn parser, manual correction |
| Evidence index | Quote IDs (`Q001…`) tied to turns |
| Module registry | Metadata schema, versioning, output validation |
| Prompt compiler | Shared + module templates, JSON output contract |
| Core modules + meta-synthesis | Relationship, NVC, Systems, Bias & Reliability, synthesis |
| Workflow engine | Sequential module runs, synthesis step |
| Streamlit UI | Ingest, prepare, analyze, results |
| API shell | FastAPI, health check, core routes |

**MVP principle (still applies):** Reasoning quality and evidence traceability first; prompts remain replaceable.

---

## Application — Post-MVP (Phases H–L, v0.3.0)

| Area | Delivered |
|------|-----------|
| Full module library | **13 modules** with structured JSON output |
| Workflows | **5 workflows**: Quick Review, Conflict Coaching, Mediation Brief, Clinical Exploration, Full MVP |
| Synthesis engine | Meta-synthesis, safety validation, report assembly |
| Exports | Markdown, JSON, PDF, coach summary, mediation brief |
| Exploration APIs | Drill-down, cross-module, follow-up Q&A |
| Streamlit Explore tab | Interactive exploration over stored findings |
| Knowledge graph APIs | Graph data from module outputs (basic Mermaid in UI) |
| Comparative analysis | Compare workflow runs on the same transcript |
| PostgreSQL | Optional backend with Alembic migrations |
| Background jobs | Async workflow execution, resume incomplete runs |
| API key auth | Optional `X-API-Key` middleware |

---

## Documentation — Phase M0

| Area | Delivered |
|------|-----------|
| Doc layout | `user/`, `developer/`, `design/`, `planning/` |
| User guides | Getting started, user guide, deployment, model setup |
| Developer guides | Architecture, development, API reference, contributing, aws-operations |
| Index | [doc/README.md](../README.md) |
| Legacy redirects | Stub paths for moved documents |

---

## Audio & diarization — Phases M, M1.5, M2 (core)

| Area | Delivered |
|------|-----------|
| Diarization service | pyannote wrapper, lazy load, `HF_TOKEN`, graceful fallback |
| Segment alignment | Diarization timeline + Whisper segments → labeled turns (`Person A` / `Person B`) |
| Sliced transcription | Per-speaker audio slices; `TRANSCRIPTION_MODE=sliced` default |
| Timeline smoothing | `diarization_timeline.py` — merge gaps, absorb short flips |
| Transcribe API | Progress events, speaker count, labeled ingest, `transcription_mode` |
| Health reporting | `diarization_ready`, device resolution in `/api/health` |
| Prerequisites script | `scripts/check_prerequisites.py` |
| Streamlit | Speaker count after transcribe; fallback messaging when diarization skipped |

**Pipeline (sliced mode):** diarize → smooth timeline → slice audio → Whisper per slice → labeled turns → ingest.

---

## Ollama reliability (local dev)

| Area | Delivered |
|------|-----------|
| JSON mode | Structured output requests to Ollama |
| `think=false` | Disable reasoning tokens where supported |
| Nested JSON parser | Recover JSON from markdown fences and partial responses |
| Retry / repair loop | Validation failures trigger corrected-output prompt |

---

## AWS pivot — architecture & backbone (P0-AWS-1, P0-AWS-2)

| # | Task | Status |
|---|------|--------|
| AWS-1a | [aws-deployment.md](aws-deployment.md) — VPC, ECS, RDS, S3, Bedrock, Transcribe, hybrid profiles | ✓ |
| AWS-1e | Ollama for local dev; Bedrock as AWS default (documented) | ✓ |
| AWS-2a | GitHub OIDC trust for `Purposeful-Audio-Transcription` | ✓ |
| AWS-2b | `rre-dev-*` IAM prefix (MinneAnalytics unchanged) | ✓ |
| AWS-2c | Backbone integration documented | ✓ |
| AWS-2d | Backbone merged to `main` (`3d14411`) | ✓ |

---

## AWS pivot — observability (P0-AWS-3)

| # | Task | Status |
|---|------|--------|
| AWS-3a | Structured JSON logs — `request_id`, `workflow_run_id`, `module_run_id`, `module_id`, `error_type` | ✓ |
| AWS-3b | `RequestContextMiddleware` — `X-Request-ID` propagate/generate | ✓ |
| AWS-3c | ERROR/WARNING logging in `module_runner`, `workflow_engine`, `output_parser` | ✓ |
| AWS-3d | CloudWatch log groups `/rre/dev/{api,ui}` (Terraform) | ✓ |
| AWS-3e | CloudWatch Logs Insights runbook — [aws-operations.md](../developer/aws-operations.md) | ✓ |
| AWS-3f | Deploy smoke beyond `/api/health` — `scripts/aws-deploy-smoke.sh` in CI | ✓ |

---

## AWS pivot — containerization (P0-AWS-4)

| # | Task | Status |
|---|------|--------|
| AWS-4a | `Dockerfile` — API + uvicorn + ffmpeg | ✓ |
| AWS-4b | `Dockerfile.ui` — Streamlit | ✓ |
| AWS-4c | Diarization deps in core image (pyannote + torch) | ✓ |
| AWS-4d | `.dockerignore`, container health checks | ✓ |
| AWS-4e | ECR repositories `rre-dev-api`, `rre-dev-ui` | ✓ |

---

## AWS pivot — Terraform `infra/dev/` (P0-AWS-5, partial)

| # | Task | Status |
|---|------|--------|
| AWS-5a | State key `purposeful-audio-transcription/dev/terraform.tfstate` | ✓ |
| AWS-5b | VPC (default), security groups, ALB | ✓ |
| AWS-5c | ECS cluster + Fargate services, execution/task roles | ✓ |
| AWS-5d | RDS PostgreSQL (dev sizing) | ✓ |
| AWS-5e | S3 uploads bucket with lifecycle delete | ✓ |
| AWS-5f | Secrets Manager: `DATABASE_URL` | ✓ |
| AWS-5i | Task role: Bedrock invoke, S3, Transcribe, CloudWatch | ✓ |
| AWS-5j | CloudWatch log groups + retention | ✓ |
| AWS-5h | VPC endpoints Stage A + Stage B (no public IP; S3 prefix-list + DNS egress) | ✓ |

---

## AWS pivot — CI/CD (P0-AWS-6, partial)

| # | Task | Status |
|---|------|--------|
| AWS-6a | `.github/workflows/deploy-dev.yml` — OIDC → `dev-github-deploy` | ✓ |
| AWS-6b | Jobs: test → build/push ECR → terraform apply → ECS stable wait | ✓ |
| AWS-6c | Trigger: `push` to `phase-m0-docs` + `workflow_dispatch` | ✓ |
| AWS-6d | Smoke: `GET /api/health` via ALB | ✓ |
| AWS-6e | First green deploy on `phase-m0-docs` | ✓ |
| — | `.github/workflows/pause-dev.yml` — scale ECS to 0, stop RDS | ✓ |
| — | Pause/resume documented in [infra/dev/README.md](../../infra/dev/README.md) | ✓ |

---

## AWS pivot — LLM provider layer (P0-AWS-7, partial)

| # | Task | Status |
|---|------|--------|
| AWS-7a | `LLMProvider` protocol — `chat()`, `stream()`, `health_check()` | ✓ |
| AWS-7b | `OllamaProvider` — wraps `OllamaService` | ✓ |
| AWS-7c | `BedrockProvider` — Converse API + JSON mode | ✓ |
| AWS-7d | Settings: `LLM_PROVIDER`, `BEDROCK_MODEL_ID`, region | ✓ |
| AWS-7e | Quick Review burn-in on AWS dev — Claude Sonnet 4.5 (`us.…` profile); 3/3 modules completed | ✓ |
| AWS-7f | Module YAML `model_id` (backward compatible with `ollama_model`) | ✓ |
| — | Health endpoint reports `llm_provider`, `llm_available` | ✓ |
| — | `boto3` dependency; unit tests for provider and log context | ✓ |
| — | Marketplace subscribe on task role; longer Converse timeout; output schema coercion for Bedrock | ✓ |

---

## Vision gaps closed (since v0.3.0)

| Vision item | Was | Now |
|-------------|-----|-----|
| Segment speakers from audio | Single-speaker Whisper only | pyannote diarization + sliced/overlap pipelines |
| Reproducible deployment | Manual venv + host deps | Docker images + ECS Fargate + GitHub Actions |
| Structured logging in cloud | Ad hoc logs | JSON logs + CloudWatch + correlation IDs |
| LLM on AWS | Ollama-only coupling | `LLMProvider` + Bedrock adapter |

---

## Release milestones reached

| Release | Theme |
|---------|--------|
| **v0.2.0** | MVP — 4 modules + synthesis, Quick Review workflow |
| **v0.3.0** | Post-MVP — 13 modules, 5 workflows, exploration, PostgreSQL |
| **v0.4.x** | Diarization, sliced transcription, timeline smoothing, Ollama JSON fixes |
| **v0.5.0** (partial) | AWS dev substrate — ECS, Terraform, GitHub Actions, LLM abstraction |

---

## Key decisions (implemented)

| Decision | Rationale |
|----------|-----------|
| AWS over native Windows | ML stack fragility on Windows; backbone account exists |
| Bedrock over Ollama (AWS) | Native AWS, VPC endpoints, no self-hosted LLM ops |
| Transcribe over Whisper (AWS target) | Removes GPU/HF burden in cloud |
| Ollama retained locally | Fast prompt/module iteration without AWS cost |
| `rre-dev-*` IAM prefix | Isolation from MinneAnalytics |
| Hybrid profiles | Full local Docker + slim cloud target via env |
| App infra in RRE repo | aws-backbone is IAM/OIDC only |
| `phase-m0-docs` until stable | Safe AWS testing before `main` PR |
| Diarization before full-suite workflow | Multi-speaker turns required for module quality |
| pyannote over Whisper-only diarization | Whisper does not identify speakers |
| Graceful diarization fallback | Users without `HF_TOKEN` still get transcription |
| Streamlit before React | Faster iteration; APIs exploration-ready |
