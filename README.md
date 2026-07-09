# Purposeful Audio Transcription

A local-first **Relationship Reasoning Engine (RRE)** that transcribes audio with **Whisper** and analyzes transcripts with **Ollama** — evidence-linked, multi-module workflows, and interactive exploration.

**Release:** [v0.3.0](https://github.com/SethDKelly/Purposeful-Audio-Transcription/releases/tag/v0.3.0)

## Quick start

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
copy .env.example .env
# Set DEFAULT_OLLAMA_MODEL in .env
.\scripts\run_dev.ps1
```

- **UI:** http://localhost:8501  
- **API:** http://127.0.0.1:8000/docs  

Full instructions: **[doc/user/getting-started.md](doc/user/getting-started.md)**

## Documentation

| Audience | Guide |
|----------|-------|
| **Users** | [doc/user/](doc/user/) — getting started, user guide, deployment, models |
| **Developers** | [doc/developer/](doc/developer/) — architecture, API, contributing |
| **Index** | [doc/README.md](doc/README.md) — full documentation map |

## Features (v0.3.0)

- 13 analysis modules · 5 workflows · meta-synthesis
- Evidence quote IDs (`Q001…`) on every finding
- Live transcription progress (elapsed time, audio %, segments)
- Streamlit report + **Explore** tab (drill-down, follow-up Q&A)
- Exports: Markdown, JSON, PDF, coach summary, mediation brief
- Optional PostgreSQL, background jobs, API key auth
- 99 automated tests

## Prerequisites

- Python 3.11+
- [ffmpeg](https://ffmpeg.org/download.html) on PATH
- [Ollama](https://ollama.com/) with at least one chat model

## Configuration

See `.env.example`. Key settings:

| Variable | Purpose |
|----------|---------|
| `DEFAULT_OLLAMA_MODEL` | Default LLM for workflows |
| `WHISPER_MODEL` | Whisper model size (`base`, `tiny`, etc.) |
| `WHISPER_BEAM_SIZE` | Speed vs accuracy (default `1`) |
| `DATABASE_URL` | SQLite (default) or PostgreSQL |
| `API_KEY` | Optional API authentication |

Details: [doc/user/model-setup.md](doc/user/model-setup.md) · [doc/user/deployment.md](doc/user/deployment.md)

## Project structure

```text
backend/          FastAPI application
config/           Modules, workflows, prompts
ui/               Streamlit UI
tests/            Test suite
doc/
  user/           User documentation
  developer/      Developer documentation
  design/         Product & technical design (01–16)
  planning/       Implementation plans & roadmap
  releases/       Release notes
```

## API

Summary in [doc/developer/api-reference.md](doc/developer/api-reference.md). Interactive docs at `/docs` when the API is running.

## Roadmap

- **History:** [doc/planning/implementation_plan.md](doc/planning/implementation_plan.md) (phases A–L)
- **Next:** [doc/planning/18_post_v0.3_plan.md](doc/planning/18_post_v0.3_plan.md) (phases M–R)

## Prompt storage

Analysis prompts live in `config/prompts/` and link from `config/modules/*.yaml`. See [config/prompts/README.md](config/prompts/README.md).
