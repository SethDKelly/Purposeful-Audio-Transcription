# Getting started

Quick path from clone to your first workflow report.

## What you need

| Requirement | Notes |
|-------------|-------|
| Python 3.11+ | `python --version` |
| [ffmpeg](https://ffmpeg.org/download.html) | On `PATH` for audio |
| [Ollama](https://ollama.com/) | Running locally |
| Chat model | e.g. `ollama pull llama3.2` |
| Speaker diarization | Optional: `pip install -e ".[local]"` + `HF_TOKEN` — see [model-setup.md](model-setup.md) |

## Install

```powershell
git clone https://github.com/SethDKelly/Purposeful-Audio-Transcription.git
cd Purposeful-Audio-Transcription
git checkout v0.5.1   # or use main

python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev,local]"

copy .env.example .env
```

Edit `.env` and set at minimum:

```env
DEFAULT_OLLAMA_MODEL=llama3.2
```

## Verify

```powershell
.venv\Scripts\python scripts\check_prerequisites.py
.venv\Scripts\pytest tests/ -q
```

## Run

```powershell
.\scripts\run_dev.ps1
```

| Service | URL |
|---------|-----|
| Streamlit UI | http://localhost:8501 |
| API | http://127.0.0.1:8000 |
| API docs | http://127.0.0.1:8000/docs |

## First workflow (5 minutes)

1. Open the UI and confirm the sidebar shows **Ollama**, **ffmpeg**, and optionally **Diarization** as connected.
2. **Ingest** — paste a short two-speaker transcript or upload `tests/fixtures/golden_transcript.txt`.
3. **Prepare** — optionally rename speakers; click through to keep quote IDs.
4. **Analyze** — choose **Quick Review** and your Ollama model; click **Run workflow**.
5. **Report** — review findings, open the **Explore** tab, export `.md` or `.pdf`.

## Choose a workflow

| Workflow | Best for | Runtime |
|----------|----------|---------|
| `quick_review` | Fast practical insight | ~1–3 min |
| `full_mvp` | Full analysis + synthesis | ~3–8 min |
| `conflict_coaching` | Needs, coaching tone | ~2–4 min |
| `mediation_brief` | Positions, interests, agreements | ~3–6 min |
| `clinical_exploration` | Deeper exploratory lenses | ~8–15 min |

See [user-guide.md](user-guide.md) for details.

## Next steps

- [User guide](user-guide.md) — exploration, exports, safety notes
- [Model setup](model-setup.md) — stronger models for synthesis
- [Deployment](deployment.md) — backup, API key, PostgreSQL
