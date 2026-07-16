# Purposeful Audio Transcription

**Relationship Reasoning Engine (RRE)** — evidence-linked, multi-module transcript analysis on **AWS** (Bedrock + Amazon Transcribe + ECS + RDS).

| | |
|--|--|
| **Canonical release** | [v0.9.0](https://github.com/SethDKelly/Purposeful-Audio-Transcription/releases/tag/v0.9.0) |
| **Runtime** | AWS only (account `521018312783`, `us-east-2`) |
| **Active work** | [docs/planning/implementing.md](docs/planning/implementing.md) · [docs/planning/roadmap_v0.7_to_v1.0.md](docs/planning/roadmap_v0.7_to_v1.0.md) |

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

## Capabilities (v0.9.0)

- 14 analysis modules · 7 workflows · meta-synthesis over **structured inventory**
- **Cases** — group transcripts by case; session labels/dates; longitudinal compare + synthesis
- Normalized persistence: findings, constructs, relationships (Alembic `005`–`007`)
- Graph merge + deterministic convergence scores on canonical constructs
- Table-first structured inventory explorer + knowledge graph
- Finding feedback (helpful / unhelpful / unsure) on report cards
- Report package ZIP (manifest + report + evidence appendix + findings index)
- Transcript preparation workspace (edit turns, exclude, Ready to Analyze)
- Ontology vocabulary v1 (`config/ontology/`) + `expected_constructs` soft coverage warnings
- Evidence quote IDs (`Q001…`) on findings; golden transcript fixtures (GT001/GT002)
- Per-module / workflow telemetry (latency, tokens, estimated cost)
- **LLM:** Amazon Bedrock · **ASR:** Amazon Transcribe (speaker labels)
- Stage B VPC (no public task IPs); shared API key auth; optional HTTPS via ACM
- Streamlit report + Explore tab + Cases expander
- Exports: Markdown, JSON, PDF, coach summary, mediation brief, report package ZIP
- RDS PostgreSQL, background jobs

## Deploy policy

Deploy on **minor-version releases** (git tag `v*.*.*` or manual **Deploy to AWS dev**). Ordinary commits to `main` do not wake AWS. Pause when idle.

## License

See repository license file.
