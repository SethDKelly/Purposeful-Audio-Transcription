# Purposeful Audio Transcription

A local-first application that transcribes audio with **Whisper** and analyzes transcripts with **Ollama**.

## Prerequisites

- Python 3.11+
- [ffmpeg](https://ffmpeg.org/download.html) on PATH
- [Ollama](https://ollama.com/) installed and running
- At least one Ollama model pulled (e.g. `ollama pull llama3.2`) — required for Phase 3 analysis

## Setup

```powershell
# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install the project
pip install -e .

# Copy environment config
copy .env.example .env

# Verify prerequisites
python scripts\check_prerequisites.py
```

## Run the application

### Option 1: Start API and UI together (recommended)

```powershell
.\scripts\run_dev.ps1
```

This starts:
- **API** at [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **UI** at [http://localhost:8501](http://localhost:8501)

Press `Ctrl+C` in the terminal to stop the UI; the script also stops the API.

### Option 2: Run services separately

Terminal 1 — API:

```powershell
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2 — UI:

```powershell
streamlit run ui/streamlit_app.py
```

## Using the UI

1. Open [http://localhost:8501](http://localhost:8501)
2. Check the sidebar for ffmpeg, Ollama, and Whisper status
3. **Ingest** — upload audio or paste/upload a transcript
4. **Prepare** — edit speaker names and review evidence quote IDs
5. **Analyze** — select a workflow (`quick_review` or `full_mvp`) and Ollama model
6. **Report** — explore findings, synthesis, evidence drill-down, interactive follow-up; export `.md` / `.json` / `.pdf`

## Prompt storage

Analysis prompts are stored in `config/prompts/` and linked from `config/modules/*.yaml`. See [config/prompts/README.md](config/prompts/README.md) for how to add new modules.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Check ffmpeg, Ollama, and Whisper status |
| `GET` | `/api/models/ollama` | List available Ollama models |
| `GET` | `/api/modules` | List analysis modules |
| `GET` | `/api/workflows` | List workflows |
| `POST` | `/api/transcripts` | Create transcript with speakers, turns, and quote IDs |
| `GET` | `/api/transcripts/{id}` | Get transcript bundle |
| `PATCH` | `/api/transcripts/{id}/speakers` | Update speaker display names |
| `POST` | `/api/transcripts/upload` | Upload `.txt` transcript file |
| `POST` | `/api/transcribe` | Upload audio file and get transcript |
| `POST` | `/api/workflows/{id}/run` | Run structured analysis workflow |
| `GET` | `/api/workflow-runs/{id}/synthesis` | Get synthesis report |
| `GET` | `/api/workflow-runs/{id}/exploration/findings` | List indexed findings for exploration |
| `GET` | `/api/workflow-runs/{id}/exploration/findings/{key}` | Finding drill-down with evidence chain |
| `GET` | `/api/workflow-runs/{id}/exploration/cross-module` | Cross-module agreement/tension explorer |
| `GET` | `/api/workflow-runs/{id}/exploration/knowledge-graph` | Construct relationship graph |
| `POST` | `/api/workflow-runs/{id}/exploration/ask` | Ask follow-up questions scoped to stored findings |
| `POST` | `/api/exploration/compare` | Compare multiple workflow runs |
| `GET` | `/api/transcripts/{id}/workflow-runs` | List completed runs for a transcript |
| `POST` | `/api/modules/{id}/stream` | Stream single-module LLM output |
| `POST` | `/api/process` | Upload audio + workflow → transcript + analysis |
| `GET` | `/api/purposes` | Deprecated alias for `/api/modules` |

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for interactive API documentation.

### Transcribe example

```powershell
curl -X POST "http://127.0.0.1:8000/api/transcribe" -F "file=@sample.wav"
```

## Configuration

See `.env.example` for available settings:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `WHISPER_MODEL` | `base` | Whisper model size (`tiny`, `base`, `small`, `medium`, `large-v3`) |
| `WHISPER_DEVICE` | `auto` | `auto`, `cpu`, or `cuda` |
| `WHISPER_COMPUTE_TYPE` | `int8` | Compute precision (`int8` for CPU, `float16` for GPU) |
| `MAX_UPLOAD_MB` | `100` | Maximum upload file size |
| `TEMP_DIR` | `./data/temp` | Temporary file storage |
| `API_HOST` | `127.0.0.1` | API bind address |
| `API_PORT` | `8000` | API port |
| `STREAMLIT_PORT` | `8501` | Streamlit UI port |
| `DEFAULT_OLLAMA_MODEL` | _(empty)_ | Default model for workflows when not set in module YAML |

## Project Structure

```
doc/implementation_plan.md     Active MVP implementation plan
doc/12_mvp_build_plan.md          MVP goals and phases
doc/01–16_*.md                    RRE design package
doc/archived/                     Earlier plans and backlogs
backend/                     FastAPI application
config/                      Settings and future purpose configs
ui/                          Streamlit UI
scripts/                     Utility scripts
```

## Deployment

For private-use setup, configuration, backup, and upgrade steps, see [doc/DEPLOYMENT.md](doc/DEPLOYMENT.md).

Model configuration: [doc/MODEL_SETUP.md](doc/MODEL_SETUP.md).

## Implementation Status

See [doc/implementation_plan.md](doc/implementation_plan.md) for the active MVP plan and post-MVP roadmap (phases H–L).

- **Phases 1–4** — Audio transcription + single-purpose analysis ✓
- **Phases A–G** — RRE MVP (transcripts, modules, workflows, synthesis, report UI, testing) ✓
- **Phase H** — Legacy cleanup ✓
- **Phase I** — Full module library (13 modules) + 5 workflows ✓
- **Phase J** — PDF export, coach/mediation summaries, redaction ✓
- **Phase K** — PostgreSQL, Alembic, background workflows, API auth ✓
- **Phase L** — Interactive exploration (drill-down, cross-module, follow-up Q&A) ✓
- **Release** — `v0.3.0` (phases H–L on `phase-h-legacy-cleanup`); `v0.2.0` (MVP on `main`)
