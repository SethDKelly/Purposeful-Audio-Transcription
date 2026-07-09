# Implementation Plan

Active plan to evolve the existing Purposeful Audio Transcription codebase into the **Relationship Reasoning Engine (RRE)** MVP defined in the design package (`doc/01`–`doc/16`).

| | |
|---|---|
| **Status** | Active |
| **Baseline** | Phases 1–4 complete (audio → Whisper → single-purpose Ollama analysis) |
| **Target** | Evidence-linked, structured, multi-module workflow MVP |
| **Design reference** | [12_mvp_build_plan.md](12_mvp_build_plan.md) |
| **Estimated timeline** | ~6 weeks |

---

## Document Map

| Document | Purpose |
|----------|---------|
| [01_product_vision_and_scope.md](01_product_vision_and_scope.md) | Product goals and MVP success criteria |
| [02_system_architecture.md](02_system_architecture.md) | Service boundaries and data flow |
| [03_domain_model.md](03_domain_model.md) | Core entities |
| [05_data_model_and_schemas.md](05_data_model_and_schemas.md) | JSON and database schemas |
| [12_mvp_build_plan.md](12_mvp_build_plan.md) | Original MVP phase definitions |
| **This document** | Actionable codebase update plan |
| [archived/](archived/) | Earlier plans and backlogs |

---

## 1. Executive Summary

### Current state

The codebase is a working **local analysis pipeline**:

- FastAPI backend + Streamlit UI
- Whisper transcription from audio
- 13 analysis purposes via `config/purposes.yaml` + markdown prompts
- Single-purpose analysis (sync + stream) and one-shot `transcribe + analyze`
- Raw markdown output — no structured findings, evidence IDs, or workflows

### Target state

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

## 2. Gap Analysis

| Capability | Design docs | Current code | MVP target |
|------------|-------------|--------------|------------|
| Transcript paste / text upload | Required | Audio only | Paste + `.txt` + audio |
| Speaker / turn parsing | Required | None | Parser + manual correction |
| Evidence quote IDs (`Q001…`) | Required | None | Evidence index service |
| Module metadata registry | Required | Basic `purposes.yaml` | Full `ModuleDefinition` schema |
| Structured JSON output | Required | Markdown only | Pydantic `ModuleRunOutput` |
| Prompt compiler | Required | Static template | Shared rules + evidence + schema |
| Workflow engine | Required | Single `orchestrator.process()` | Quick Review + Full MVP |
| Synthesis engine | Required | Single LLM call | Structured cross-module synthesis |
| Finding cards + evidence UI | Required | Raw markdown | Dashboard with quote viewer |
| Persistence | Required | Session state | SQLite store |
| Tests | Required | None | Parser, schemas, golden transcripts |
| Confidence calibration | Required | In prompts only | Validated `Confidence` enum |

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

### Milestones

| ID | Deliverable |
|----|-------------|
| M1 | Transcript ingestion + evidence indexing |
| M2 | Single module → structured findings |
| M3 | Multi-module workflow |
| M4 | Interactive report UI |
| M5 | Synthesis + confidence calibration |

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

## 5. Implementation Phases

### Phase A — Domain Foundation · M1

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

### Phase B — Module Registry & Prompt Compiler · M2 prep

**Goal:** Structured module definitions and compiled prompts.

- [ ] `config/modules/*.yaml` for 5 MVP modules ([06](06_analysis_modules.md))
- [ ] `config/framework/shared_instructions.md` ([07](07_prompt_compiler.md), [09](09_evidence_confidence_and_citations.md))
- [ ] `config/framework/output_schema_instructions.md`
- [ ] `ModuleRegistry` — load and validate module YAML
- [ ] `PromptCompiler` — shared rules + module + evidence index + schema → messages
- [ ] API: `GET /api/modules`
- [ ] `PurposeRegistry` facade over `ModuleRegistry`

**Acceptance:** Deterministic compiled prompts. `/api/purposes` still works.

**Effort:** 3–4 days

---

### Phase C — Structured Module Runner · M2

**Goal:** Validated JSON findings, not markdown-only output.

- [ ] `OutputParser` — JSON extraction from LLM response
- [ ] `SafetyValidator` ([14](14_testing_evaluation_and_safety.md))
- [ ] `ModuleRunner` — compile → Ollama → parse → validate → retry
- [ ] Enforce evidence IDs, confidence ceiling, alternative explanations
- [ ] API: `POST /api/modules/{id}/run`, `GET /api/module-runs/{id}`
- [ ] Golden transcript fixtures + schema tests
- [ ] Start with Relationship Conversation Analysis; expand to 4 pre-synthesis modules

**Acceptance:** Valid `ModuleRunOutput` with evidence-linked findings.

**Effort:** 5–7 days

---

### Phase D — Workflow Engine · M3

**Goal:** Quick Review and Full MVP workflows.

- [ ] `config/workflows/quick_review.yaml`, `full_mvp.yaml` ([08](08_workflow_engine.md))
- [ ] `WorkflowEngine` — sequential module execution, status tracking
- [ ] Meta-synthesis receives module outputs only
- [ ] API: `GET /api/workflows`, `POST /api/workflows/{id}/run`, `GET /api/workflow-runs/{id}`
- [ ] `/api/process` delegates to workflow engine
- [ ] Integration tests: transcript → workflow → outputs

**Acceptance:** Both workflows complete end-to-end with persisted results.

**Effort:** 4–6 days

---

### Phase E — Synthesis Engine · M5

**Goal:** Cross-module integration without re-analyzing transcript.

- [ ] `SynthesisEngine` ([10](10_synthesis_engine.md))
- [ ] Pre-process: group findings by type and overlapping evidence
- [ ] Parse `SynthesisReport` JSON
- [ ] API: `GET /api/workflow-runs/{id}/synthesis`
- [ ] Safety validation on synthesis output

**Acceptance:** Convergence/divergence sections; no unsupported new claims.

**Effort:** 3–4 days

---

### Phase F — Report UI · M4

**Goal:** Evidence-linked interactive report ([11](11_ui_ux_design.md)).

- [ ] Streamlit pages: Ingest → Prepare → Analyze → Report
- [ ] `ExecutiveSummaryPanel`, `FindingCard`, `EvidenceQuoteViewer`
- [ ] `ModuleTabs`, `SynthesisPanel`, `ConfidenceBadge`
- [ ] Progressive disclosure + safety disclaimer
- [ ] Export `.md` and `.json` workflow report
- [ ] Workflow progress during multi-module runs
- [ ] Legacy single-purpose mode toggle

**Acceptance:** Full user journey without API knowledge; quote drill-down works.

**Effort:** 5–7 days

---

### Phase G — Testing & Hardening · M5

**Goal:** MVP ready for private use.

- [ ] `tests/fixtures/transcripts/` — 5–8 golden + red-team scenarios
- [ ] Unit + integration test suite
- [ ] Long transcript handling (evidence summarization)
- [ ] Document model setup; per-module model overrides
- [ ] Deprecate `/api/analyze` in favor of workflows

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

### Legacy (maintained during migration)

| Endpoint | Plan |
|----------|------|
| `/api/transcribe` | Keep — feeds transcript pipeline |
| `/api/analyze` | Wrap `ModuleRunner`; deprecate in G |
| `/api/analyze/stream` | Keep for single-module streaming |
| `/api/process` | Delegate to `WorkflowEngine` |
| `/api/purposes` | Facade over `ModuleRegistry` |

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

## 8. Migration Strategy

| Legacy | Replacement | Approach |
|--------|-------------|----------|
| `config/purposes.yaml` | `config/modules/*.yaml` | Dual-load in Phase B; deprecate in G |
| `PurposeRegistry` | `ModuleRegistry` | Facade until Phase G |
| `AnalysisService` | `ModuleRunner` | `/api/analyze` delegates |
| `orchestrator.process()` | `WorkflowEngine` | `/api/process` delegates |
| Streamlit Step 3 | Workflow selector | Legacy tab until Phase F |

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

## 11. Success Criteria

- [ ] Paste or upload transcript (audio optional)
- [ ] Speakers, turns, and quote IDs generated
- [ ] Quick Review and Full MVP workflows run end-to-end
- [ ] Structured findings with evidence quote IDs
- [ ] Confidence labels in plain language in UI
- [ ] Report dashboard with finding cards and evidence viewer
- [ ] Meta-synthesis uses module outputs only
- [ ] Safety disclaimer present
- [ ] Golden transcript tests pass
- [ ] Export `.md` and `.json` reports

---

## 12. Build Order

| # | Task | Reference |
|---|------|-----------|
| 1 | Domain types + schemas | doc/03, doc/05 |
| 2 | Transcript parser + tests | Phase A |
| 3 | Evidence index + tests | doc/09 |
| 4 | SQLite repositories | doc/05 |
| 5 | Module registry | doc/06 |
| 6 | Prompt compiler | doc/07 |
| 7 | Output parser + safety validator | doc/14 |
| 8 | Module runner (one module) | Phase C |
| 9 | Workflow engine | doc/08 |
| 10 | Synthesis engine | doc/10 |
| 11 | Report UI | doc/11 |
| 12 | Golden transcript tests | doc/14 |
| 13 | Legacy migration + docs | Phase G |

One milestone per PR where possible. Tests with every service.

---

## 13. Timeline

| Phase | Days | Week |
|-------|------|------|
| A — Domain + ingestion | 3–5 | 1 |
| B — Registry + compiler | 3–4 | 1–2 |
| C — Module runner | 5–7 | 2–3 |
| D — Workflow engine | 4–6 | 3–4 |
| E — Synthesis | 3–4 | 4 |
| F — Report UI | 5–7 | 4–5 |
| G — Testing | 4–5 | 5–6 |

---

## 14. Next Action

**Start Phase A:** Implement `backend/domain/` models and `TranscriptParser` with tests. No LLM changes in the first PR.

```text
Implement domain models and transcript parser per doc/implementation_plan.md Phase A.
Include tests for 2-speaker and unlabeled transcripts.
Do not modify LLM integration yet.
```
