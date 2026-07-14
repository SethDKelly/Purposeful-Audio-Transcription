# Architecture overview

High-level map of the RRE codebase. Deep design specs live in [../design/](../design/).

## System diagram

```text
┌─────────────────────────────────────────────────────────────┐
│  Streamlit UI (ui/)                                          │
│  Ingest · Prepare · Analyze · Report · Explore               │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP (ui/api_client.py)
┌──────────────────────────▼──────────────────────────────────┐
│  FastAPI (backend/main.py)                                   │
│  /transcripts · /workflows · /modules · /exploration         │
└──────────────────────────┬──────────────────────────────────┘
                           │
     ┌─────────────────────┼─────────────────────┐
     ▼                     ▼                     ▼
 TranscriptService   WorkflowEngine      ExplorationService
 EvidenceIndex       ModuleRunner        SynthesisEngine
                     PromptCompiler      WorkflowJobService
                     OutputParser
                     SafetyValidator
     ┌─────────────────┴─────────────────┐
     ▼                                     ▼
 AudioTranscriptionService            OllamaService (LLM)
   WhisperService · DiarizationService
   TranscriptAlignmentService
                           │
                     SQLite / PostgreSQL (SQLAlchemy + Alembic)
```

## Core services

| Service | Role |
|---------|------|
| `AudioTranscriptionService` | Whisper + pyannote diarization → labeled transcript |
| `WhisperService` | faster-whisper transcription with segment timestamps |
| `DiarizationService` | pyannote speaker timeline (optional; requires `HF_TOKEN`) |
| `TranscriptAlignmentService` | Map Whisper segments to speaker labels (Person A / B) |
| `TranscriptService` | Parse, ingest, store transcripts with speakers, turns, quotes |
| `EvidenceIndexService` | Assign `Q001…` quote IDs with context |
| `ModuleRegistry` | Load `config/modules/*.yaml` |
| `WorkflowRegistry` | Load `config/workflows/*.yaml` |
| `PromptCompiler` | Build LLM messages from framework + module + evidence |
| `ModuleRunner` | Run module → parse JSON → validate → retry |
| `WorkflowEngine` | Sequential modules; resume incomplete runs |
| `WorkflowJobService` | Background thread-pool execution |
| `SynthesisEngine` | Cross-module report from module outputs |
| `ExplorationService` | Drill-down, compare, follow-up Q&A |

## Domain layer

`backend/domain/` — Pydantic models: `Transcript`, `Finding`, `ModuleRun`, `WorkflowRun`, `SynthesisReport`, etc.

## Persistence

- **SQLite** default (`data/rre.db`)
- **PostgreSQL** via `DATABASE_URL`
- **Alembic** migrations in `alembic/versions/`
- Repositories in `backend/repositories/`

## Configuration

| Path | Purpose |
|------|---------|
| `config/modules/*.yaml` | Module metadata, prompt file, model override |
| `config/workflows/*.yaml` | Module sequences, tone, runtime hints |
| `config/prompts/*.md` | LLM prompt templates |
| `config/framework/` | Shared instructions and output schema |
| `.env` | Runtime settings (`config/settings.py`) |

## Extension points

### Add a module

1. Add prompt in `config/prompts/`
2. Add YAML in `config/modules/`
3. Register is automatic via `ModuleRegistry`
4. Add to a workflow YAML or test via `POST /api/modules/{id}/run`

### Add a workflow

1. Create `config/workflows/my_workflow.yaml`
2. List modules in order; set `meta_synthesis: true` if last step is synthesis

### Add an API route

1. Route in `backend/api/routes/`
2. Schema in `backend/api/schemas.py`
3. Register router in `backend/main.py`
4. Integration test in `tests/`

## Auth and logging

- `APIKeyMiddleware` — optional `X-API-Key` when `API_KEY` set
- `logging_config.py` — JSON structured logs when `LOG_JSON=true`

## Related design docs

- [../design/02_system_architecture.md](../design/02_system_architecture.md)
- [../design/03_domain_model.md](../design/03_domain_model.md)
- [../design/08_workflow_engine.md](../design/08_workflow_engine.md)
- [../design/10_synthesis_engine.md](../design/10_synthesis_engine.md)
