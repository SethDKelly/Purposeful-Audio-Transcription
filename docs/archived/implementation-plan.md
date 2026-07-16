# Pre-RRE implementation plan (archived)

> **Archived.** Original Whisper + Ollama phased build before the RRE redesign. Canonical: [../planning/completed.md](../planning/completed.md) · [../planning/implementing.md](../planning/implementing.md). Prompt layout: [../../config/prompts/README.md](../../config/prompts/README.md).

---

# Implementation Plan: Purposeful Audio Transcription

A local-first application that uploads audio from the user's machine, transcribes it with **Whisper**, and analyzes the transcript with **Ollama**. Ollama does not process raw audio natively, so Python bridges a local Whisper library with Ollama's text inference engine.

---

## Goals

| Goal | Description |
|------|-------------|
| **Upload** | Pick or drag-and-drop audio from local storage |
| **Transcribe** | Run local Whisper in Python |
| **Analyze** | Send transcript to a local Ollama LLM for configurable purposes |
| **Extensible** | Plug in new analysis models/prompts without rewriting core logic |
| **Local-only** | No cloud dependency; runs entirely on the user's machine |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  UI (Streamlit — Phase 2)                               │
│  - Upload audio                                         │
│  - Show transcript                                      │
│  - Select purpose / run analysis                        │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP
┌────────────────────▼────────────────────────────────────┐
│  Python Backend (FastAPI)                               │
│  1. Save upload → temp file                             │
│  2. whisper.transcribe() → text                         │
│  3. ollama.chat(model, prompt + transcript) → analysis  │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
  Local Whisper              Ollama (:11434)
  (faster-whisper)           (LLM inference)
```

---

## Tech Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Language | Python 3.11+ | Whisper ecosystem, Ollama client libraries |
| Transcription | `faster-whisper` | Faster and lighter than `openai-whisper` |
| LLM | Ollama HTTP API (`ollama` package) | Local inference, simple chat API |
| API | FastAPI + Uvicorn | Multipart uploads, OpenAPI docs, async |
| UI (Phase 2) | Streamlit | Rapid local UI with file upload and progress |
| Config | `pyproject.toml` + `.env` + `config/purposes.yaml` | Reproducible deps; secrets in env |
| Audio prep | ffmpeg (system) | Format conversion for mp3/m4a/wav |

---

## Project Structure

```
Purposeful-Audio-Transcription/
├── docs/
│   └── implementation-plan.md     # This document
├── pyproject.toml
├── .env.example
├── README.md
│
├── config/
│   ├── settings.py                # Pydantic settings from env
│   ├── purposes.yaml              # Purpose definitions
│   └── prompts/                   # System prompt files (Markdown)
│       ├── README.md
│       ├── 01 Relationship Conversation Analysis.md
│       └── ...
│
├── backend/
│   ├── main.py                    # FastAPI app entry
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py
│   │   │   ├── transcribe.py
│   │   │   └── analyze.py         # Phase 3
│   │   └── schemas.py
│   │
│   ├── services/
│   │   ├── whisper_service.py
│   │   ├── ollama_service.py
│   │   ├── audio_service.py
│   │   └── orchestrator.py        # Phase 3
│   │
│   └── core/
│       ├── purpose_registry.py    # Phase 3
│       └── exceptions.py
│
├── ui/
│   └── streamlit_app.py           # Phase 2
│
├── scripts/
│   ├── check_prerequisites.py
│   └── run_dev.ps1                # Phase 2
│
└── tests/
    ├── test_whisper_service.py
    ├── test_ollama_service.py
    └── test_orchestrator.py
```

---

## Data Flow

### Flow 1: Transcription

```
1. User selects audio file (mp3, wav, m4a, flac, ogg)
2. UI sends multipart POST → /api/transcribe
3. audio_service validates size/format, writes to temp dir
4. whisper_service.transcribe(path) → { text, segments[], language, duration }
5. Temp file deleted; transcript returned to UI
6. UI displays transcript
```

### Flow 2: Purpose-driven analysis (Phase 3)

```
1. User selects a "purpose" from dropdown (from purposes.yaml)
2. User clicks "Analyze" with transcript
3. POST → /api/analyze { transcript, purpose_id, ollama_model? }
4. purpose_registry loads: system_prompt, user_prompt_template, default_model
5. ollama_service.chat(system, user_prompt.format(transcript=...))
6. Response returned to UI
```

---

## API Design

| Method | Endpoint | Phase | Purpose |
|--------|----------|-------|---------|
| `GET` | `/api/health` | 1 | ffmpeg, Ollama, Whisper status |
| `GET` | `/api/models/ollama` | 1 | List locally available Ollama models |
| `POST` | `/api/transcribe` | 1 | Upload audio → transcript |
| `GET` | `/api/purposes` | 3 | List configured analysis purposes |
| `POST` | `/api/analyze` | 3 | Transcript + purpose → analysis |
| `POST` | `/api/process` | 4 | Upload + purpose → transcript + analysis |

---

## Purpose Registry & Prompt Storage

Purpose-specific models and prompts are defined in `config/purposes.yaml`. System prompts are stored as Markdown files in `config/prompts/` and referenced by filename.

```yaml
purposes:
  conversation_analyzer:
    name: "Conversation Analyzer"
    enabled: true
    ollama_model: null
    system_prompt_file: "01 Relationship Conversation Analysis.md"
    user_prompt_template: |
      Analyze the following conversation transcript according to your instructions.

      ---
      {transcript}
      ---
```

See [config/prompts/README.md](../config/prompts/README.md) for how to add new purposes.

---

## Implementation Phases

### Phase 1 — Foundation

- [x] `pyproject.toml` with FastAPI, faster-whisper, ollama, pydantic-settings
- [x] Settings and logging
- [x] `audio_service`: validation, temp files, ffmpeg check
- [x] `whisper_service`: model load (lazy singleton), transcribe
- [x] `ollama_service`: health check, list models, chat
- [x] FastAPI routes: `/health`, `/transcribe`, `/models/ollama`
- [x] `scripts/check_prerequisites.py`

**Exit criteria:** Upload a wav file via API and get a transcript back.

### Phase 2 — UI & Transcription UX

- [x] Streamlit app with upload, progress, transcript display
- [x] Sidebar health indicators
- [x] Copy/download transcript
- [x] `run_dev.ps1` to start API + Streamlit together
- [x] README with Windows setup steps

**Exit criteria:** End-to-end transcription through the UI.

### Phase 3 — Analysis Pipeline

- [x] `purpose_registry.py` + `config/prompts/` prompt storage
- [x] `config/purposes.yaml` with conversation analyzer purpose
- [x] `/api/analyze` and `/api/purposes`
- [x] UI Step 3 with purpose and model selection
- [x] Markdown rendering for analysis output
- [x] Export analysis as `.md` / `.json`

**Exit criteria:** Analysis works once purposes are enabled in config.

### Phase 4 — Purpose Models & Polish

- [x] Add purpose entries to `purposes.yaml` for all prompt files
- [x] Enable purpose dropdown in UI
- [x] Streaming analysis responses (`/api/analyze/stream`)
- [x] Transcript editing before analysis
- [x] `/api/process` one-shot endpoint
- [ ] Set per-purpose `ollama_model` when models are chosen (deferred)

**Exit criteria:** All intended analysis purposes work with chosen Ollama models.

### Phase 5 — Hardening (Optional)

- [ ] Async job queue for long files
- [ ] Unit + integration tests with mocked Ollama/Whisper
- [ ] Rate limiting and stricter file validation
- [ ] React frontend if Streamlit UX is insufficient
- [ ] PyInstaller or Docker for easier distribution

### Backlog

- [Analysis Suite](backlog-analysis-suite.md) — multi-analysis bundles (Quick, Therapeutic, Clinical Exploration, Research) with Meta-Synthesis

---

## Configuration

### Environment variables (`.env`)

```env
OLLAMA_HOST=http://localhost:11434
WHISPER_MODEL=base
WHISPER_DEVICE=auto
WHISPER_COMPUTE_TYPE=int8
MAX_UPLOAD_MB=100
TEMP_DIR=./data/temp
LOG_LEVEL=INFO
API_HOST=127.0.0.1
API_PORT=8000
```

### External prerequisites

1. **ffmpeg** on PATH
2. **Ollama** installed and running (`ollama serve`)
3. At least one **Ollama text model** pulled (`ollama pull llama3.2`)
4. Optional: **CUDA** for faster Whisper

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Whisper slow on CPU | Default to `base` + `int8`; document GPU setup; show progress |
| Large audio files OOM | Max upload size; chunk long files in Phase 5 |
| Ollama not running | Health check on startup; clear UI error with fix instructions |
| Unsupported audio format | ffmpeg conversion layer; list supported formats in UI |
| Purpose models not ready | Registry + disabled UI; transcription works independently |
| Temp file leaks | Context manager + cleanup on success/failure |

---

## Decisions

| Decision | Choice |
|----------|--------|
| UI (Phase 1) | API only; Streamlit in Phase 2 |
| Whisper variant | `faster-whisper` |
| Deployment target | Developer machine (local) |
| Transcript editing | Phase 4 (optional) |
| Analysis streaming | Phase 4 (optional) |
