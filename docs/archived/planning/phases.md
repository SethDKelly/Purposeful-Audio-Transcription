# Phases — Relationship Reasoning Engine

Sequential record of **completed** project phases. Numbering starts at **1** and increments by **1**. When a new series of phases is planned and later finished, append starting at the next free number (**50** after this document).

Executive summary: [executive_roadmap.md](executive_roadmap.md). Active backlogs: [../../planning/deferred_backlog.md](../../planning/deferred_backlog.md) · [../../planning/general_backlog.md](../../planning/general_backlog.md).

---

## Phase 1 — Project foundation

**Status:** Complete · **Release:** precursor to v0.2.0

Repository, Python packaging, FastAPI health shell, environment/settings, schema validation footing, and early LLM provider abstraction.

---

## Phase 2 — Transcript ingestion

**Status:** Complete · **Release:** v0.2.0

Paste/upload transcript UI, speaker-turn parser, manual speaker correction, and evidence quote IDs (`Q001…`) tied to turns.

---

## Phase 3 — Module registry

**Status:** Complete · **Release:** v0.2.0

Module metadata schema, versioning, first module definitions, and structured output schema contracts.

---

## Phase 4 — Prompt compiler MVP

**Status:** Complete · **Release:** v0.2.0

Shared + module prompt templates, evidence injection, JSON output request, and output validation loop.

---

## Phase 5 — Core modules and module runner

**Status:** Complete · **Release:** v0.2.0

Representative modules (relationship, NVC, systems, bias/reliability), runner with parse/validate/retry, and persistence of module runs.

---

## Phase 6 — Workflow engine MVP

**Status:** Complete · **Release:** v0.2.0

Sequential multi-module orchestration and workflow run records (Quick Review / early Full MVP path).

---

## Phase 7 — Meta-synthesis MVP

**Status:** Complete · **Release:** v0.2.0

Cross-module synthesis step, safety-oriented validation of synthesis language, and integrated report assembly.

---

## Phase 8 — Streamlit application shell

**Status:** Complete · **Release:** **v0.2.0**

Ingest → prepare → analyze → report UI over the MVP API surface.

---

## Phase 9 — Full module library

**Status:** Complete · **Release:** v0.3.0

Expanded analysis library to **13** structured modules (beyond the MVP subset).

---

## Phase 10 — Expanded workflows

**Status:** Complete · **Release:** v0.3.0

Conflict Coaching, Mediation Brief, Clinical Exploration, and related YAML workflows alongside Quick Review / Full MVP.

---

## Phase 11 — Exports and report packaging (early)

**Status:** Complete · **Release:** v0.3.0

Markdown, JSON, PDF, coach summary, and mediation brief exports with optional redaction hooks.

---

## Phase 12 — Persistence, jobs, and API key auth

**Status:** Complete · **Release:** v0.3.0

PostgreSQL + Alembic, background workflow jobs with resume, and optional `X-API-Key` middleware.

---

## Phase 13 — Exploration APIs and Explore UI

**Status:** Complete · **Release:** **v0.3.0**

Drill-down, cross-module, compare, knowledge-graph APIs, follow-up Q&A, and Streamlit Explore tab.

---

## Phase 14 — Documentation reorganization (M0)

**Status:** Complete

`docs/` layout (`user/`, `developer/`, `design/`, `planning/`), user/developer guides, and documentation index.

---

## Phase 15 — Audio diarization and sliced transcription

**Status:** Complete · **Release:** v0.4.x (later superseded on AWS by Transcribe)

pyannote diarization, timeline smoothing, per-speaker slices, labeled turns, Transcribe/Whisper-era API progress events, and Streamlit speaker UX. Product ASR later became Amazon Transcribe-only (Phase 23–24).

---

## Phase 16 — Local LLM reliability (Ollama)

**Status:** Complete · **Release:** v0.4.x (later removed in AWS-only prune)

JSON mode, `think=false`, nested JSON recovery, and repair loops for local Ollama development. Removed from product runtime in Phase 24.

---

## Phase 17 — AWS architecture and backbone

**Status:** Complete

AWS deployment architecture document; GitHub OIDC; `rre-dev-*` IAM isolation; aws-backbone integration (MinneAnalytics unchanged).

---

## Phase 18 — Cloud observability

**Status:** Complete

Structured JSON logs, request correlation IDs, CloudWatch log groups, Insights runbook, and deploy smoke beyond health.

---

## Phase 19 — Containerization

**Status:** Complete

API/UI Dockerfiles, `.dockerignore`, health checks, ECR repositories; later slim `Dockerfile.cloud` for Bedrock + Transcribe.

---

## Phase 20 — Terraform `infra/dev`

**Status:** Complete

VPC/ALB/ECS/RDS/S3/Secrets/CloudWatch; Stage A then Stage B (no public task IPs, VPC endpoints).

---

## Phase 21 — CI/CD deploy and pause

**Status:** Complete · **Release:** **v0.5.1** ops path

Deploy-to-AWS workflow (OIDC → ECR → Terraform → ECS); pause workflow (scale to zero + stop RDS); standing “pause when idle” practice.

---

## Phase 22 — LLM provider layer (Bedrock)

**Status:** Complete

`LLMProvider` protocol, Bedrock Converse adapter, settings/health reporting, Quick Review burn-in on Claude Sonnet.

---

## Phase 23 — Amazon Transcribe and slim cloud image

**Status:** Complete · **Release:** **v0.5.1**

Transcription provider adapters, Transcribe on ECS, `Dockerfile.cloud`, Fargate sizing, live Transcribe + Quick Review under Stage B.

---

## Phase 24 — Trust controls, full workflows, AWS-only prune

**Status:** Complete · **Release:** **v0.6.0**

Cascade delete, log redaction, retention/audit/privacy copy; `full_multidisciplinary` / `research_oriented`; remove Ollama/Whisper/pyannote product path; Bedrock reliability hardening (structured JSON, compact handoff, multi-worker API).

---

## Phase 25 — Secure external UAT readiness

**Status:** Complete · **Release:** v0.7.0

Optional ACM HTTPS, Streamlit API key wiring, generic errors + `request_id`, privacy/retention captions, export redaction default-on, clear deletion controls.

---

## Phase 26 — Transcript preparation workspace

**Status:** Complete · **Release:** v0.7.0

Edit/exclude turns, evidence rebuild, `analysis_ready` gate, Streamlit prepare UX. (Split/merge and multi-file stitch deferred — see deferred backlog.)

---

## Phase 27 — Ontology vocabulary v1

**Status:** Complete · **Release:** v0.7.0

`config/ontology/`, `OntologyRegistry`, canonical construct/relationship IDs and aliases, module validation against ontology.

---

## Phase 28 — Module construct expectations

**Status:** Complete · **Release:** v0.7.0

`expected_constructs` on modules; soft coverage warnings on runs (not hard-fail by default).

---

## Phase 29 — Golden fixtures and evaluation foundation

**Status:** Complete · **Release:** v0.7.0

GT001/GT002 fixtures, signal assertions, golden pytest suite, manual review rubric.

---

## Phase 30 — Cost, latency, and module telemetry

**Status:** Complete · **Release:** **v0.7.0**

Per-module latency/tokens/cost fields; workflow `telemetry_summary`; deploy policy tightened to tag/manual only.

---

## Phase 31 — Normalized findings persistence

**Status:** Complete · **Release:** v0.8.0

`findings` (+ evidence quotes, alternatives) written on module completion; exploration prefers DB; `parsed_output` retained for audit. Alembic `005`.

---

## Phase 32 — Normalized constructs persistence

**Status:** Complete · **Release:** v0.8.0

`constructs` + evidence/sources; ontology resolve/warn. Alembic `006`.

---

## Phase 33 — Construct relationship persistence

**Status:** Complete · **Release:** v0.8.0

`construct_relationships` with ontology and dangling-link warnings. Alembic `007`.

---

## Phase 34 — Graph merge / deduplication

**Status:** Complete · **Release:** v0.8.0

Cross-module similarity merge; sources/evidence preserved on canonical nodes.

---

## Phase 35 — Deterministic convergence scoring

**Status:** Complete · **Release:** v0.8.0

Strong / moderate / weak / contested scores with rationale JSON.

---

## Phase 36 — Table-first graph exploration UI

**Status:** Complete · **Release:** v0.8.0

`GET /api/workflow-runs/{id}/structured-graph` and Streamlit structured inventory tables.

---

## Phase 37 — Synthesis over structured objects

**Status:** Complete · **Release:** **v0.8.0**

Meta-synthesis handoff prefers structured inventory; merge/score before synthesis.

---

## Phase 38 — Case data model

**Status:** Complete · **Release:** v0.9.0

`cases` table; transcript `case_id` / `session_label` / `session_date`; CRUD + assign API. Alembic `008`.

---

## Phase 39 — Case dashboard

**Status:** Complete · **Release:** v0.9.0

Streamlit Cases expander: create, assign, list sessions.

---

## Phase 40 — Longitudinal comparison

**Status:** Complete · **Release:** v0.9.0

`POST /api/exploration/compare-transcripts` (earliest vs latest themes).

---

## Phase 41 — Longitudinal synthesis module

**Status:** Complete · **Release:** v0.9.0

`longitudinal_synthesis` module + `POST /api/cases/{id}/longitudinal-synthesis` (14 modules total).

---

## Phase 42 — Report package export

**Status:** Complete · **Release:** v0.9.0

ZIP: manifest + report + evidence appendix + findings index.

---

## Phase 43 — Finding feedback / analyst review loop

**Status:** Complete · **Release:** **v0.9.0**

`finding_feedback` ratings (helpful / unhelpful / unsure) + API + finding-card UI. Alembic `009`.

---

## Phase 44 — Dedicated workflow worker

**Status:** Complete · **Release:** v1.0.0

ECS worker (`RRE_PROCESS=worker`); API queues `CREATED` jobs; cancel / timeout / retries. Alembic `010`.

---

## Phase 45 — Workflow DAG engine

**Status:** Complete · **Release:** v1.0.0

YAML `steps` with `depends_on` + `parallel`; topological waves; `full_mvp` migrated.

---

## Phase 46 — Custom workflow builder

**Status:** Complete · **Release:** v1.0.0

`POST /api/workflows/custom/run` and Streamlit custom suite builder.

---

## Phase 47 — Long transcript strategy

**Status:** Complete · **Release:** v1.0.0

Balanced quote sampling (not silent head/tail-only); `GET …/length-assessment`; UI warnings.

---

## Phase 48 — Safety-aware report mode

**Status:** Complete · **Release:** v1.0.0

Risk scanner, `safety_mode` on runs, UI banner, synthesis framing, exploratory-module skip. Alembic `011`.

---

## Phase 49 — Production-grade API and documentation

**Status:** Complete · **Release:** **v1.0.0**

API reference expansion, architecture/user guide refresh, version alignment (`1.0.0`), release notes.

---

## Append rule

When a new planned series completes, add **Phase 50**, **Phase 51**, … here with status, release tag (if any), and a short delivery summary. Update [executive_roadmap.md](executive_roadmap.md) completion bands accordingly.
