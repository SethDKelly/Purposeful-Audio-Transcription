# Completed Work

Record of shipped capabilities for the **Relationship Reasoning Engine (RRE)** through **July 2026**. Active priorities: [implementing.md](implementing.md). Optional future work: [backlog.md](backlog.md).

| | |
|---|---|
| **Current branch** | `main` @ **v1.0.0** |
| **Baseline release** | **v1.0.0** — workflow hardening ([releases/v1.0.0.md](../releases/v1.0.0.md)) |
| **Next** | **Post-v1.0** backlog ([implementing.md](implementing.md) · [future_considerations.md](future_considerations.md)) |
| **Deferred** | [future_considerations.md](future_considerations.md) |
| **Tests** | ~220+ passing locally / CI |
| **AWS account** | `521018312783`, `us-east-2` |
| **Architecture detail** | [aws-deployment.md](aws-deployment.md) |
| **Docs root** | `docs/` (renamed from `doc/` in v0.7.0) |

---

## v1.0.0 — Workflow hardening (July 2026)

| Area | Delivered |
|------|-----------|
| Dedicated worker | ECS worker process; cancel / timeout / retries |
| Workflow DAG | `steps` / `depends_on` / parallel waves |
| Custom workflows | API + Streamlit builder |
| Long transcripts | Balanced sampling + length assessment |
| Safety mode | Risk scan, banner, framing, exploratory skip |
| Migrations | Alembic `010`–`011` |

---

## v0.9.0 — Cases + longitudinal (July 2026)

| Area | Delivered |
|------|-----------|
| Cases | `cases` + transcript session fields; CRUD/assign API; Streamlit dashboard |
| Longitudinal | Compare earliest vs latest sessions; `longitudinal_synthesis` module |
| Report package | ZIP: manifest + report + evidence appendix + findings index |
| Finding feedback | Ratings + notes on findings; API + finding-card UI |
| Migrations | Alembic `008`–`009` |
| Module library | **14 modules** (adds longitudinal synthesis) |

---

## v0.8.0 — Structured persistence + graph (July 2026)

| Area | Delivered |
|------|-----------|
| Findings persistence | Normalized tables + write on module complete; exploration prefers DB |
| Constructs / relationships | Ontology-validated persistence; knowledge graph from DB |
| Merge + convergence | Cross-module dedup; strong/moderate/weak/contested scores |
| Exploration UI | Structured inventory tables + `GET …/structured-graph` |
| Synthesis | Meta-synthesis primary input = structured inventory |
| Migrations | Alembic `005`–`007` |

---

## v0.7.0 — Trust, prep, ontology (July 2026)

| Area | Delivered |
|------|-----------|
| Secure UAT | Shared API key (UI+API), generic errors + `request_id`, privacy captions, export redaction default-on, optional ACM HTTPS Terraform |
| Transcript preparation | Edit/exclude turns, evidence rebuild, `analysis_ready` gate, Streamlit prepare UX |
| Ontology vocabulary v1 | `config/ontology/`, `OntologyRegistry`, aliases, module validation |
| Construct expectations | `expected_constructs` on modules; soft coverage warnings on runs |
| Golden evaluation | GT001/GT002 fixtures, signal assertions, golden pytest suite, manual rubric |
| Telemetry | Module latency/tokens/cost; workflow `telemetry_summary` |
| Deploy policy | Tag `v*.*.*` or manual deploy only; pause when idle |
| Docs | `docs/` rename; architecture/API/user guides updated |

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
| Index | [docs/README.md](../README.md) |
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
| AWS-4a | `Dockerfile` — API + uvicorn + ffmpeg (+ `.[local]` Whisper stack) | ✓ |
| AWS-4b | `Dockerfile.ui` — Streamlit (core deps only) | ✓ |
| AWS-4c | Diarization deps in **local** image (`.[local]`) | ✓ |
| AWS-4d | `.dockerignore`, container health checks (`/api/live`) | ✓ |
| AWS-4e | ECR repositories `rre-dev-api`, `rre-dev-ui` | ✓ |
| — | `Dockerfile.cloud` — slim API (Bedrock + Transcribe, no torch) | ✓ |

---

## AWS pivot — Terraform `infra/dev/` (P0-AWS-5)

| # | Task | Status |
|---|------|--------|
| AWS-5a | State key `purposeful-audio-transcription/dev/terraform.tfstate` | ✓ |
| AWS-5b | VPC (default), security groups, ALB | ✓ |
| AWS-5c | ECS cluster + Fargate services, execution/task roles | ✓ |
| AWS-5d | RDS PostgreSQL (dev sizing) | ✓ |
| AWS-5e | S3 uploads bucket with lifecycle delete | ✓ |
| AWS-5f | Secrets Manager: `DATABASE_URL` | ✓ |
| AWS-5g | Secrets Manager: `HF_TOKEN` | **Skipped** (Transcribe on AWS) |
| AWS-5i | Task role: Bedrock invoke, S3, Transcribe, CloudWatch | ✓ |
| AWS-5j | CloudWatch log groups + retention | ✓ |
| AWS-5h | VPC endpoints Stage A + Stage B (no public IP; S3 prefix-list + DNS egress) | ✓ |

---

## AWS pivot — CI/CD (P0-AWS-6)

| # | Task | Status |
|---|------|--------|
| AWS-6a | `.github/workflows/deploy-dev.yml` — OIDC → `dev-github-deploy` | ✓ |
| AWS-6b | Jobs: test → build/push ECR → terraform apply → ECS stable wait | ✓ |
| AWS-6c | Trigger: was `workflow_dispatch` only during slim cutover | ✓ |
| AWS-6d | Smoke: health payload + workflows + UI + ECS + TGs | ✓ |
| AWS-6e | First green deploy on `phase-m0-docs` | ✓ |
| AWS-6f | Switch default trigger to `main` (push + `workflow_dispatch`) | ✓ |
| AWS-6g | Pause AWS when idle (standing ops practice) | ✓ `pause-dev.yml` + docs |
| — | `.github/workflows/pause-dev.yml` — scale ECS to 0, stop RDS | ✓ |
| — | Pause/resume documented in [infra/dev/README.md](../../infra/dev/README.md) + [aws-operations.md](../developer/aws-operations.md) | ✓ |

---

## AWS pivot — LLM provider layer (P0-AWS-7)

| # | Task | Status |
|---|------|--------|
| AWS-7a | `LLMProvider` protocol — `chat()`, `stream()`, `health_check()` | ✓ |
| AWS-7b | `OllamaProvider` — wraps `OllamaService` | ✓ |
| AWS-7c | `BedrockProvider` — Converse API + JSON mode | ✓ |
| AWS-7d | Settings: `LLM_PROVIDER`, `BEDROCK_MODEL_ID`, region | ✓ |
| AWS-7e | Quick Review burn-in on AWS dev — Claude Sonnet 4.5 (`us.…` profile); 3/3 modules completed | ✓ |
| AWS-7f | Module YAML `model_id` (backward compatible with `ollama_model`) | ✓ |
| — | Health endpoint reports `llm_provider`, `llm_available`; `/api/live` for ALB | ✓ |
| — | Marketplace subscribe on task role; Converse timeout; output schema coercion | ✓ |

---

## AWS pivot — ASR + slim image (P1-1, P1-2)

| # | Task | Status |
|---|------|--------|
| P1-1a–d | `TranscriptionProvider`, Whisper + Amazon Transcribe adapters, route wiring | ✓ |
| P1-2a–c,e | `Dockerfile.cloud`, CI cloud build, ECS Transcribe env, model-setup docs | ✓ |
| P1-2d | Lower Fargate sizing | ✓ API 1024/2048 (memory cut; 512/2048 rolled back after health timeouts) |
| — | Live AWS Transcribe + Quick Review under Stage B | ✓ 2026-07-14 |

---

## Tier 2 — Trust, workflows, AWS-only prune (P1-3, P1-4, P1-7)

| # | Task | Status |
|---|------|--------|
| P1-3 | Cascade DELETE, log redaction, retention, audit, privacy copy | ✓ |
| P1-4a–e | `full_multidisciplinary`, `research_oriented`, background defaults, sync limit, mocked tests | ✓ |
| P1-7 | Remove Ollama/Whisper/pyannote/`.[local]`/fat Dockerfile; Bedrock + Transcribe only; docs AWS-primary | ✓ |
| P1-4f | Live AWS burn-in for long suites | **In progress** (2026-07-14+) — research_oriented completed on Bedrock; full_multidisciplinary running / affirm |
| P1-5d–f | Pre-commit + config validation; multi-worker uvicorn + ALB health; synthesis `findings` rollup | ✓ on branch (merge with burn-in closeout) |

### Bedrock reliability (shipped on Tier 2 branch)

| Area | Delivered |
|------|-----------|
| JSON-only framework prompts | No “markdown after JSON” dual instruction |
| Bedrock `outputConfig` structured JSON | With prompt fallback if schema rejected |
| Default alternatives for inferred findings | Parser fill so moderate confidence validates |
| Compact meta handoff | Strip `raw_markdown_report` from prior module payloads |
| Synthesis API | Flat `findings` rollup + empty-report validation |
| API health under load | 2 uvicorn workers; ALB unhealthy_threshold 10; deploy min_healthy 0 |

---

## Vision gaps closed (since v0.3.0)

| Vision item | Was | Now |
|-------------|-----|-----|
| Segment speakers from audio | Single-speaker Whisper only | Amazon Transcribe speaker labels |
| Reproducible deployment | Manual venv + host deps | Docker images + ECS Fargate + GitHub Actions |
| Structured logging in cloud | Ad hoc logs | JSON logs + CloudWatch + correlation IDs |
| LLM on AWS | Ollama coupling | Bedrock only (local Ollama removed) |
| ASR on AWS (no HF) | Whisper/pyannote in fat image | Transcribe + slim `Dockerfile.cloud` |
| Dual local/cloud product paths | Hybrid defaults | **AWS-only** product (edit → pytest → Deploy) |
| Long-suite workflows | Quick Review / Full MVP only | + Full Multidisciplinary + Research-oriented |

---

## Release milestones reached

| Release | Theme |
|---------|--------|
| **v0.2.0** | MVP — 4 modules + synthesis, Quick Review workflow |
| **v0.3.0** | Post-MVP — 13 modules, 5 workflows, exploration, PostgreSQL |
| **v0.4.x** | Diarization, sliced transcription, timeline smoothing, Ollama JSON fixes |
| **v0.5.0** (ops) | AWS substrate — folded into v0.5.1 |
| **v0.5.1** | AWS cloud cutover — Transcribe + slim image + Stage B + main deploy/pause |
| **v0.6.0** | Trust + full/research workflows + AWS-only prune + component UAT |
| **v0.7.0** | **Canonical** — secure UAT, transcript prep, ontology, golden fixtures, telemetry |

---

## Key decisions (implemented)

| Decision | Rationale |
|----------|-----------|
| AWS over native Windows | ML stack fragility on Windows; backbone account exists |
| Bedrock over Ollama (AWS) | Native AWS, VPC endpoints, no self-hosted LLM ops |
| Transcribe over Whisper (AWS) | Removes GPU/HF burden in cloud |
| AWS-only product (no local LLM/ASR runtime) | Cost control + one path; pytest uses mocks/SQLite |
| `rre-dev-*` IAM prefix | Isolation from MinneAnalytics |
| App infra in RRE repo | aws-backbone is IAM/OIDC only |
| Docs-only pushes skip deploy | Superseded in v0.7 — deploy on **tag / manual only** |
| Streamlit before React | Faster iteration; APIs exploration-ready |
| Structured Bedrock JSON + repair loop | Claude often drifts; constrained output + coerce layer |
| Multi-worker API under Converse | Protect `/api/live` during burn-in |
