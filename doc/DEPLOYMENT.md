# Deployment Notes — RRE MVP (v0.2.0)

Private-use deployment guide for the **Relationship Reasoning Engine (RRE)** MVP. This application is designed to run **locally on a single machine** with Whisper and Ollama. It is not a multi-tenant hosted service.

## Release summary

| Item | Value |
|------|-------|
| Tag | `v0.2.0` |
| Scope | MVP phases A–G complete |
| Workflows | `quick_review`, `full_mvp` |
| Modules | 5 analysis modules + meta-synthesis |
| Tests | `pytest tests/ -q` (76 tests) |

## System requirements

| Component | Requirement |
|-----------|-------------|
| OS | Windows 10/11 (primary); Linux/macOS supported with manual commands |
| Python | 3.11+ |
| ffmpeg | On `PATH` (audio transcription) |
| Ollama | Running locally with at least one chat model pulled |
| RAM | 8 GB minimum; 16 GB+ recommended for larger Ollama models |
| Disk | ~2 GB for Whisper + models; SQLite DB grows with usage |
| GPU | Optional (`WHISPER_DEVICE=cuda` for faster transcription) |

## First-time install

```powershell
git clone https://github.com/SethDKelly/Purposeful-Audio-Transcription.git
cd Purposeful-Audio-Transcription
git checkout v0.2.0

python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

copy .env.example .env
# Edit .env — set DEFAULT_OLLAMA_MODEL at minimum

ollama pull llama3.2
.venv\Scripts\python scripts\check_prerequisites.py
.venv\Scripts\pytest tests/ -q
```

See also [MODEL_SETUP.md](MODEL_SETUP.md) for Ollama and per-module model configuration.

## Configuration

Copy `.env.example` to `.env`. Key settings for deployment:

| Variable | Default | Notes |
|----------|---------|-------|
| `DEFAULT_OLLAMA_MODEL` | _(empty)_ | **Set this** before running workflows |
| `DATABASE_URL` | `sqlite:///./data/rre.db` | Persists transcripts, runs, synthesis |
| `API_HOST` | `127.0.0.1` | Keep on localhost for private use |
| `API_PORT` | `8000` | FastAPI port |
| `STREAMLIT_PORT` | `8501` | UI port |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama API |
| `WHISPER_MODEL` | `base` | Use `small` or `medium` for better accuracy |
| `MAX_UPLOAD_MB` | `100` | Audio upload limit |
| `EVIDENCE_PROMPT_MAX_QUOTES` | `120` | Long-transcript prompt summarization |

The `data/` directory (gitignored) stores:

- `data/rre.db` — SQLite database
- `data/temp/` — temporary audio uploads

Create it automatically on first run, or pre-create with `mkdir data`.

## Running (development)

```powershell
.\scripts\run_dev.ps1
```

- API: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- UI: [http://localhost:8501](http://localhost:8501)
- API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

The dev script starts uvicorn with `--reload`. Use only on a trusted machine.

## Running (private production)

For day-to-day private use, run services without auto-reload:

**Terminal 1 — API:**

```powershell
.venv\Scripts\uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

**Terminal 2 — UI:**

```powershell
.venv\Scripts\streamlit run ui/streamlit_app.py --server.address localhost --server.port 8501
```

Keep both terminals open. Bind to `127.0.0.1` / `localhost` only unless you understand the security implications of exposing the API on your network.

## User workflow (Streamlit)

1. **Ingest** — paste or upload a transcript (or transcribe audio)
2. **Prepare** — edit speaker names; review quote IDs
3. **Analyze** — run `quick_review` or `full_mvp` workflow
4. **Report** — review module findings, synthesis, evidence drill-down; export `.md` / `.json`

Legacy single-purpose analysis remains available via sidebar toggle. Prefer workflows for structured output.

## API quick reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/api/health` | ffmpeg, Ollama, Whisper status |
| `POST` | `/api/transcripts` | Ingest transcript |
| `GET` | `/api/workflows` | List workflows |
| `POST` | `/api/workflows/{id}/run` | Run analysis workflow |
| `GET` | `/api/workflow-runs/{id}` | Poll workflow status |
| `GET` | `/api/workflow-runs/{id}/synthesis` | Synthesis report |
| `POST` | `/api/transcribe` | Audio → transcript |
| `POST` | `/api/analyze` | **Deprecated** — use workflows |

## Pre-flight checklist

Before relying on this deployment for real transcripts:

- [ ] `scripts/check_prerequisites.py` passes
- [ ] `DEFAULT_OLLAMA_MODEL` set in `.env`
- [ ] `pytest tests/ -q` passes
- [ ] Sidebar shows Ollama + ffmpeg healthy
- [ ] Trial run on a short golden fixture (`tests/fixtures/transcripts/two_speaker_repair.txt`)
- [ ] Review safety disclaimer in report UI

## Backup and restore

**Backup:**

```powershell
copy data\rre.db data\rre.db.backup
```

**Restore:** stop API/UI, replace `data/rre.db`, restart.

No migration tooling is included in MVP — treat the database as disposable during upgrades unless you back up first.

## Upgrade procedure

```powershell
git fetch origin
git checkout v0.2.0   # or newer tag
pip install -e ".[dev]"
.venv\Scripts\pytest tests/ -q
# Restart API and UI
```

If schema changes occur in a future release, delete `data/rre.db` and re-ingest transcripts, or restore from backup after reviewing release notes.

## Security notes

- **No authentication** — intended for single-user local use only.
- **Do not expose** API/UI to the public internet without adding auth, TLS, and rate limiting.
- Transcripts may contain sensitive personal data; disk encryption and access control are your responsibility.
- LLM output is analytical, not clinical or legal advice; safety validation reduces but does not eliminate risk.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| "No Ollama model specified" | Missing model config | Set `DEFAULT_OLLAMA_MODEL` in `.env` |
| Ollama connection failed | Ollama not running | Start Ollama app or `ollama serve` |
| ffmpeg not found | Missing from PATH | Install ffmpeg, restart terminal |
| Workflow stuck / slow | Large model or long transcript | Use smaller model; check evidence limits |
| Empty analysis | Model too small for JSON output | Try `llama3.1:8b` or larger |
| SQLite locked | Multiple API instances | Run only one uvicorn process |

## Performance tips

- Use `quick_review` for faster iteration (3 modules, no meta-synthesis).
- Use `full_mvp` when you need integrated synthesis.
- Override `ollama_model` in `config/modules/meta_synthesis.yaml` for a stronger synthesis model.
- For very long transcripts, tune `EVIDENCE_PROMPT_*` settings (see [MODEL_SETUP.md](MODEL_SETUP.md)).

## Related docs

- [implementation_plan.md](implementation_plan.md) — MVP phases and architecture
- [MODEL_SETUP.md](MODEL_SETUP.md) — Ollama and model overrides
- [14_testing_evaluation_and_safety.md](14_testing_evaluation_and_safety.md) — safety design
- [README.md](../README.md) — quick start
