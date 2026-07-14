# Purposeful Audio Transcription

**Relationship Reasoning Engine (RRE)** — evidence-linked, multi-module transcript analysis on **AWS** (Bedrock + Amazon Transcribe + ECS + RDS).

| | |
|--|--|
| **Canonical release** | [v0.5.1](https://github.com/SethDKelly/Purposeful-Audio-Transcription/releases/tag/v0.5.1) |
| **Runtime** | AWS only (account `521018312783`, `us-east-2`) |
| **Active work** | [doc/planning/implementing.md](doc/planning/implementing.md) |

## Quick start (operators)

1. Deploy the stack: GitHub Actions **Deploy to AWS dev** (`workflow_dispatch` or push under runtime paths to `main`).
2. Open the ALB UI URL from the workflow summary / Terraform outputs.
3. Paste a transcript or upload audio → run **Quick Review** (Bedrock).
4. When idle: **Pause AWS dev** to avoid cost.

Full walkthrough: [doc/user/getting-started.md](doc/user/getting-started.md) · Ops: [doc/developer/aws-operations.md](doc/developer/aws-operations.md)

## Developer loop

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pre-commit install
pytest tests/ -q
```

Tests use SQLite. There is **no** supported local Whisper/Ollama server — integrate and validate on AWS after green pytest. Pre-commit runs YAML/config checks, ruff, actionlint, and a targeted pytest slice. See [doc/developer/development.md](doc/developer/development.md).

## Documentation

| Audience | Guide |
|----------|-------|
| **Operators / users** | [doc/user/](doc/user/) — getting started, guide, AWS deployment, models |
| **Developers** | [doc/developer/](doc/developer/) — architecture, API, contributing, AWS ops |
| **Architecture** | [doc/planning/aws-deployment.md](doc/planning/aws-deployment.md) |
| **Planning** | [doc/planning/](doc/planning/) — completed / implementing / backlog |
| **Index** | [doc/README.md](doc/README.md) |

## Capabilities

- 13 analysis modules · 7 workflows · meta-synthesis
- Evidence quote IDs (`Q001…`) on findings
- **LLM:** Amazon Bedrock · **ASR:** Amazon Transcribe (speaker labels)
- Stage B VPC (no public task IPs); data stays in-account
- Streamlit report + Explore tab
- Exports: Markdown, JSON, PDF, coach summary, mediation brief
- RDS PostgreSQL, background jobs, optional API key auth

## License

See repository license file.
