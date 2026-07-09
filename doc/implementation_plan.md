# Implementation Plan

Active plan to evolve the existing Purposeful Audio Transcription codebase into the **Relationship Reasoning Engine (RRE)** MVP defined in the design package (`doc/01`–`doc/16`).

| | |
|---|---|
| **Status** | **Phase I complete** — post-MVP expansion (phases J–L) |
| **Release** | [`v0.2.0`](https://github.com/SethDKelly/Purposeful-Audio-Transcription/releases/tag/v0.2.0) |
| **Baseline** | Phases 1–4 complete (audio → Whisper → single-purpose Ollama analysis) |
| **Delivered** | Evidence-linked, structured, multi-module workflow MVP |
| **Design reference** | [12_mvp_build_plan.md](12_mvp_build_plan.md) |
| **Deploy** | [DEPLOYMENT.md](DEPLOYMENT.md) · [MODEL_SETUP.md](MODEL_SETUP.md) |

---

## Document Map

| Document | Purpose |
|----------|---------|
| [01_product_vision_and_scope.md](01_product_vision_and_scope.md) | Product goals and MVP success criteria |
| [02_system_architecture.md](02_system_architecture.md) | Service boundaries and data flow |
| [03_domain_model.md](03_domain_model.md) | Core entities |
| [05_data_model_and_schemas.md](05_data_model_and_schemas.md) | JSON and database schemas |
| [12_mvp_build_plan.md](12_mvp_build_plan.md) | Original MVP phase definitions |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Private-use install, run, backup, upgrade |
| [MODEL_SETUP.md](MODEL_SETUP.md) | Ollama and per-module model configuration |
| [15_future_roadmap.md](15_future_roadmap.md) | Post-MVP enhancements |
| **This document** | Implementation record and next steps |
| [archived/](archived/) | Earlier plans and backlogs |

---

## 1. Executive Summary

### Current state (v0.2.0)

The codebase is a working **Relationship Reasoning Engine** for private local use:

- FastAPI backend + Streamlit 4-step UI (Ingest → Prepare → Analyze → Report)
- Whisper transcription from audio; paste / `.txt` upload for transcripts
- Speaker/turn parsing with stable evidence quote IDs (`Q001…`)
- 5 MVP modules via `config/modules/*.yaml` + `PromptCompiler`
- Structured `ModuleRunOutput` JSON with validation, retries, and safety checks
- Workflows `quick_review` and `full_mvp` via `WorkflowEngine`
- `SynthesisEngine` with convergence/divergence from module outputs
- SQLite persistence (`data/rre.db`); 76 tests passing
- Workflow-only Streamlit UI; structured module registry via `config/modules/*.yaml`

### Target state (achieved)

The RRE MVP is a **reasoning platform**, not a prompt runner:

```text
Transcript → Speaker/Turn parsing → Evidence Index (Q001…)
  → Workflow (suite of modules)
  → Structured JSON findings per module
  → Synthesis across modules
  → Interactive evidence-linked report
```

### Key decisions

| Design doc suggestion | This plan |
|-----------------------|-----------|
| Next.js frontend | **Keep Streamlit for MVP**; API-first for future React |
| PostgreSQL | **SQLite for MVP**; SQLAlchemy models portable to PostgreSQL |
| New repository | **Extend** existing `backend/` + `config/` |
| All 13 modules | **5 MVP modules** + meta-synthesis per doc/12 |

Audio transcription remains supported; Whisper output feeds the transcript parser.

---

## 2. Gap Analysis (MVP — resolved)

All MVP gaps below were closed in phases A–G.

| Capability | Design docs | Was missing | Delivered in |
|------------|-------------|-------------|--------------|
| Transcript paste / text upload | Required | Audio only | Phase A |
| Speaker / turn parsing | Required | None | Phase A |
| Evidence quote IDs (`Q001…`) | Required | None | Phase A |
| Module metadata registry | Required | Basic `purposes.yaml` | Phase B |
| Structured JSON output | Required | Markdown only | Phase C |
| Prompt compiler | Required | Static template | Phase B |
| Workflow engine | Required | Single `orchestrator.process()` | Phase D |
| Synthesis engine | Required | Single LLM call | Phase E |
| Finding cards + evidence UI | Required | Raw markdown | Phase F |
| Persistence | Required | Session state | Phase A |
| Tests | Required | None | Phase G (76 tests) |
| Confidence calibration | Required | In prompts only | Phase C |

---

## 3. MVP Scope

### Modules (5)

| # | Module | Purpose ID | Prompt file |
|---|--------|------------|-------------|
| 1 | Relationship Conversation Analysis | `relationship_conversation_analysis` | `01 Relationship Conversation Analysis.md` |
| 2 | NVC Analysis | `nvc_analysis` | `07 NVC Analysis.md` |
| 3 | Systems Analysis | `systems_analysis` | `04 Systems Analysis.md` |
| 4 | Bias & Epistemic Quality | `bias_epistemic_quality` | `12 Bias & Epistemic Quality.md` |
| 5 | Meta-Synthesis | `meta_synthesis` | `13 Meta-Synthesis.md` |

Remaining prompts stay registered but excluded from MVP workflows.

### Workflows (2)

**Quick Review** (`quick_review`)

```text
relationship_conversation_analysis → nvc_analysis → bias_epistemic_quality
```

**Full MVP** (`full_mvp`)

```text
relationship_conversation_analysis → nvc_analysis → systems_analysis
  → bias_epistemic_quality → meta_synthesis
```

Meta-synthesis receives **structured module outputs only**, not the raw transcript.

### Milestones (complete)

| ID | Deliverable | Status |
|----|-------------|--------|
| M1 | Transcript ingestion + evidence indexing | ✓ |
| M2 | Single module → structured findings | ✓ |
| M3 | Multi-module workflow | ✓ |
| M4 | Interactive report UI | ✓ |
| M5 | Synthesis + confidence calibration | ✓ |

---

## 4. Target Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│  UI (Streamlit MVP → React later)                           │
│  Ingest · Workflow select · Report dashboard                │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST
┌──────────────────────────▼──────────────────────────────────┐
│  API — /transcripts · /workflows · /modules · /reports      │
│  (legacy /transcribe · /analyze kept during migration)       │
└──────────────────────────┬──────────────────────────────────┘
                           │
     ┌─────────────────────┼─────────────────────┐
     ▼                     ▼                     ▼
 TranscriptService   WorkflowEngine        ReportService
 EvidenceIndex       ModuleRunner          SynthesisEngine
                     PromptCompiler        OutputParser
                     ModuleRegistry        SafetyValidator
                           │
                     Ollama (LLM adapter)
                           │
                     SQLite (MVP)
```

### Directory structure (incremental additions)

```text
backend/
  domain/                 # Transcript, Finding, ModuleRun, WorkflowRun, …
  schemas/                # module_output_v1, synthesis_output_v1
  repositories/           # SQLite persistence
  services/
    transcript_service.py
    evidence_index.py
    prompt_compiler.py
    module_runner.py
    workflow_engine.py
    synthesis_engine.py
    output_parser.py
    safety_validator.py
    report_service.py
  api/routes/
    transcripts.py
    workflows.py
    reports.py

config/
  modules/                # Per-module YAML metadata
  workflows/              # quick_review.yaml, full_mvp.yaml
  framework/              # shared_instructions.md, output_schema_instructions.md
  prompts/                # Existing — unchanged
```

---

## 5. Implementation Phases (complete)

### Phase A — Domain Foundation · M1 ✓

**Goal:** Core types and transcript ingestion. No LLM changes.

- [x] `backend/domain/` Pydantic models ([03](03_domain_model.md), [05](05_data_model_and_schemas.md))
- [x] `backend/schemas/module_output_v1.py` and synthesis schemas
- [x] `TranscriptParser` — `Speaker:` / `Person A:` labeled text → turns
- [x] `EvidenceIndexService` — `Q001`, `Q002`, … with lookup
- [x] SQLite + SQLAlchemy (`data/rre.db`)
- [x] API: `POST/GET/PATCH /api/transcripts`
- [x] Tests: 2-speaker, multi-speaker, unlabeled fallback
- [x] UI: paste transcript, `.txt` upload, speaker edit, quote IDs in view

**Acceptance:** Labeled transcript → stored speakers, turns, quote IDs. Audio path still works.

**Effort:** 3–5 days

---

### Phase B — Module Registry & Prompt Compiler · M2 prep ✓

**Goal:** Structured module definitions and compiled prompts.

- [x] `config/modules/*.yaml` for 5 MVP modules ([06](06_analysis_modules.md))
- [x] `config/framework/shared_instructions.md` ([07](07_prompt_compiler.md), [09](09_evidence_confidence_and_citations.md))
- [x] `config/framework/output_schema_instructions.md`
- [x] `ModuleRegistry` — load and validate module YAML
- [x] `PromptCompiler` — shared rules + module + evidence index + schema → messages
- [x] API: `GET /api/modules`
- [x] `PurposeRegistry` facade over `ModuleRegistry`

**Acceptance:** Deterministic compiled prompts. `/api/purposes` still works.

**Effort:** 3–4 days

---

### Phase C — Structured Module Runner · M2 ✓

**Goal:** Validated JSON findings, not markdown-only output.

- [x] `OutputParser` — JSON extraction from LLM response
- [x] `SafetyValidator` ([14](14_testing_evaluation_and_safety.md))
- [x] `ModuleRunner` — compile → Ollama → parse → validate → retry
- [x] Enforce evidence IDs, confidence ceiling, alternative explanations
- [x] API: `POST /api/modules/{id}/run`, `GET /api/module-runs/{id}`
- [x] Golden transcript fixtures + schema tests
- [x] All 4 pre-synthesis modules + meta-synthesis path

**Acceptance:** Valid `ModuleRunOutput` with evidence-linked findings.

**Effort:** 5–7 days

---

### Phase D — Workflow Engine · M3 ✓

**Goal:** Quick Review and Full MVP workflows.

- [x] `config/workflows/quick_review.yaml`, `full_mvp.yaml` ([08](08_workflow_engine.md))
- [x] `WorkflowEngine` — sequential module execution, status tracking
- [x] Meta-synthesis receives module outputs only
- [x] API: `GET /api/workflows`, `POST /api/workflows/{id}/run`, `GET /api/workflow-runs/{id}`
- [x] `/api/process` delegates to workflow engine
- [x] Integration tests: transcript → workflow → outputs

**Acceptance:** Both workflows complete end-to-end with persisted results.

**Effort:** 4–6 days

---

### Phase E — Synthesis Engine · M5 ✓

**Goal:** Cross-module integration without re-analyzing transcript.

- [x] `SynthesisEngine` ([10](10_synthesis_engine.md))
- [x] Pre-process: group findings by type and overlapping evidence
- [x] Parse `SynthesisReport` JSON
- [x] API: `GET /api/workflow-runs/{id}/synthesis`
- [x] Safety validation on synthesis output

**Acceptance:** Convergence/divergence sections; no unsupported new claims.

**Effort:** 3–4 days

---

### Phase F — Report UI · M4 ✓

**Goal:** Evidence-linked interactive report ([11](11_ui_ux_design.md)).

- [x] Streamlit pages: Ingest → Prepare → Analyze → Report
- [x] `ExecutiveSummaryPanel`, `FindingCard`, `EvidenceQuoteViewer`
- [x] `ModuleTabs`, `SynthesisPanel`, `ConfidenceBadge`
- [x] Progressive disclosure + safety disclaimer
- [x] Export `.md` and `.json` workflow report
- [x] Workflow progress during multi-module runs
- [x] Legacy single-purpose mode toggle

**Acceptance:** Full user journey without API knowledge; quote drill-down works.

**Effort:** 5–7 days

---

### Phase G — Testing & Hardening · M5 ✓

**Goal:** MVP ready for private use.

- [x] `tests/fixtures/transcripts/` — 7 golden + red-team scenarios
- [x] Unit + integration test suite (76 tests)
- [x] Long transcript handling (evidence summarization)
- [x] Document model setup; per-module model overrides ([MODEL_SETUP.md](MODEL_SETUP.md))
- [x] Deprecate `/api/analyze` in favor of workflows
- [x] Deployment guide ([DEPLOYMENT.md](DEPLOYMENT.md))

**Acceptance:** `pytest` passes; safety validator catches forbidden patterns.

**Effort:** 4–5 days

---

## 6. API Plan

### New endpoints

| Method | Endpoint | Phase |
|--------|----------|-------|
| `POST` | `/api/transcripts` | A |
| `GET` | `/api/transcripts/{id}` | A |
| `PATCH` | `/api/transcripts/{id}/speakers` | A |
| `GET` | `/api/modules` | B |
| `POST` | `/api/modules/{id}/run` | C |
| `GET` | `/api/module-runs/{id}` | C |
| `GET` | `/api/workflows` | D |
| `POST` | `/api/workflows/{id}/run` | D |
| `GET` | `/api/workflow-runs/{id}` | D |
| `GET` | `/api/workflow-runs/{id}/synthesis` | E |
| `GET` | `/api/reports/{workflow_run_id}` | F |

### Legacy (maintained for compatibility)

| Endpoint | Status |
|----------|--------|
| `/api/transcribe` | Active — feeds transcript pipeline |
| `/api/process` | Active — workflow-only audio processing |
| `/api/purposes` | Deprecated alias over `/api/modules` |
| `/api/modules/{id}/stream` | Single-module streaming |

---

## 7. Configuration Examples

### Module (`config/modules/nvc_analysis.yaml`)

```yaml
id: nvc_analysis
name: "NVC Analysis"
version: "1.0.0"
enabled: true
primary_lens: "Nonviolent Communication"
analytical_level: relational
unit_of_analysis: interaction
primary_question: "What observations, feelings, needs, and requests appear?"
confidence_ceiling: moderate
inference_depth: medium
dependencies:
  - transcript_preprocessing
output_schema: module_output_v1
prompt_file: "07 NVC Analysis.md"
ollama_model: null
```

### Workflow (`config/workflows/quick_review.yaml`)

```yaml
id: quick_review
name: "Quick Review"
description: "Fast, practical communication insight."
estimated_runtime: "1-3 min"
modules:
  - relationship_conversation_analysis
  - nvc_analysis
  - bias_epistemic_quality
meta_synthesis: false
```

---

## 8. Migration Strategy (MVP complete)

| Legacy | Replacement | Status |
|--------|-------------|--------|
| `config/purposes.yaml` | `config/modules/*.yaml` | Archived; `/api/purposes` is deprecated alias |
| `PurposeRegistry` | `ModuleRegistry` | Removed in Phase H |
| `AnalysisService` | `ModuleRunner` | Removed in Phase H |
| `orchestrator.process()` | `WorkflowEngine` | `/api/process` delegates |
| Streamlit single-purpose flow | Workflow report UI | Both available; workflows preferred |

```text
Audio → Whisper → TranscriptParser → EvidenceIndex → WorkflowEngine
```

---

## 9. Out of Scope (MVP)

- Full 13-module workflows
- Graph database / knowledge graph UI
- User accounts, billing, permissions
- PDF export, React frontend
- Distributed job queue
- PostgreSQL (until deployment requires it)
- Ontology-driven prompt generation

---

## 10. Risks

| Risk | Mitigation |
|------|------------|
| Invalid JSON from LLM | Retry + repair prompt; store raw output |
| Weak local model | Document recommended models; per-module override |
| Long transcripts | Evidence index summarization in compiler |
| Scope creep | Strict 5-module MVP cap |
| Dual architecture confusion | Facades + deprecation in Phase G |

---

## 11. Success Criteria (met)

- [x] Paste or upload transcript (audio optional)
- [x] Speakers, turns, and quote IDs generated
- [x] Quick Review and Full MVP workflows run end-to-end
- [x] Structured findings with evidence quote IDs
- [x] Confidence labels in plain language in UI
- [x] Report dashboard with finding cards and evidence viewer
- [x] Meta-synthesis uses module outputs only
- [x] Safety disclaimer present
- [x] Golden transcript tests pass
- [x] Export `.md` and `.json` reports

---

## 12. Build Order (complete)

| # | Task | Status |
|---|------|--------|
| 1 | Domain types + schemas | ✓ |
| 2 | Transcript parser + tests | ✓ |
| 3 | Evidence index + tests | ✓ |
| 4 | SQLite repositories | ✓ |
| 5 | Module registry | ✓ |
| 6 | Prompt compiler | ✓ |
| 7 | Output parser + safety validator | ✓ |
| 8 | Module runner | ✓ |
| 9 | Workflow engine | ✓ |
| 10 | Synthesis engine | ✓ |
| 11 | Report UI | ✓ |
| 12 | Golden transcript tests | ✓ |
| 13 | Legacy migration + docs | ✓ |

---

## 13. Timeline (actual)

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 1–4 | Audio transcription + single-purpose analysis | ✓ |
| A | Domain + ingestion | ✓ |
| B | Registry + compiler | ✓ |
| C | Module runner | ✓ |
| D | Workflow engine | ✓ |
| E | Synthesis | ✓ |
| F | Report UI | ✓ |
| G | Testing + hardening | ✓ |
| — | Release `v0.2.0` | ✓ |

---

## 14. Post-MVP Next Steps

MVP is complete and released. Prioritized work below extends the platform per [15_future_roadmap.md](15_future_roadmap.md). Tackle one theme per PR; keep tests with every change.

### Immediate — stabilize private use

| Priority | Task | Notes |
|----------|------|-------|
| P0 | Run real transcripts through `quick_review` and `full_mvp` | Validate with your Ollama model; tune `DEFAULT_OLLAMA_MODEL` |
| P0 | Set per-module `ollama_model` where needed (especially `meta_synthesis`) | See [MODEL_SETUP.md](MODEL_SETUP.md) |
| P1 | Expand golden fixtures from real usage | Add anonymized scenarios to `tests/fixtures/transcripts/` |
| P1 | Monitor safety validator flags on live output | Calibrate prompts if false positives appear |

### Phase H — Legacy cleanup ✓

**Goal:** Single module/workflow architecture; less confusion for contributors.

- [x] Remove dual-load of `config/purposes.yaml` (modules YAML only)
- [x] Retire `PurposeRegistry` / `AnalysisService`
- [x] Remove deprecated `POST /api/analyze` (replaced by `POST /api/modules/{id}/stream`)
- [x] Update README and `config/prompts/README.md` to reference modules/workflows only
- [x] Archive `config/purposes.yaml` to `config/archived/`

**Acceptance:** No production code path depends on `purposes.yaml`; docs reflect workflows as primary.

### Phase I — Module & workflow expansion ✓

**Goal:** Grow from 5 modules / 2 workflows toward the full prompt library.

- [x] Add module YAML for remaining prompts (8 modules; 13 total)
- [x] Define new workflows: Conflict Coaching, Mediation Brief, Clinical Exploration
- [x] Workflow-level metadata: estimated runtime, recommended model, output tone
- [x] UI workflow picker with descriptions and output tone

**Acceptance:** At least 3 new modules and 2 new workflows run end-to-end with existing runner/engine.

### Phase J — Export & reporting

**Goal:** Professional-ready outputs beyond `.md` / `.json`.

- [ ] PDF export (workflow report)
- [ ] Therapist/coach summary template (shorter, action-oriented)
- [ ] Mediation brief template
- [ ] Optional redaction pass before export

**Acceptance:** Full MVP report exports to PDF; at least one role-specific summary format.

### Phase K — Platform hardening

**Goal:** Prepare for heavier use without full multi-tenant deployment.

- [ ] PostgreSQL option (env-driven; keep SQLite default)
- [ ] Database migrations (Alembic)
- [ ] Async/workflow job queue for long runs (optional background execution)
- [ ] API authentication hook (local API key or reverse-proxy pattern)
- [ ] Structured logging + run telemetry

**Acceptance:** Can switch `DATABASE_URL` to PostgreSQL; long workflows survive API restart.

### Phase L — Interactive exploration (future)

**Goal:** Move from static report to guided reasoning ([15](15_future_roadmap.md)).

- [ ] “Why this finding?” drill-down (module + evidence chain)
- [ ] Cross-module agreement/disagreement explorer
- [ ] Comparative analysis across multiple transcripts / sessions
- [ ] Knowledge graph visualization (constructs, cycles, needs)
- [ ] React frontend (API already supports this path)

**Acceptance:** User can ask follow-up questions scoped to stored findings without re-running full workflow.

### Recommended first PR after Phase H

### Recommended first PR after Phase I

```text
Phase J: Add PDF export for workflow reports and a therapist/coach summary template.
```

### Out of scope (unchanged)

See [§9 Out of Scope](#9-out-of-scope-mvp). Multi-user SaaS, billing, and ontology-driven prompt generation remain post-roadmap unless requirements change.
