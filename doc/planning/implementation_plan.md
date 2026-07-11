# Implementation Plan

Active plan for the **Relationship Reasoning Engine (RRE)**. This document supersedes the forward-looking sections of [18_post_v0.3_plan.md](18_post_v0.3_plan.md) (July 2026 revision).

| | |
|---|---|
| **Status** | **v0.4.0 in progress** on branch `phase-m0-docs` |
| **Baseline** | MVP (A–G) + post-MVP (H–L) shipped in **v0.3.0**; audio/diarization (M, M1.5, M2 core) on branch |
| **Tests** | 144 passing (see [§ Platform reality](#2-platform-reality-windows--local-deployment)) |
| **Nice-to-have backlog** | [backlog.md](backlog.md) |
| **Design anchors** | [../design/01_product_vision_and_scope.md](../design/01_product_vision_and_scope.md) · [15_future_roadmap.md](15_future_roadmap.md) |
| **Deploy** | [../user/deployment.md](../user/deployment.md) · [../user/model-setup.md](../user/model-setup.md) |

---

## Document map

| Document | Purpose |
|----------|---------|
| **This document** | Prioritized implementation plan (critical → important) |
| [backlog.md](backlog.md) | Nice-to-have and deferred enhancements |
| [18_post_v0.3_plan.md](18_post_v0.3_plan.md) | Historical post-v0.3.0 plan (superseded for priorities) |
| [12_mvp_build_plan.md](12_mvp_build_plan.md) | Original MVP phase definitions |
| [15_future_roadmap.md](15_future_roadmap.md) | Long-term strategic direction |
| [../archived/](../archived/) | Earlier plans |

---

## 1. Where the project is today

### Delivered (v0.3.0 + branch work)

| Area | Status |
|------|--------|
| Transcript paste / upload + evidence index (`Q001…`) | ✓ |
| 13 modules + prompt compiler + structured JSON output | ✓ |
| 5 workflows (Quick Review, Full MVP, Conflict Coaching, Mediation Brief, Clinical Exploration) | ✓ |
| Synthesis, safety validation, exploration APIs, Streamlit Explore tab | ✓ |
| Exports (md, json, pdf, coach summary, mediation brief) | ✓ |
| PostgreSQL option, Alembic, background jobs, API key auth | ✓ |
| Speaker diarization (pyannote) + timeline smoothing (M1.5) | ✓ |
| Sliced transcription mode — diarize first, Whisper per interval (M2 core) | ✓ |
| Ollama reliability fixes — `think=false`, JSON mode, nested JSON parser | ✓ |

### Gaps vs product vision

| Vision item | Gap |
|-------------|-----|
| **5. Full Multidisciplinary Suite** | No workflow runs all 12 transcript modules + meta-synthesis |
| **Research-oriented analysis** | No dedicated workflow |
| **Reliable audio ingest on all target hosts** | Native Windows + CPU torch + pyannote/ffmpeg coupling is fragile |
| **Reproducible deployment** | Manual venv; no containers or lockfiles |
| **Long-context LLM use** | Ollama `num_ctx` / sampling not exposed; evidence caps conservative |
| **Knowledge graph value** | APIs exist; constructs rarely populated in LLM output |
| **Longitudinal / case view** | Compare runs on one transcript only |
| **Custom workflows** | Fixed YAML only |
| **React frontend** | Deferred; Streamlit remains primary UI |

### Completed history (reference)

Phases **A–G** (MVP), **H–L** (post-MVP expansion), and **M0** (documentation) are complete. See [§ Appendix — completed phases](#appendix--completed-phases) for the record.

---

## 2. Platform reality: Windows & local deployment

Real-world use on **native Windows** exposed limits that change priority order. The reasoning platform (transcript → modules → synthesis → report) is solid; the **ML operations stack** is the bottleneck.

### Observed constraints

| Layer | Issue | Impact |
|-------|-------|--------|
| **Whisper (faster-whisper / ctranslate2)** | DLL load failures under Windows Application Control on some machines | Audio transcription blocked entirely |
| **PyTorch** | Default pip wheel is **CPU-only**; CUDA requires manual reinstall | GPU acceleration unavailable without extra steps |
| **pyannote + ffmpeg** | torchcodec unavailable on Windows; ffmpeg path dependency | Diarization warnings, decode failures if ffmpeg misconfigured |
| **Hugging Face** | Gated models require `HF_TOKEN` and runtime download | Not air-gapped; first-run friction |
| **Ollama on Windows** | Long sessions + `--reload` → socket exhaustion (`WinError 10055`) | API instability during workflow burn-in |
| **Local LLM** | Gemma 4 thinking mode, truncated JSON, default low `num_ctx` | Module failures until tuned (`think=false`, JSON mode, `num_predict`) |
| **Resource cost** | 12-module suite + large model on CPU | 15–45 min estimates unrealistic; RAM/VRAM pressure |
| **Dependency drift** | torch, pyannote, ffmpeg, Ollama versions vary by host | “Works on my machine” support burden |

### Strategic implication

**Transcript-first workflows** (paste or pre-labeled `.txt`) are the reliable core on any OS. **Audio ingest with diarization** should be treated as **best-effort on native Windows** until containerized or WSL2/Linux deployment is the documented primary path.

```text
Reliability tiers (recommended)

Tier 1 — Transcript ingest + Ollama workflows     ✓ viable on Windows today (with tuning)
Tier 2 — Audio → Whisper only (no diarization)    ✓ viable when ctranslate2 loads
Tier 3 — Audio + pyannote diarization             ⚠ fragile on native Windows; prefer Linux/WSL2/Docker
Tier 4 — Full 12-module suite on local CPU        ⚠ use background jobs + smaller models
```

---

## 3. Priority framework

| Level | Meaning | Examples |
|-------|---------|----------|
| **Critical (P0)** | Blocks reliable private use or causes frequent failure | Deployment path, Ollama tuning, M2 validation, container MVP |
| **Important (P1)** | Product completeness, trust, or professional use | Full multidisciplinary workflow, data handling, workflow guardrails |
| **Deferred (P2)** | Valuable after platform is stable | Cases, custom workflows, ontology population, Streamlit polish |
| **Nice-to-have** | See [backlog.md](backlog.md) | React UI, Helm, audio timing analysis, collaborative review |

**Principle:** Stabilize the **deployment and inference substrate** before adding features that multiply runtime (full suite, constructs, cases).

---

## 4. Implementation plan (priority order)

Work top to bottom. Each phase has acceptance criteria; do not skip P0 items to chase product gaps.

---

### P0-1 — Deployment & platform guidance

**Goal:** Operators can choose a supported path and avoid known Windows failure modes.

| # | Task | Priority | Status |
|---|------|----------|--------|
| P0-1a | Document **Windows limitations** and recommended paths: native (transcript-first), WSL2, Docker (when available) | Critical | [ ] |
| P0-1b | Document **production run mode**: no uvicorn `--reload`; restart API after long Ollama sessions | Critical | [ ] |
| P0-1c | Extend `scripts/check_prerequisites.py` — report torch CUDA, ctranslate2 load, ffmpeg, HF_TOKEN, Ollama model | Critical | [ ] |
| P0-1d | Add **troubleshooting** section to [deployment.md](../user/deployment.md) (DLL, WinError 10055, diarization skip reasons) | Critical | [ ] |

**Acceptance:** New user on Windows can follow docs, identify their tier, and run `quick_review` on a pasted transcript without hitting undocumented failures.

**Effort:** 1–2 days

---

### P0-2 — Ollama inference tuning (model-agnostic)

**Goal:** Reliable structured JSON from local models without hardcoding model names.

| # | Task | Priority | Status |
|---|------|----------|--------|
| P0-2a | Add `OLLAMA_NUM_CTX`, `OLLAMA_TEMPERATURE`, `OLLAMA_TOP_P` to settings; pass via Ollama `options` | Critical | [ ] |
| P0-2b | Document context tiers in [model-setup.md](../user/model-setup.md) (e.g. 8K–32K typical; avoid max 256K on CPU) | Critical | [ ] |
| P0-2c | Optional: scale `EVIDENCE_PROMPT_*` when context budget allows (env-driven, not model-specific) | Important | [ ] |

**Acceptance:** Quick Review completes on Gemma 4 / Llama with documented `.env`; no Gemma-specific branches in application code.

**Effort:** 1 day

---

### P0-3 — Phase M2 completion (sliced transcription)

**Goal:** Validate and polish diarize-first pipeline; keep overlap fallback.

| # | Task | Priority | Status |
|---|------|----------|--------|
| P0-3a | Streamlit progress: `Diarizing…` → `Transcribing N segments…` | Critical | [ ] |
| P0-3b | Fixture audio validation: sliced vs overlap quality comparison | Critical | [ ] |
| P0-3c | Fix or skip Windows-specific ffmpeg waveform test (`test_diarization_audio.py`) with clear CI/local policy | Critical | [ ] |
| P0-3d | Document `TRANSCRIPTION_MODE=sliced|overlap` tradeoffs in user guide | Important | [ ] |

**Acceptance:** Two-speaker fixture produces labeled turns; UI shows progress; overlap fallback unchanged when diarization disabled.

**Effort:** 2–3 days

---

### P0-4 — Containerized deployment MVP (Phase T-lite)

**Goal:** Reproducible Linux path for ffmpeg + torch + pyannote + API; reduces Windows ML fragility.

| # | Task | Priority | Status |
|---|------|----------|--------|
| P0-4a | `Dockerfile` — API, system ffmpeg, optional `[diarization]` build arg | Critical | [ ] |
| P0-4b | `docker-compose.yml` — `api`, `streamlit`, `ollama` (profile), volume mounts for models and `data/` | Critical | [ ] |
| P0-4c | `.env.docker.example` + smoke script (health + fixture transcribe or transcript workflow) | Critical | [ ] |
| P0-4d | Document GPU passthrough and model volume strategy | Important | [ ] |

**Acceptance:** Clean Linux host with Docker runs ingest (transcript or audio with diarization image) + `quick_review` without manual ffmpeg/torch alignment.

**Effort:** 1–2 weeks

---

### P1-1 — Workflow completeness (Phase N)

**Goal:** Close product vision **§5 Full Multidisciplinary Suite** and research-oriented option.

| # | Task | Priority | Status |
|---|------|----------|--------|
| P1-1a | `config/workflows/full_multidisciplinary.yaml` — all 12 transcript modules → meta_synthesis | Important | [ ] |
| P1-1b | Optional `research_oriented.yaml` | Important | [ ] |
| P1-1c | Default `background: true` for long workflows in API/UI | Important | [ ] |
| P1-1d | `WORKFLOW_SYNC_MODULE_LIMIT` env guardrail | Important | [ ] |
| P1-1e | Integration tests with mocked LLM | Important | [ ] |

**Acceptance:** Full suite completes in background; synthesis receives all module outputs; UI warns on long synchronous runs.

**Effort:** 2–3 days

**Note:** Defer burning in full suite on native Windows CPU until P0-2 and P0-4 are done.

---

### P1-2 — Data handling & trust (Phase U-lite)

**Goal:** Privacy-sensitive users can trust local processing and delete data.

| # | Task | Priority | Status |
|---|------|----------|--------|
| P1-2a | Audit temp audio deletion on all transcribe paths (`finally` blocks) | Important | [ ] |
| P1-2b | `DELETE /api/transcripts/{id}` with cascade to runs/reports (if missing) | Important | [ ] |
| P1-2c | Streamlit ingest privacy copy: processed locally, no vendor cloud | Important | [ ] |
| P1-2d | Log redaction: no transcript body in production logs by default | Important | [ ] |

**Acceptance:** Security reviewer confirms temp files removed after transcribe; operator can purge transcript via API.

**Effort:** 2–3 days

---

### P1-3 — Real-world evaluation loop

**Goal:** Continuous validation on real transcripts and models (ongoing, every release).

| # | Task | Priority | Status |
|---|------|----------|--------|
| P1-3a | Burn-in: `quick_review`, `conflict_coaching`, `full_mvp` on real transcripts | Important | [ ] |
| P1-3b | Add 3–5 anonymized scenarios to `tests/fixtures/transcripts/` | Important | [ ] |
| P1-3c | Track safety validator false positives; tune patterns | Important | [ ] |
| P1-3d | Per-module `ollama_model` overrides documented for `meta_synthesis` | Important | [ ] |

**Effort:** Ongoing

---

### P2-1 — Ontology & construct population (Phase O)

**Goal:** Knowledge graph and drill-down become data-rich.

| # | Task | Priority | Status |
|---|------|----------|--------|
| P2-1a | Schema nudges + optional `expects_constructs` per module YAML | Deferred | [ ] |
| P2-1b | Post-parse construct linking from ontology map | Deferred | [ ] |
| P2-1c | Exploration presets: `why`, `evidence`, `counterfactual`, `agreement` | Deferred | [ ] |

**Effort:** 4–6 days

---

### P2-2 — Cases & longitudinal analysis (Phase P)

**Goal:** Multiple transcripts over time for coach/therapist personas.

| # | Task | Priority | Status |
|---|------|----------|--------|
| P2-2a | `Case` domain model + Alembic migration | Deferred | [ ] |
| P2-2b | `POST /api/exploration/compare-transcripts` | Deferred | [ ] |
| P2-2c | Streamlit case dashboard | Deferred | [ ] |

**Effort:** 4–5 days

---

### P2-3 — Custom workflows (Phase Q)

**Goal:** Power users select modules without editing YAML.

| # | Task | Priority | Status |
|---|------|----------|--------|
| P2-3a | `POST /api/workflows/custom/run` | Deferred | [ ] |
| P2-3b | Streamlit multi-select module picker | Deferred | [ ] |

**Effort:** 3–4 days

---

### P2-4 — Streamlit UX & professional polish (Phase R)

**Goal:** Close [11_ui_ux_design.md](../design/11_ui_ux_design.md) gaps without React.

| # | Task | Priority | Status |
|---|------|----------|--------|
| P2-4a | Plain-language confidence labels in UI | Deferred | [ ] |
| P2-4b | `API_KEY` header in Streamlit client when configured | Deferred | [ ] |
| P2-4c | Background workflow toggle in Analyze step | Deferred | [ ] |
| P2-4d | Finding feedback endpoint | Deferred | [ ] |
| P2-4e | Supervision export template | Deferred | [ ] |

**Effort:** 3–5 days

---

### P2-5 — Full air-gapped deployment (Phase U)

**Goal:** Internet-disconnected hosts with pre-staged models.

| # | Task | Priority | Status |
|---|------|----------|--------|
| P2-5a | `doc/user/air-gapped-deployment.md` | Deferred | [ ] |
| P2-5b | `ALLOW_OUTBOUND_HTTP=false` startup check | Deferred | [ ] |
| P2-5c | Retention policy + optional encryption guidance | Deferred | [ ] |

**Effort:** 3–5 days (docs + flags); +1 week for retention APIs

**Depends on:** P0-4 container/model volume strategy

---

## 5. Suggested release milestones

| Release | Phases | Theme |
|---------|--------|-------|
| **v0.4.0** | M, M1.5, M2 core, Ollama JSON fixes | Diarization + sliced transcription + LLM reliability |
| **v0.4.1** | P0-1, P0-2, P0-3 | Windows guidance, Ollama tuning, M2 polish |
| **v0.5.0** | P0-4, P1-2 | Docker Compose + data handling |
| **v0.5.1** | P1-1 | Full multidisciplinary + research workflows |
| **v0.6.0** | P2-1, P2-2 | Ontology-rich outputs + cases |
| **v0.7.0** | P2-3, P2-4 | Custom workflows + Streamlit professional polish |
| **v0.8.0** | P2-5 | Air-gapped deployment |
| **v1.0.0** | Backlog: React UI | API-stable SPA (see [backlog.md](backlog.md)) |

---

## 6. Explicitly out of scope

Unless requirements change:

- Multi-user SaaS, billing, RBAC beyond API key
- Ontology-driven prompt **generation** (static prompts + metadata remain)
- Graph database backend
- Tone/emotion inference from audio timing
- Distributed queue (Celery/Redis) — thread pool sufficient for private use
- Hardcoded per-model branches in application code

---

## 7. Decision log (July 2026 revision)

| Decision | Rationale |
|----------|-----------|
| Reprioritize containerization to **P0** | Native Windows ML stack failures block audio ingest; Linux/Docker is the durable fix |
| Transcript-first as **Tier 1** deployment | Core RRE value does not require audio; de-risks Windows |
| Ollama tuning before full multidisciplinary suite | 12-module runs fail or truncate without ctx/sampling fixes |
| M2 polish before Phase N burn-in | Sliced transcription unvalidated on fixture audio |
| Keep SQLite default | PostgreSQL path exists; no forced migration |
| Nice-to-have items → [backlog.md](backlog.md) | React, Helm, audio timing, collaborative review do not unblock current failures |
| Supersede 18_post_v0.3_plan priority order | Original plan assumed stable local ML on Windows; experience proved otherwise |

---

## 8. Next PR checklist

Recommended immediate work (P0-1 + P0-2):

```text
[ ] doc/user/deployment.md — Windows limitations + troubleshooting
[ ] doc/user/model-setup.md — OLLAMA_NUM_CTX, temperature tiers
[ ] config/settings.py + backend/services/ollama_service.py — generic Ollama options
[ ] .env.example — new Ollama settings
[ ] tests/test_ollama_service.py — options passthrough
[ ] pytest tests/ -q
```

M2 polish (P0-3) can follow in the same or next PR.

---

## Appendix — completed phases

Historical record. Do not re-implement.

### MVP (Phases A–G) ✓

Domain foundation, module registry, prompt compiler, structured module runner, workflow engine, synthesis engine, report UI, testing & hardening. **96 tests** at v0.3.0 release.

### Post-MVP (Phases H–L) ✓

| Phase | Deliverable |
|-------|-------------|
| H | Legacy cleanup — modules/workflows only |
| I | 13 modules, 5 workflows |
| J | PDF, coach summary, mediation brief exports |
| K | PostgreSQL, Alembic, background jobs, API key, structured logging |
| L | Exploration APIs, drill-down, comparative analysis, knowledge graph API |

### Phase M0 ✓

Documentation reorganization under `doc/user/`, `doc/developer/`, `doc/design/`, `doc/planning/`.

### Phase M — Speaker diarization ✓

`diarization_service`, `transcript_alignment_service`, `audio_transcription_service`, health checks, optional `[diarization]` extra.

### Phase M1.5 — Timeline smoothing ✓

`diarization_timeline.py`, `DIARIZATION_MIN_DURATION_ON/OFF`, unit tests.

### Phase M2 — Sliced transcription (core ✓, polish open)

`audio_slicing.py`, `whisper_service.transcribe_speaker_intervals()`, `TRANSCRIPTION_MODE=sliced|overlap`, `transcription_mode` in API response. Remaining: UI progress, fixture validation (see P0-3).

### Ollama reliability (branch) ✓

`OLLAMA_THINK=false`, `OLLAMA_MODULE_JSON_FORMAT`, balanced JSON extraction, `OLLAMA_NUM_PREDICT=8192`.
