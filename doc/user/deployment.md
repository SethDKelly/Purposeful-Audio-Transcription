# Deployment guide — local private use

Private-use deployment for the **Relationship Reasoning Engine** on a single machine (Whisper + Ollama). This is **not** the AWS cloud guide.

| Deploy target | Document |
|---------------|----------|
| **This page** | Local Windows/Linux private use |
| **AWS dev** | [../planning/aws-deployment.md](../planning/aws-deployment.md) · [../developer/aws-operations.md](../developer/aws-operations.md) · [../../infra/dev/README.md](../../infra/dev/README.md) |

## Baseline

| Item | Value |
|------|-------|
| App baseline | v0.3.0+ on `main` / active branch |
| Workflows | `quick_review`, `full_mvp`, `conflict_coaching`, `mediation_brief`, `clinical_exploration`, `research_oriented`, `full_multidisciplinary` |
| Modules | 13 analysis modules + meta-synthesis |
| Tests | `pytest tests/ -q` |

## System requirements

| Component | Requirement |
|-----------|-------------|
| OS | Windows 10/11 (primary); Linux/macOS supported |
| Python | 3.11+ |
| ffmpeg | On `PATH` |
| Ollama | Running locally with at least one chat model |
| RAM | 8 GB minimum; 16 GB+ for larger models |
| Disk | ~2 GB for Whisper + models; DB grows with usage |
| GPU | Optional NVIDIA CUDA (`WHISPER_DEVICE` / `DIARIZATION_DEVICE=auto`) |

## First-time install

```powershell
git clone https://github.com/SethDKelly/Purposeful-Audio-Transcription.git
cd Purposeful-Audio-Transcription

python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

copy .env.example .env
# Set DEFAULT_OLLAMA_MODEL

ollama pull llama3.2
.venv\Scripts\python scripts\check_prerequisites.py
.venv\Scripts\pytest tests/ -q
```

See [model-setup.md](model-setup.md) for Ollama configuration. Day-one walkthrough: [getting-started.md](getting-started.md).

## Configuration

| Variable | Default | Notes |
|----------|---------|-------|
| `DEFAULT_OLLAMA_MODEL` | _(empty)_ | **Required** for local workflows |
| `LLM_PROVIDER` | `ollama` | Use `bedrock` only on AWS |
| `DATABASE_URL` | `sqlite:///./data/rre.db` | Or PostgreSQL |
| `DATABASE_POOL_SIZE` | `5` | PostgreSQL pool |
| `ALEMBIC_AUTO_UPGRADE` | `false` | `true` for migrations on startup |
| `API_KEY` | _(empty)_ | Require `X-API-Key` when set |
| `LOG_JSON` | `false` | Structured JSON logs |
| `LOG_REDACT` | _(auto)_ | Redact transcript/prompt bodies from logs; auto-on for Bedrock / non-SQLite |
| `TRANSCRIPT_RETENTION_DAYS` | _(unset)_ | When set, purge transcripts older than N days on API startup |
| `WORKFLOW_BACKGROUND_DEFAULT` | `false` | Background workflow queue |
| `WORKFLOW_SYNC_MODULE_LIMIT` | `6` | Longer suites auto-run in background; explicit `background=false` over the limit returns 400 |
| `API_HOST` / `API_PORT` | `127.0.0.1` / `8000` | Keep on localhost for private use |
| `STREAMLIT_PORT` | `8501` | UI port |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama API |
| `WHISPER_MODEL` | `base` | Transcription quality |
| `DIARIZATION_ENABLED` | `true` | Speaker diarization for audio |
| `HF_TOKEN` | _(empty)_ | Required for pyannote model download |
| `MAX_UPLOAD_MB` | `100` | Audio upload limit |

### PostgreSQL (optional)

```env
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/rre
ALEMBIC_AUTO_UPGRADE=true
```

### Data directory

`data/` (gitignored): `rre.db` (SQLite), `temp/` (uploads).

## Running

**Development:**

```powershell
.\scripts\run_dev.ps1
```

**Private production (no reload):**

```powershell
.venv\Scripts\uvicorn backend.main:app --host 127.0.0.1 --port 8000
.venv\Scripts\streamlit run ui/streamlit_app.py --server.address localhost --server.port 8501
```

| Service | URL |
|---------|-----|
| UI | http://localhost:8501 |
| API docs | http://127.0.0.1:8000/docs |

## Pre-flight checklist

- [ ] `scripts/check_prerequisites.py` passes  
- [ ] `DEFAULT_OLLAMA_MODEL` set  
- [ ] `pytest tests/ -q` passes  
- [ ] Sidebar shows Ollama + ffmpeg healthy  
- [ ] Trial run on a short fixture  

## Backup, upgrade, security

- **Backup:** copy `data\rre.db` (or use PostgreSQL tools).  
- **Upgrade:** `git pull` / checkout release tag → `pip install -e ".[dev]"` → run tests. See [releases/](../releases/).  
- **Security:** prefer `API_KEY` for anything beyond solo local use; do not expose without TLS; transcripts may be sensitive; LLM output is not clinical/legal advice.  
- **GPU / offline:** see [model-setup.md](model-setup.md) and [../planning/backlog.md](../planning/backlog.md).

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| No Ollama model | Set `DEFAULT_OLLAMA_MODEL` |
| Ollama connection failed | Start Ollama |
| ffmpeg not found | Install ffmpeg, restart shell |
| Workflow slow | Smaller model; `quick_review`; background API |
| Empty / invalid JSON | Larger chat model; check `OLLAMA_THINK` |
| SQLite locked | Single uvicorn instance |
| 401 on API | Send `X-API-Key` when `API_KEY` is set |

## Related

- [user-guide.md](user-guide.md) · [model-setup.md](model-setup.md)  
- [../planning/implementing.md](../planning/implementing.md) · [../planning/completed.md](../planning/completed.md)  
- API: [../developer/api-reference.md](../developer/api-reference.md)
