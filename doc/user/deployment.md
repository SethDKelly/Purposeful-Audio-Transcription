# Deployment guide — RRE v0.3.0

Private-use deployment for the **Relationship Reasoning Engine**. Runs locally with Whisper and Ollama; not a multi-tenant hosted service.

## Release summary

| Item | Value |
|------|-------|
| Tag | `v0.3.0` |
| Scope | MVP (A–G) + post-MVP (H–L) |
| Workflows | `quick_review`, `full_mvp`, `conflict_coaching`, `mediation_brief`, `clinical_exploration` |
| Modules | 13 analysis modules + meta-synthesis |
| Tests | `pytest tests/ -q` (96 tests) |

## System requirements

| Component | Requirement |
|-----------|-------------|
| OS | Windows 10/11 (primary); Linux/macOS supported |
| Python | 3.11+ |
| ffmpeg | On `PATH` |
| Ollama | Running locally with at least one chat model |
| RAM | 8 GB minimum; 16 GB+ for larger models |
| Disk | ~2 GB for Whisper + models; DB grows with usage |
| GPU | Optional (`WHISPER_DEVICE=cuda`) |

## First-time install

```powershell
git clone https://github.com/SethDKelly/Purposeful-Audio-Transcription.git
cd Purposeful-Audio-Transcription
git checkout v0.3.0

python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

copy .env.example .env
# Set DEFAULT_OLLAMA_MODEL

ollama pull llama3.2
.venv\Scripts\python scripts\check_prerequisites.py
.venv\Scripts\pytest tests/ -q
```

See [model-setup.md](model-setup.md) for Ollama configuration.

## Configuration

| Variable | Default | Notes |
|----------|---------|-------|
| `DEFAULT_OLLAMA_MODEL` | _(empty)_ | **Required** for workflows |
| `DATABASE_URL` | `sqlite:///./data/rre.db` | SQLite default |
| `DATABASE_POOL_SIZE` | `5` | PostgreSQL pool |
| `ALEMBIC_AUTO_UPGRADE` | `false` | `true` for PostgreSQL migrations on startup |
| `API_KEY` | _(empty)_ | Require `X-API-Key` on protected routes |
| `LOG_JSON` | `false` | Structured JSON logs |
| `WORKFLOW_BACKGROUND_DEFAULT` | `false` | Background workflow queue |
| `API_HOST` / `API_PORT` | `127.0.0.1` / `8000` | Keep on localhost |
| `STREAMLIT_PORT` | `8501` | UI port |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama API |
| `WHISPER_MODEL` | `base` | Transcription quality |
| `DIARIZATION_ENABLED` | `true` | Speaker diarization for audio uploads |
| `HF_TOKEN` | _(empty)_ | Hugging Face token for pyannote models |
| `MAX_UPLOAD_MB` | `100` | Audio upload limit |
| `EVIDENCE_PROMPT_MAX_QUOTES` | `120` | Long-transcript summarization |

### PostgreSQL (optional)

```env
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/rre
ALEMBIC_AUTO_UPGRADE=true
```

Or run `alembic upgrade head` before starting the API.

### Data directory

`data/` (gitignored):

- `data/rre.db` — SQLite database
- `data/temp/` — temporary uploads

## Running

**Development (auto-reload):**

```powershell
.\scripts\run_dev.ps1
```

**Private production (no reload):**

```powershell
# Terminal 1
.venv\Scripts\uvicorn backend.main:app --host 127.0.0.1 --port 8000

# Terminal 2
.venv\Scripts\streamlit run ui/streamlit_app.py --server.address localhost --server.port 8501
```

| Service | URL |
|---------|-----|
| UI | http://localhost:8501 |
| API | http://127.0.0.1:8000 |
| Docs | http://127.0.0.1:8000/docs |

## API quick reference

See [developer/api-reference.md](../developer/api-reference.md) for the full list.

## Pre-flight checklist

- [ ] `scripts/check_prerequisites.py` passes
- [ ] `DEFAULT_OLLAMA_MODEL` set
- [ ] `pytest tests/ -q` passes
- [ ] Sidebar shows Ollama + ffmpeg healthy
- [ ] Trial run on a short fixture
- [ ] Safety disclaimer reviewed

## Backup and restore

```powershell
copy data\rre.db data\rre.db.backup
```

Stop services, replace the DB file, restart. For PostgreSQL, use your standard backup tools.

## Upgrade

```powershell
git fetch origin
git checkout v0.3.0
pip install -e ".[dev]"
.venv\Scripts\pytest tests/ -q
```

Review [releases/v0.3.0.md](../releases/v0.3.0.md). SQLite: backup first; Alembic handles schema when enabled.

## Security

- **API key** — set `API_KEY` to require `X-API-Key` (health and docs stay public).
- **Default open** — empty `API_KEY` is fine for single-user local use only.
- **Do not expose** to the public internet without TLS, auth, and rate limiting.
- Transcripts may contain sensitive data; encrypt disk and control access.
- LLM output is not clinical or legal advice.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| No Ollama model specified | Set `DEFAULT_OLLAMA_MODEL` |
| Ollama connection failed | Start Ollama / `ollama serve` |
| ffmpeg not found | Install ffmpeg, restart terminal |
| Workflow slow | Smaller model; use `quick_review`; `background: true` via API |
| Empty / invalid JSON | Try `llama3.1:8b` or larger |
| SQLite locked | Single uvicorn instance only |
| 401 on API | Set `X-API-Key` header when `API_KEY` configured |

## Performance

- `quick_review` — fastest iteration (3 modules).
- `clinical_exploration` — longest; consider background API runs.
- Override `ollama_model` in `config/modules/meta_synthesis.yaml` for stronger synthesis.
- Tune `EVIDENCE_PROMPT_*` for very long transcripts.

## Related

- [getting-started.md](getting-started.md)
- [user-guide.md](user-guide.md)
- [model-setup.md](model-setup.md)
- [../planning/implementation_plan.md](../planning/implementation_plan.md)
