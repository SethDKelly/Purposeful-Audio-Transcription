# Purposeful Audio Transcription

**Relationship Reasoning Engine (RRE)** — evidence-linked, multi-module transcript analysis on **AWS** (Bedrock + Amazon Transcribe + ECS + RDS).

| | |
|--|--|
| **Canonical release** | [v1.0.0](https://github.com/SethDKelly/Purposeful-Audio-Transcription/releases/tag/v1.0.0) |
| **Runtime** | AWS only (account `521018312783`, `us-east-2`) |
| **Active work** | [docs/planning/implementing.md](docs/planning/implementing.md) · [docs/planning/future_considerations.md](docs/planning/future_considerations.md) |

## Quick start (operators)

1. Deploy the stack: GitHub Actions **Deploy to AWS dev** (`workflow_dispatch`, or push of a `v*.*.*` tag).
2. Open the ALB UI URL from the workflow summary / Terraform outputs.
3. Paste a transcript or upload audio → **Prepare** (review/edit turns) → **Ready to Analyze** → run **Quick Review** (Bedrock).
4. When idle: **Pause AWS dev** to avoid cost.

Full walkthrough: [docs/user/getting-started.md](docs/user/getting-started.md) · Ops: [docs/developer/aws-operations.md](docs/developer/aws-operations.md)

## Developer loop

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pre-commit install
pytest tests/ -q
```

Tests use SQLite. There is **no** supported local Whisper/Ollama server — integrate and validate on AWS after green pytest. Pre-commit runs YAML/config checks, ruff, actionlint, and a targeted pytest slice. See [docs/developer/development.md](docs/developer/development.md).

## Documentation

| Audience | Guide |
|----------|-------|
| **Operators / users** | [docs/user/](docs/user/) — getting started, guide, AWS deployment, models |
| **Developers** | [docs/developer/](docs/developer/) — architecture, API, contributing, AWS ops |
| **Architecture** | [docs/planning/aws-deployment.md](docs/planning/aws-deployment.md) |
| **Planning** | [docs/planning/](docs/planning/) — completed / implementing / backlog |
| **Index** | [docs/README.md](docs/README.md) |

## Capabilities (v1.0.0)

- 14 analysis modules · 7 workflows · DAG `steps` (e.g. `full_mvp`) · custom suites
- Dedicated ECS workflow worker — cancel, job timeout, retries
- **Cases** — group transcripts; longitudinal compare + synthesis
- Normalized persistence: findings, constructs, relationships
- Graph merge + deterministic convergence scores
- Table-first structured inventory + knowledge graph
- Safety-aware report mode (risk scan, banner, framing, exploratory skip)
- Long-transcript balanced quote sampling (explicit strategy, not silent truncation)
- Finding feedback + report package ZIP
- Transcript preparation workspace (edit turns, exclude, Ready to Analyze)
- Ontology vocabulary v1 + `expected_constructs` soft coverage warnings
- Evidence quote IDs (`Q001…`); golden transcript fixtures
- Per-module / workflow telemetry
- **LLM:** Amazon Bedrock · **ASR:** Amazon Transcribe
- Stage B VPC; shared API key auth; optional HTTPS via ACM
- Streamlit report + Explore + Cases + custom workflow builder
- RDS PostgreSQL, background jobs / worker queue


## Deploy policy

Deploy on **minor-version releases** (git tag `v*.*.*` or manual **Deploy to AWS dev**). Ordinary commits to `main` do not wake AWS. Pause when idle.

## License

See repository license file.
