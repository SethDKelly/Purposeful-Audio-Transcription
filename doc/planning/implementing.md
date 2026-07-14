# Implementing — Active Priorities

Material work in flight or next to ship for the **Relationship Reasoning Engine (RRE)**. Completed: [completed.md](completed.md). Optional future work: [backlog.md](backlog.md).

| | |
|---|---|
| **Status** | **v0.5.1 cutover** — slim deploy green; next: Transcribe + Quick Review burn-in |
| **Branch** | `phase-m0-docs` → PR to `main` when v0.5.0/v0.5.1 acceptance met |
| **Strategy** | AWS dev (account `521018312783`, `us-east-2`) via [aws-backbone](https://github.com/SethDKelly/aws-backbone); local for prompt/module + Whisper |
| **Cost control** | **Pause AWS dev when idle** — Actions → Pause AWS dev (ECS→0, stop RDS). Resume via Deploy. See [aws-operations.md](../developer/aws-operations.md) |
| **Architecture** | [aws-deployment.md](aws-deployment.md) |
| **Design anchors** | [../design/01_product_vision_and_scope.md](../design/01_product_vision_and_scope.md) |

**Scope rule:** Items here **need to ship** or **materially improve** reliability, deployability, or core product value. Work top to bottom within each tier.

**Platform constraint:** During transcript analysis, transcription, and synthesis in AWS, the application must **not** call external APIs (off-host Ollama, Hugging Face, public model registries). Model operations use AWS services or in-VPC endpoints.

**Strategic architecture (unchanged):**

```text
Domain Model → Ontology → Module Definitions → Workflow Engine → Prompt Compiler
  → Structured Findings → Synthesis Engine → Interactive UI
```

Prompts are replaceable; enduring assets are the domain model, evidence/confidence model, workflow design, and structured data.

---

## Priority framework

| Tier | Meaning | When |
|------|---------|------|
| **1 — Critical** | Blocks cloud validation, Bedrock proof, or secure AWS operation | **Now** |
| **2 — Significant** | Core product on AWS dev — inference migration, trust, workflow completeness | After Tier 1 gate |
| **3 — Materially important** | Application depth — ontology, cases, customization | After Quick Review + Full MVP on Bedrock |

---

## Product vision gaps (remaining)

| Vision item | Gap | Tier |
|-------------|-----|------|
| Full Multidisciplinary Suite | No workflow runs all transcript modules + meta-synthesis | 2 (P1-4) |
| Research-oriented analysis | No dedicated workflow | 2 (P1-4) |
| Interactive exploration | No counterfactual presets | 3 (P2-O) / backlog |
| Knowledge graph | APIs exist; constructs/relationships rarely populated | 3 (P2-O) |
| Longitudinal / progress tracking | Same-transcript compare only; no case view | 3 (P2-P) |
| Module customization | Fixed YAML workflows only | 3 (P2-Q) |
| Professional mode | No case files, session series, finding feedback | 3 (P2-P, P2-R) |
| Air-gapped / data sovereignty (local) | AWS VPC Stage B done; local offline guide in backlog | backlog |

---

## Immediate next steps

```text
[x] Manual slim deploy (Dockerfile.cloud + Transcribe env — CI green)
[ ] AWS burn-in: Transcribe audio upload + Quick Review on Bedrock
[ ] Pause AWS dev when burn-in is done (or whenever the stack sits idle)
[ ] P1-2d — Lower Fargate CPU/memory after slim proves healthy
[ ] Close Tier 1 docs: AWS-1c live Transcribe checklist
```

**Slim deploy validated:** `/api/health` → `llm_provider=bedrock`, `llm_available=true`, `database_available=true`, `diarization_ready=false` (expected). CI AWS-3f smoke passed.

**Standing ops rule:** When AWS is not actively used for deploy, burn-in, or demos, run **Pause AWS dev** so Fargate and RDS compute stop. Resume with **Deploy to AWS dev**. Details: [aws-operations.md](../developer/aws-operations.md) · [infra/dev/README.md](../../infra/dev/README.md).

---

## Tier 1 — Critical

Mostly complete. Remaining: **slim-image AWS validation** and closing formal notes.

### Finish P0-AWS — Bedrock proof & secure AWS dev

| # | Task | Notes |
|---|------|-------|
| **AWS-5h** | VPC endpoints Stage B | ✓ |
| **AWS-5g** | Secrets Manager: `HF_TOKEN` | **Skipped** — Transcribe replaces pyannote on AWS |
| **AWS-3f** | Deploy smoke beyond `/api/health` | ✓ |
| **AWS-6f** | Deploy trigger → `main` | After slim cutover stable |
| **AWS-6g** | Pause AWS when idle (standing practice) | ✓ Workflow exists; use after every idle period — [aws-operations.md](../developer/aws-operations.md) |
| **AWS-1b** | Formal LLM evaluation note | ✓ [llm-evaluation-bedrock.md](llm-evaluation-bedrock.md) |
| **AWS-1c** | Formal ASR evaluation note | [asr-evaluation-transcribe.md](asr-evaluation-transcribe.md) — code ✓; live AWS checklist open |
| **AWS-1d** | Document no-egress network model | ✓ Staged A/B in [aws-deployment.md](aws-deployment.md) |

**Tier 1 acceptance (update after slim deploy):** Quick Review on Bedrock ✓ · Stage B no-egress ✓ · Transcribe path proven on AWS · operator can trace ALB → CloudWatch → `module_run_id`.

### Hybrid runtime profiles

| Profile | API image | LLM | Audio ingest |
|---------|-----------|-----|--------------|
| **Local** | `Dockerfile` + `.[local]` | Ollama | Whisper + pyannote |
| **Cloud** | `Dockerfile.cloud` | Bedrock | Amazon Transcribe |

---

## Tier 2 — Significant

Core product on AWS after slim cutover burn-in.

### P1-1 — ASR migration (Amazon Transcribe) ✓ code

**Goal:** Remove Whisper/pyannote/Hugging Face dependency in AWS.

| # | Task | Status |
|---|------|--------|
| P1-1a | `TranscriptionProvider` abstraction | ✓ |
| P1-1b | Amazon Transcribe adapter — async job, speaker labels | ✓ |
| P1-1c | S3 upload → output JSON in bucket → labeled turns | ✓ |
| P1-1d | Whisper path for local (`TRANSCRIPTION_PROVIDER=whisper`) | ✓ |
| — | Routes/orchestrator use `get_transcription_provider()` | ✓ |
| — | Live AWS Transcribe burn-in | **Next** (after slim deploy) |

### P1-2 — Slim cloud API image ✓ code (except sizing)

| # | Task | Status |
|---|------|--------|
| P1-2a | `Dockerfile.cloud` — no torch / pyannote / faster-whisper | ✓ |
| P1-2b | CI builds cloud image; tests use `.[dev,local]` | ✓ (`workflow_dispatch`) |
| P1-2c | ECS `TRANSCRIPTION_PROVIDER=transcribe`, diarization off | ✓ |
| P1-2d | Reduce Fargate CPU/memory | **After** healthy slim deploy |
| P1-2e | Local vs cloud in [model-setup.md](../user/model-setup.md) | ✓ |

**Cutover:** Actions → **Deploy to AWS dev** → Run workflow. Re-enable push-to-branch deploy only after green slim burn-in.

### P1-3 — Data handling & trust

**Goal:** Sensitive data lifecycle and logging boundaries on AWS dev.

| # | Task |
|---|------|
| P1-3a | Temp audio deletion — S3 lifecycle + app `finally` (audit all code paths) |
| P1-3b | `DELETE /api/transcripts/{id}` cascade to runs/reports |
| P1-3c | Log redaction — no transcript body in CloudWatch | Design: [log-redaction.md](log-redaction.md) |
| P1-3d | Privacy copy updated for AWS (data stays in account/VPC) |
| P1-3e | Optional `TRANSCRIPT_RETENTION_DAYS` + cleanup job |
| P1-3f | Audit logging for ingest, export, delete events |

### P1-4 — Workflow completeness (Phase N)

**Goal:** Full multidisciplinary + research workflows validated on AWS dev.

| # | Task |
|---|------|
| P1-4a | `config/workflows/full_multidisciplinary.yaml` — all 12 transcript-input modules → `meta_synthesis` |
| P1-4b | `config/workflows/research_oriented.yaml` — `relationship_conversation_analysis` → `cognitive_analysis` → `narrative_identity_analysis` → `bias_epistemic_quality` → `systems_analysis` → `meta_synthesis` |
| P1-4c | Default `background: true` for long workflows in API/UI |
| P1-4d | `WORKFLOW_SYNC_MODULE_LIMIT` env + UI warning for long suites |
| P1-4e | Integration tests with mocked LLM (pattern from existing workflow tests) |
| P1-4f | Burn-in on AWS dev with Bedrock |

### P1-5 — CI & deploy reliability

**Goal:** Reproducible builds without live Ollama/Bedrock in every CI run.

| # | Task |
|---|------|
| P1-5a | Pinned lockfile (`uv.lock` or equivalent) in CI and Docker builds |
| P1-5b | Golden LLM output fixtures — record/replay for integration tests |
| P1-5c | Container smoke test in CI — health + one mocked module run |

### P1-6 — Evaluation & real-world hardening

Run alongside Tier 2 delivery ([14_testing_evaluation_and_safety.md](../design/14_testing_evaluation_and_safety.md)):

| # | Task |
|---|------|
| P1-6a | Burn-in: `quick_review`, `conflict_coaching`, `full_mvp` on real transcripts (Bedrock on AWS; Ollama locally) |
| P1-6b | Add 3–5 anonymized real scenarios to `tests/fixtures/transcripts/` |
| P1-6c | Track safety validator false positives; adjust patterns |

---

## Tier 3 — Materially important

Application depth after AWS dev is stable and Quick Review + Full MVP pass on Bedrock.

### P2-O — Ontology & construct population

**Problem:** Knowledge graph endpoints work, but LLM outputs usually return empty `constructs` / `relationships`.

| # | Task |
|---|------|
| P2-O1 | Extend `output_schema_instructions.md` with construct minimums for relational modules |
| P2-O2 | `PromptCompiler` optional ontology cheat-sheet section |
| P2-O3 | Validator soft warnings + retry when `constructs` empty (`expects_constructs: true` in module YAML) |
| P2-O4 | Post-parse pass: auto-suggest `construct_ids` from keywords via `config/framework/construct_ontology.yaml` |
| P2-O5 | Exploration presets: `why`, `evidence`, `counterfactual`, `agreement` — API enum + Explore tab buttons |

**Acceptance:** Golden fixture produces ≥2 constructs for relationship + NVC modules; counterfactual preset cites quote IDs.

### P2-P — Cases & longitudinal analysis

| # | Task |
|---|------|
| P2-P1 | Domain model: `Case` entity; optional `Transcript.case_id`; Alembic migration |
| P2-P2 | API: `POST/GET /api/cases`, assign transcript to case |
| P2-P3 | `POST /api/exploration/compare-transcripts` — themes across transcripts in a case |
| P2-P4 | Streamlit: assign to case on ingest; case dashboard with runs and trend summary |

### P2-Q — Custom workflows

| # | Task |
|---|------|
| P2-Q1 | `POST /api/workflows/custom/run` — `{ transcript_id, module_ids[], model?, background? }` |
| P2-Q2 | Validate module existence, input types, `meta_synthesis` last if included |
| P2-Q3 | Streamlit multi-select module picker |
| P2-Q4 | Optional `output_tone` / `inference_depth` in compiler context |

### P2-R — Streamlit professional polish

| # | Task |
|---|------|
| P2-R1 | Human-readable confidence labels (“Directly observed”, etc.) |
| P2-R2 | Streamlit sends `X-API-Key` when `API_KEY` set in UI env |
| P2-R3 | Background workflow toggle in Analyze step |
| P2-R4 | Finding feedback: `POST .../findings/{key}/feedback` helpful/unhelpful + note |
| P2-R5 | Supervision export template — anonymized, limitations prominent |
| P2-R6 | Basic workflow cancellation for background runs |
| P2-R7 | Coaching action plan export — short actionable markdown distinct from coach summary |

---

## Release milestones (target)

| Release | Theme | Status |
|---------|--------|--------|
| **v0.5.0** | AWS dev — ECS, Bedrock, CloudWatch, Stage B, deploy smoke | **Code/ops mostly done** (fat-image era); close on `main` after slim cutover |
| **v0.5.1** | Transcribe + `Dockerfile.cloud` | **Code done**; AWS burn-in next |
| **v0.6.0** | Full multidisciplinary on AWS; data handling & trust (P1-3/P1-4) | Pending |
| **v0.7.0** | Ontology + cases | Pending |
| **v1.0.0** | Stable `main` deploy + API contract | Pending |

---

## Explicitly out of scope

- Modifying **MinneAnalytics** IAM, state, or deploy workflows in aws-backbone
- Multi-user SaaS, billing, RBAC beyond API key
- Production AWS account / `prod-github-deploy`
- Runtime Hugging Face or public model downloads in AWS deploy
- Hardcoded per-model branches (use provider + `model_id` config)
- Graph database backend
- Tone/emotion inference from audio timing
- Distributed queue (Celery/Redis) — thread pool sufficient for private use
- torchcodec migration ([aws-deployment.md §5](aws-deployment.md))

---

## Decision log (active)

| Decision | Rationale |
|----------|-----------|
| **Pause auto-deploy until slim cutover** | Fat image + Stage B caused ALB/ECR thrash; develop Transcribe/slim offline |
| **Pause AWS when idle** | Stop Fargate + RDS compute between sessions; ALB/ECR/storage still bill |
| **Skip AWS-5g HF_TOKEN** | Transcribe replaces pyannote on AWS |
| **S3 output for Transcribe JSON** | Stage B has no public egress — avoid fetching TranscriptFileUri over the internet |
| **`/api/live` for ALB** | Full `/api/health` can hang on Bedrock/deps |
| **Constructs before React** | Graph UI useless without populated data |
| **Cases before custom workflows** | Longitudinal value for coach/therapist personas |
| **SQLite remains default locally** | PostgreSQL optional; no forced migration |

---

## Supporting documents

| Document | Purpose |
|----------|---------|
| [aws-deployment.md](aws-deployment.md) | AWS architecture, backbone integration, model strategy |
| [../developer/aws-operations.md](../developer/aws-operations.md) | CloudWatch Logs Insights runbook |
| **aws-backbone** (separate repo) | IAM, OIDC, `dev-github-deploy` |
