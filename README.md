# Purposeful Audio Transcription

**Relationship Reasoning Engine (RRE)** — evidence-linked, multi-module transcript analysis.

| | |
|--|--|
| **Canonical release** | [v0.5.1](https://github.com/SethDKelly/Purposeful-Audio-Transcription/releases/tag/v0.5.1) — AWS cloud cutover |
| **Baseline (local MVP)** | [v0.3.0](https://github.com/SethDKelly/Purposeful-Audio-Transcription/releases/tag/v0.3.0) |
| **Active work** | Tier 2 (trust + full workflows) — [doc/planning/implementing.md](doc/planning/implementing.md) |

## Quick start (local)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev,local]"
copy .env.example .env
# Set DEFAULT_OLLAMA_MODEL in .env; HF_TOKEN optional for pyannote
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
| **Release** | [doc/releases/v0.5.1.md](doc/releases/v0.5.1.md) |
| **Index** | [doc/README.md](doc/README.md) |

## Capabilities

- 13 analysis modules · 5 workflows · meta-synthesis  
- Evidence quote IDs (`Q001…`) on findings  
- **Local:** Whisper + optional pyannote; Ollama  
- **AWS:** Bedrock + Amazon Transcribe; Stage B VPC (no public task IPs)  
- Streamlit report + Explore tab  
- Exports: Markdown, JSON, PDF, coach summary, mediation brief  
- Optional PostgreSQL, background jobs, API key auth  

## Prerequisites (local)

- Python 3.11+  
- [ffmpeg](https://ffmpeg.org/download.html) on PATH  
- [Ollama](https://ollama.com/) with at least one chat model  
- Optional: Hugging Face token for pyannote — [model-setup.md](doc/user/model-setup.md)

## AWS (operators)

See [aws-operations.md](doc/developer/aws-operations.md). Deploy: push runtime paths to `main` or **workflow_dispatch**. Pause when idle: **Pause AWS dev**.

## License

See repository license file.
