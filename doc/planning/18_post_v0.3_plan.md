# 18 — Post-v0.3.0 Implementation Plan

Forward plan after merging **v0.3.0** (phases H–L) to `main`. Supersedes the “recommended next PR” notes at the end of [implementation_plan.md](implementation_plan.md).

| | |
|---|---|
| **Baseline** | `v0.3.0` on `main` — 13 modules, 5 workflows, 96 tests |
| **Design anchors** | [../design/01_product_vision_and_scope.md](../design/01_product_vision_and_scope.md) · [../design/04_knowledge_ontology.md](../design/04_knowledge_ontology.md) · [../design/11_ui_ux_design.md](../design/11_ui_ux_design.md) · [15_future_roadmap.md](15_future_roadmap.md) · [../design/16_additional_thoughts.md](../design/16_additional_thoughts.md) |
| **Documentation** | [../README.md](../README.md) · [../user/](../user/) · [../developer/](../developer/) |
| **Principle** | Evidence traceability and progressive disclosure first; prompts remain replaceable |

---

## 1. Where we are

### Delivered (v0.3.0)

| Area | Status |
|------|--------|
| Transcript ingestion + evidence index | ✓ |
| 13 modules + prompt compiler | ✓ |
| 5 workflows | ✓ |
| Synthesis + safety validation | ✓ |
| Exports (md, json, pdf, coach, mediation) | ✓ |
| PostgreSQL, Alembic, background jobs, API key | ✓ |
| Exploration APIs + Streamlit Explore tab | ✓ |

### Gaps vs product vision

| Vision item ([01](../design/01_product_vision_and_scope.md)) | Gap |
|---------------------------------------------------|-----|
| **5. Full Multidisciplinary Suite** | No workflow runs all transcript modules + meta-synthesis |
| **Research-oriented analysis** | No dedicated workflow |
| **Interactive exploration** | Partial — no counterfactual presets (“what would change this?”) |
| **Knowledge graph** | APIs exist; module outputs rarely populate `constructs` / `relationships` |
| **Longitudinal / progress tracking** | Compare runs on one transcript only; no cross-transcript case view |
| **Module customization** | Workflows are fixed YAML only |
| **Professional mode** | Exports exist; no case files, session series, or finding feedback |
| **Segment speakers from audio** ([01](../design/01_product_vision_and_scope.md), [16](../design/16_additional_thoughts.md)) | Whisper outputs unlabeled text; parser assigns **Speaker 1** for entire audio |
| **React frontend** | Deferred; Streamlit remains primary UI |

### Documentation (resolved in M0)

Documentation is organized under [doc/README.md](../README.md) with **user**, **developer**, **design**, and **planning** sections. v0.3.0 stats are reflected in [user/deployment.md](../user/deployment.md) and [planning/implementation_plan.md](implementation_plan.md).

---

## 2. Recommended priorities

```text
M0  Doc & release alignment     ✓ complete
M   Speaker diarization        (audio ingest — next)
N   Full suite workflows       (product completeness)
O   Ontology & constructs      (unlocks knowledge graph value)
P   Cases & longitudinal view  (professional / repeat use)
Q   Custom workflows           (power users)
R   UX hardening               (Streamlit polish)
S   React frontend             (parallel track, larger)
—   Evaluation loop            (ongoing, every phase)
```

**Recommended next implementation PR:** **Phase M** (speaker diarization + Whisper segment alignment).

---

## 3. Phase M0 — Documentation & release alignment ✓

**Goal:** Single source of truth for v0.3.0 after merge.

- [x] Reorganize docs: `user/`, `developer/`, `design/`, `planning/`
- [x] [doc/README.md](../README.md) documentation index
- [x] User guides: [getting-started](../user/getting-started.md), [user-guide](../user/user-guide.md), [deployment](../user/deployment.md), [model-setup](../user/model-setup.md)
- [x] Developer guides: [architecture](../developer/architecture.md), [development](../developer/development.md), [api-reference](../developer/api-reference.md), [contributing](../developer/contributing.md)
- [x] Update [implementation_plan.md](implementation_plan.md) §1 to v0.3.0
- [x] Stub redirects at legacy paths (`doc/DEPLOYMENT.md`, etc.)
- [x] Update root [README.md](../../README.md)

**Acceptance:** New contributor can install from `main` using only current docs.

---

## 4. Phase M — Speaker diarization & labeled audio ingest

**Goal:** Close the audio-ingest gap: detect **who spoke when**, align with Whisper segments, and produce **multi-speaker labeled turns** for the evidence index — per [01_product_vision](../design/01_product_vision_and_scope.md) (“segment speakers”) and [16_additional_thoughts](../design/16_additional_thoughts.md).

### Problem (current behavior)

```text
Audio → Whisper (faster-whisper) → single text blob → TranscriptParser → Speaker 1
```

Whisper (any model size, including `large-v3`) transcribes words only; it does **not** identify speakers. Upgrading `WHISPER_MODEL` improves word accuracy but does not fix diarization.

### Target pipeline

```text
Audio
  → (optional) VAD / channel prep
  → Diarization (pyannote) → speaker timeline [{speaker, start, end}, …]
  → Whisper → segments [{text, start, end}, …]
  → Alignment service → labeled turns (Person A / Person B or Speaker 1 / Speaker 2)
  → TranscriptParser-compatible text → existing ingest + evidence index
```

### M1 — Diarization service

- Add `backend/services/diarization_service.py` wrapping [pyannote.audio](https://github.com/pyannote/pyannote-audio) (or compatible pipeline)
- Default model: `pyannote/speaker-diarization-3.1` (configurable via `DIARIZATION_MODEL`)
- Settings in `config/settings.py` + `.env.example`:
  - `DIARIZATION_ENABLED` (default `true` when deps present)
  - `HF_TOKEN` — required for gated pyannote models on Hugging Face
  - `DIARIZATION_MIN_SPEAKERS` / `DIARIZATION_MAX_SPEAKERS` (optional bounds)
- Lazy model load (same pattern as `WhisperService`)
- Health check: `GET /api/health` reports `diarization_ready`
- Graceful fallback: if pyannote unavailable or `HF_TOKEN` missing, skip diarization and keep current single-speaker behavior (log warning)

### M2 — Segment alignment

- Add `backend/services/transcript_alignment_service.py`:
  - Input: diarization timeline + Whisper `TranscriptSegment` list
  - Assign each Whisper segment to the diarization label with maximum temporal overlap
  - Merge consecutive segments with the same speaker into turns
  - Emit labeled text:

    ```text
    Person A: First speaker's words…
    Person B: Second speaker's words…
    ```

- Map anonymous diarization labels (`SPEAKER_00`, `SPEAKER_01`) → `Person A`, `Person B`, … (configurable prefix)
- Preserve segment timestamps on turns/quotes where useful for future UI (optional metadata on ingest)

### M3 — API & orchestration

- Extend `whisper_service` / `orchestrator` / `transcript_service.ingest_from_whisper`:
  - Run diarization before or in parallel with Whisper (parallel when GPU allows; sequential on CPU to avoid OOM)
  - `POST /api/transcribe` returns `speaker_count` and per-turn labels
- Stream progress events: `diarization_started`, `diarization_complete`, then Whisper transcription status as needed
- `scripts/check_prerequisites.py`: verify `HF_TOKEN`, pyannote import, CUDA optional

### M4 — UI & docs

- Streamlit Ingest: show detected speaker count after transcription; caption when diarization skipped
- Step 2 Prepare: pre-populated `Person A` / `Person B` labels (existing speaker rename UI)
- [user/model-setup.md](../user/model-setup.md): pyannote + `HF_TOKEN` setup
- [user/user-guide.md](../user/user-guide.md): note that audio diarization is automatic; manual edit still supported
- Fixture: short two-speaker audio sample in `tests/fixtures/audio/` (or synthetic mock for CI)

### Dependencies & ops

| Item | Notes |
|------|-------|
| `pyannote.audio` | Optional extra: `pip install -e ".[diarization]"` |
| Hugging Face token | Accept pyannote model terms; set `HF_TOKEN` in `.env` |
| GPU | Recommended for pyannote + Whisper on long files; CPU fallback supported |
| Privacy | All processing remains local; no audio sent to cloud APIs |

### Testing

- Unit: alignment logic (mock diarization + Whisper segments, overlap edge cases)
- Integration: mocked pyannote pipeline → ingest → ≥2 speakers in bundle
- Regression: diarization disabled → existing `Speaker 1` fallback unchanged

**Acceptance:** Two-speaker test audio → stored transcript with ≥2 speakers, labeled turns, and valid quote IDs; workflows run without manual relabeling.

**Effort:** 5–8 days

---

## 5. Phase N — Workflow completeness

**Goal:** Close product vision use cases **5 (Full Multidisciplinary Suite)** and add a research-oriented option.

### N1 — `full_multidisciplinary` workflow

```text
All transcript-input modules (12) → meta_synthesis
```

- New `config/workflows/full_multidisciplinary.yaml`
- `estimated_runtime`: 15–45 min; `recommended_model` per [model-setup.md](../user/model-setup.md)
- Default `background: true` in API/UI for this workflow
- Integration test with mocked LLM (pattern from existing workflow tests)

### N2 — `research_oriented` workflow (optional but small)

Suggested module chain:

```text
relationship_conversation_analysis → cognitive_analysis → narrative_identity_analysis
  → bias_epistemic_quality → systems_analysis → meta_synthesis
```

Targets researchers / pattern study without clinical-heavy modules.

### N3 — Workflow guardrails

- Max modules per synchronous run (env `WORKFLOW_SYNC_MODULE_LIMIT`)
- UI warning for long suites; progress polling when `background=true`

**Acceptance:** `full_multidisciplinary` completes in background; synthesis uses all module outputs; tests pass.

**Effort:** 2–3 days

---

## 6. Phase O — Ontology & construct population

**Goal:** Make knowledge graph and cross-module reasoning **data-rich**, per [04_knowledge_ontology.md](04_knowledge_ontology.md) and [16_additional_thoughts.md](16_additional_thoughts.md).

### Problem

Exploration `knowledge-graph` endpoints work, but LLM outputs usually return empty `constructs` / `relationships`, so the graph UI is empty in practice.

### O1 — Compiler & schema nudges

- Extend `output_schema_instructions.md` with construct minimums for relational modules
- `PromptCompiler` optional section: ontology cheat-sheet (construct categories)
- Validator soft warnings → retry when `constructs` empty for modules that require them (config flag per module YAML: `expects_constructs: true`)

### O2 — Finding ↔ construct linking

- Post-parse pass: auto-suggest `construct_ids` on findings from title/type keywords (ontology map in `config/framework/construct_ontology.yaml`)
- Drill-down API returns populated `linked_constructs` more often

### O3 — Exploration presets

Add structured follow-up templates (not free-form only):

| Preset | Question shape |
|--------|----------------|
| `why` | Why was this conclusion reached? |
| `evidence` | What evidence supports/contradicts this? |
| `counterfactual` | What would change this conclusion? |
| `agreement` | Which modules agree or disagree on this finding? |

API: `POST .../exploration/ask` accepts `preset` enum; UI buttons in Explore tab.

**Acceptance:** Golden fixture run produces ≥2 constructs for relationship + NVC modules; preset counterfactual returns scoped answer citing quote IDs.

**Effort:** 4–6 days

---

## 7. Phase P — Cases & longitudinal analysis

**Goal:** Support **multiple transcripts over time** ([15](15_future_roadmap.md) comparative analysis).

### P1 — Domain model

```text
Case
  id, title, created_at, notes (user text)
Transcript.case_id (optional FK)
```

- Alembic migration `002_cases.py`
- API: `POST/GET /api/cases`, `PATCH /api/transcripts/{id}` to assign case

### P2 — Longitudinal comparison

Extend exploration service:

- `POST /api/exploration/compare-transcripts` — findings/themes across transcripts in a case
- Metrics: recurring quote IDs, new vs resolved themes, confidence shifts (heuristic)

### P3 — Streamlit

- Optional “Assign to case” on ingest
- Case dashboard: list transcripts, runs, trend summary

**Acceptance:** Two transcripts in one case → comparison report without re-running workflows.

**Effort:** 4–5 days

---

## 8. Phase Q — Custom workflows

**Goal:** [Module customization](15_future_roadmap.md) without editing YAML.

- `POST /api/workflows/custom/run` body: `{ transcript_id, module_ids[], model?, background? }`
- Validate: all modules exist, transcript input type, meta_synthesis last if included
- Streamlit: multi-select module picker + “Run custom”
- Optional: `output_tone` / `inference_depth` passed to compiler context

**Acceptance:** User selects any 3 modules and gets persisted workflow run + report.

**Effort:** 3–4 days

---

## 9. Phase R — UX & professional polish (Streamlit)

**Goal:** Close gaps in [11_ui_ux_design.md](11_ui_ux_design.md) without React.

| Task | Notes |
|------|-------|
| Human-readable confidence labels | Map enum → “Directly observed”, etc. |
| `API_KEY` in Streamlit client | Header when `API_KEY` set in UI env |
| Background workflow toggle | Expose Phase K flag in Analyze step |
| Coaching action plan export | Short actionable markdown (distinct from coach summary) |
| Finding feedback | `POST .../findings/{key}/feedback` helpful/unhelpful + optional note |
| Supervision export template | Anonymized, module-attributed, limitations prominent |

**Acceptance:** Private deploy with `API_KEY` works from UI; confidence badges use plain language.

**Effort:** 3–5 days

---

## 10. Phase S — React frontend (parallel track)

**Goal:** Exploration-first SPA consuming existing APIs ([implementation_plan](implementation_plan.md) Phase L deferral).

### Scope (MVP)

- Vite + React + TypeScript
- Pages: transcript list, workflow run status, report, explore (drill-down + ask)
- No duplicate business logic — API only
- Auth: `X-API-Key` header from env

### Non-goals (R1)

- Full feature parity with Streamlit ingest/audio
- Mobile-native layout

**Acceptance:** Complete explore journey for a stored workflow run without Streamlit.

**Effort:** 2–3 weeks

---

## 11. Ongoing — Evaluation & real-world hardening

Run alongside every phase ([14_testing_evaluation_and_safety.md](14_testing_evaluation_and_safety.md)):

| Priority | Task |
|----------|------|
| P0 | Burn-in: run `quick_review`, `conflict_coaching`, `full_mvp` on real transcripts with your Ollama models |
| P0 | Tune `DEFAULT_OLLAMA_MODEL` and per-module overrides ([MODEL_SETUP.md](MODEL_SETUP.md)) |
| P1 | Add 3–5 anonymized real scenarios to `tests/fixtures/transcripts/` |
| P1 | Track safety validator false positives; adjust patterns |
| P2 | Script: `scripts/eval_construct_coverage.py` — % runs with constructs populated |

---

## 12. Explicitly out of scope (v0.4+)

Unchanged from original MVP boundaries unless requirements shift:

- Multi-user SaaS, billing, RBAC beyond API key
- Ontology-driven prompt **generation** (static prompts + metadata remain)
- Graph database backend
- Tone/emotion inference from audio timing
- Distributed queue (Celery/Redis) — thread pool is enough for private use

---

## 13. Suggested release milestones

| Release | Phases | Theme |
|---------|--------|-------|
| **v0.3.1** | M0 | Docs only |
| **v0.4.0** | M | Speaker diarization + labeled audio ingest |
| **v0.4.1** | N | Full multidisciplinary workflow + research-oriented option |
| **v0.5.0** | O + P | Ontology-rich outputs + cases / custom workflows |
| **v0.6.0** | Q + R | Streamlit professional polish |
| **v1.0.0** | S | React UI + stable API contract |

---

## 14. Next PR checklist (Phase M — diarization)

```text
[ ] git checkout main && pull
[ ] Add optional dependency group [diarization] (pyannote.audio, torch constraints)
[ ] DIARIZATION_* and HF_TOKEN settings + .env.example
[ ] diarization_service.py + transcript_alignment_service.py
[ ] Integrate with whisper orchestrator + transcription API
[ ] Health check + check_prerequisites.py
[ ] Streamlit: speaker count + fallback messaging
[ ] tests: alignment unit tests + mocked integration
[ ] pytest tests/ -q
[ ] doc/user/model-setup.md + user-guide.md updates
```

---

## 15. Decision log

| Decision | Rationale |
|----------|-----------|
| Diarization before full-suite workflow | Audio ingest is broken for multi-speaker use cases; modules need labeled turns |
| pyannote over Whisper-only | Whisper does not diarize; pyannote is the standard local OSS path |
| Align diarization → Whisper segments | Reuse existing segment timestamps; avoid re-architecting evidence index |
| Graceful fallback | Users without HF_TOKEN or GPU still get transcription (Speaker 1) |
| Streamlit before React | Faster iteration; APIs already exploration-ready |
| Constructs before React | Graph UI useless without data |
| Cases before custom workflows | Longitudinal use is higher value for coach/therapist personas |
| SQLite remains default | PostgreSQL path exists; no forced migration |
| Full multidisciplinary after diarization | All prompts shipped; workflow YAML is a smaller gap once audio ingest works |
