# 15 — Future Roadmap

> **Active priorities (July 2026):** See [implementation_plan.md](implementation_plan.md) for ordered P0–P2 work and [backlog.md](backlog.md) for nice-to-haves. This document retains long-term strategic direction.

> **Completed items:** Many near-term items below shipped in **v0.3.0** (phases H–L). See [../releases/v0.3.0.md](../releases/v0.3.0.md).

## Completed in v0.3.0

- Remaining modules (13 total) and workflows (5): Quick Review, Conflict Coaching, Mediation Brief, Clinical Exploration, Full MVP
- Export options: Markdown, PDF, JSON, coach summary, mediation brief
- Knowledge graph + interactive exploration APIs and Streamlit Explore tab
- PostgreSQL, migrations, background jobs, API key auth
- Comparative analysis (workflow runs on same transcript)

## Near-Term Enhancements (remaining)

### Speaker diarization (Phase M — shipped)

**Status:** Implemented. Audio upload runs Whisper + optional [pyannote.audio](https://github.com/pyannote/pyannote-audio) diarization, aligns segments to **Person A / Person B** turns, and ingests labeled quotes.

Setup: `pip install -e ".[diarization]"`, accept Hugging Face model terms, set `HF_TOKEN` in `.env`. See [18_post_v0.3_plan.md](18_post_v0.3_plan.md) §4 and [user/model-setup.md](../user/model-setup.md).

### Workflow library (gaps)

- **Full Multidisciplinary Suite** — all transcript modules + meta-synthesis
- **Research-Oriented Analysis** — pattern-focused module chain

### Knowledge Graph UI

Show relationships between needs, behaviors, emotions, cycles, narratives, interventions.

**Status:** API + basic Streamlit Mermaid in v0.3.0; needs richer construct population (see Phase O in [18_post_v0.3_plan.md](18_post_v0.3_plan.md)).

### Interactive Exploration

**Status:** Drill-down, cross-module, follow-up Q&A in v0.3.0. Remaining:

- What would change this conclusion? (preset counterfactuals)
- React frontend

### Comparative Analysis

**Status:** Compare workflow runs on one transcript in v0.3.0. Remaining:

- Cross-transcript / case-level progress tracking
- Pattern change and theme evolution over time

### Module Customization

Allow advanced users to:

- include/exclude modules
- adjust depth
- choose coaching vs clinical tone
- choose output format

## Long-Term Enhancements

### Platform, deployment & data sovereignty (backlog)

**Status:** Backlog — improves reliability of complex dependencies (ffmpeg, torch, pyannote, Ollama) and addresses user concerns that audio/transcript data could leave their environment.

**Problem today:** Private installs depend on host PATH (ffmpeg/ffprobe), optional Hugging Face downloads at runtime, manually aligned Python/torch/pyannote versions, and ad hoc `.env` secrets. Diarization on Windows exposed torchcodec/FFmpeg fragility; reliability varies by machine.

#### T — Containerization & reproducible deployments

| Item | Notes |
|------|-------|
| **Dockerfile(s)** | Multi-stage image: API (FastAPI), optional Streamlit UI, pinned Python + system ffmpeg |
| **Compose stack** | `docker compose` with services: `api`, `ui`, `ollama` (or document external Ollama), `postgres` (optional) |
| **Dependency bundling** | Ship ffmpeg/ffprobe inside image; optional CPU/GPU torch variants; `[diarization]` extra as image tag (`:diarization`) |
| **Model volumes** | Mount or init-container for Whisper, pyannote, and Ollama model weights — avoid re-download on every pod restart |
| **Offline model bake** | Build-time or registry image that includes gated HF models after license acceptance (no runtime `hf_hub_download`) |
| **Health & startup order** | `depends_on` + readiness: Ollama up → API healthy → UI; document first-run model pull vs pre-seeded image |
| **Pinned lockfiles** | `requirements.lock` / `uv.lock` or conda export for reproducible transitive deps (torch, torchaudio, pyannote) |
| **CI image smoke tests** | `pytest` in container; transcribe fixture without host-specific PATH |
| **Helm chart (optional)** | For clinic/org deploys: ingress, secrets, PVC for `data/` and model cache |

**Acceptance:** Fresh machine with only Docker runs full ingest → workflow on a fixture transcript without manual ffmpeg/HF setup.

**Effort:** 1–2 weeks (Compose MVP); Helm optional +1 week.

#### U — Secure & air-gapped operation

| Item | Notes |
|------|-------|
| **Air-gapped install guide** | Document transfer of Ollama blobs, Whisper weights, pyannote pipeline files, and app image via removable media or internal registry |
| **No-egress mode** | Settings flag + startup check: fail or warn if outbound HTTP detected (HF, telemetry); all inference local-only |
| **Bind-local defaults** | API/UI listen on `127.0.0.1` unless explicitly configured; deployment doc warns against public exposure |
| **Secrets management** | Replace plain `.env` in production with Docker secrets, K8s secrets, or OS keychain; never commit `HF_TOKEN` |
| **Data at rest** | Encrypt `data/` volume (LUKS, BitLocker, cloud disk encryption); optional SQLCipher or PostgreSQL TDE for regulated environments |
| **Ephemeral audio handling** | Guarantee temp upload deletion on success/failure; optional `SECURE_DELETE_TEMP=true`; document that raw audio is not retained after transcribe unless user saves transcript |
| **Transcript retention policy** | Configurable TTL or manual purge API (`DELETE /api/transcripts/{id}` + cascade); export-before-delete workflow |
| **Audit logging** | Structured logs for ingest, export, delete — no transcript body in logs by default |
| **Privacy messaging** | User-facing copy: audio/transcripts stay on user infrastructure; no vendor cloud; clarify what Ollama/HF touch when not air-gapped |
| **Threat model doc** | One-pager: local trust boundary, API key scope, multi-user gaps, backup exposure |

**Acceptance:** Operator can deploy on an internet-disconnected host with pre-staged models; no audio bytes or transcript text leave the machine during normal operation.

**Effort:** 3–5 days (docs + temp-file hardening + no-egress flag); encryption/retention APIs +1 week.

See phased detail in [18_post_v0.3_plan.md](18_post_v0.3_plan.md) §16–17.

### Audio/Video Inputs

**Status:** Whisper transcription + optional speaker diarization (Phase M) shipped.

Potential future features beyond diarization:
- timing analysis
- interruption detection
- pause detection

Be cautious with tone/emotion inference.

### Collaborative Review

Allow multiple participants to:

- add context
- respond to findings
- mark findings as helpful/unhelpful
- create shared agreements

### Professional Mode

For therapists/coaches/mediators:

- case notes
- session comparison
- exportable reports
- supervision notes
- treatment planning support

### Ontology-Driven Prompt Generation

Move from static templates to generated prompts based on:

- selected constructs
- module metadata
- workflow goals
- desired output schema
- user context

## Strategic Direction

The strongest long-term architecture treats the application as a reasoning platform:

```text
Domain Model
  → Ontology
  → Module Definitions
  → Workflow Engine
  → Prompt Compiler
  → Structured Findings
  → Synthesis Engine
  → Interactive UI
```

The prompts are important, but they should remain replaceable.

The enduring assets are:

- domain model
- ontology
- evidence model
- confidence model
- workflow design
- structured data
- synthesis logic
