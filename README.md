# Purposeful Audio Transcription

**Relationship Reasoning Engine (RRE)** — evidence-linked, multi-module transcript analysis. Runs **locally** (Whisper + Ollama) and on **AWS dev** (Bedrock; Transcribe planned).

| | |
|--|--|
| **Baseline release** | [v0.3.0](https://github.com/SethDKelly/Purposeful-Audio-Transcription/releases/tag/v0.3.0) |
| **In progress** | v0.5.0 AWS pivot — [doc/planning/implementing.md](doc/planning/implementing.md) |

## Quick start (local)

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

Full local setup: [doc/user/getting-started.md](doc/user/getting-started.md)

## Documentation

| Audience | Guide |
|----------|-------|
| **Users** | [doc/user/](doc/user/) — getting started, guide, local deployment, models |
| **Developers** | [doc/developer/](doc/developer/) — architecture, API, contributing, AWS ops |
| **Planning** | [doc/planning/](doc/planning/) — completed / implementing / backlog |
| **Index** | [doc/README.md](doc/README.md) |

## Capabilities

- 13 analysis modules · 5 workflows · meta-synthesis  
- Evidence quote IDs (`Q001…`) on findings  
- Speaker diarization for multi-speaker audio (local pyannote)  
- Streamlit report + Explore tab  
- Exports: Markdown, JSON, PDF, coach summary, mediation brief  
- Optional PostgreSQL, background jobs, API key auth  
- AWS: ECS Fargate, Bedrock LLM, CloudWatch (see planning docs)

## Prerequisites (local)

- Python 3.11+  
- [ffmpeg](https://ffmpeg.org/download.html) on PATH  
- [Ollama](https://ollama.com/) with at least one chat model  

## Configuration

See `.env.example`. Common settings:

| Variable | Purpose |
|----------|---------|
| `DEFAULT_OLLAMA_MODEL` | Default LLM for local workflows |
| `LLM_PROVIDER` | `ollama` (local) or `bedrock` (AWS) |
| `BEDROCK_MODEL_ID` | Bedrock inference profile (AWS) |
| `WHISPER_MODEL` | Whisper size (`base`, `tiny`, …) |
| `DATABASE_URL` | SQLite (default) or PostgreSQL |
| `API_KEY` | Optional API authentication |

Details: [doc/user/model-setup.md](doc/user/model-setup.md) · [doc/user/deployment.md](doc/user/deployment.md)

## Project structure

```text
backend/          FastAPI application
config/           Modules, workflows, prompts
ui/               Streamlit UI
infra/dev/        AWS Terraform (dev)
tests/
doc/
  user/           Local user docs
  developer/      Dev + AWS ops
  design/         Product design (01–16)
  planning/       Active plan + AWS architecture
  releases/
```

## Roadmap

| Doc | Role |
|-----|------|
| [implementing.md](doc/planning/implementing.md) | Active tiers (VPC endpoints, Transcribe, …) |
| [completed.md](doc/planning/completed.md) | What already shipped |
| [aws-deployment.md](doc/planning/aws-deployment.md) | AWS architecture |
| [backlog.md](doc/planning/backlog.md) | Deferred / nice-to-have |
| [aws-backbone](https://github.com/SethDKelly/aws-backbone) | Account IAM/OIDC |

## Prompt storage

Prompts live in `config/prompts/` and link from `config/modules/*.yaml`. See [config/prompts/README.md](config/prompts/README.md).
