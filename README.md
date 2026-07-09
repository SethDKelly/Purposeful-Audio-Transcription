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
3. Upload an audio file (wav, mp3, m4a, flac, ogg, webm, mp4)
4. Click **Transcribe**
5. Review the transcript and download it as a `.txt` file
6. Select an analysis purpose and an Ollama model (or set `DEFAULT_OLLAMA_MODEL` in `.env`)
7. Optionally edit the transcript before analysis
8. Click **Analyze transcript** (streaming enabled by default) or use **Transcribe + Analyze** for one-shot processing
9. Export the result as `.md` or `.json`

## Prompt storage

Analysis prompts are stored in `config/prompts/` and linked from `config/purposes.yaml`. See [config/prompts/README.md](config/prompts/README.md) for how to add new purposes.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Check ffmpeg, Ollama, and Whisper status |
| `GET` | `/api/models/ollama` | List available Ollama models |
| `GET` | `/api/purposes` | List configured analysis purposes |
| `POST` | `/api/transcribe` | Upload audio file and get transcript |
| `POST` | `/api/analyze` | Analyze a transcript for a given purpose |
| `POST` | `/api/analyze/stream` | Stream analysis tokens as plain text |
| `POST` | `/api/process` | Upload audio + purpose → transcript + analysis |

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
| `DEFAULT_OLLAMA_MODEL` | _(empty)_ | Default model for analysis when not set in purpose config |

## Project Structure

```
doc/implementation-plan.md   Full implementation plan and phase tracker
doc/backlog-analysis-suite.md  Backlog: multi-analysis suites
backend/                     FastAPI application
config/                      Settings and future purpose configs
ui/                          Streamlit UI
scripts/                     Utility scripts
```

## Implementation Status

See [doc/implementation-plan.md](doc/implementation-plan.md) for the full plan.

- **Phase 1** — Foundation (API, Whisper, Ollama services) ✓
- **Phase 2** — Streamlit UI ✓
- **Phase 3** — Transcript analysis pipeline ✓
- **Phase 4** — Purpose registration and polish ✓ (set models when ready)
- **Phase 5** — Hardening (optional)
