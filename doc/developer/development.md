# Development guide

RRE is an **AWS-only** product. Develop on a laptop; run the application on ECS.

## Prerequisites

- Python 3.11+
- GitHub access to deploy workflows
- AWS operator access for integration checks (optional for most PRs)

## Setup (tests / tooling)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
copy .env.example .env   # tooling / pytest only — not a local server
```

There is no supported local API/UI against Bedrock, Transcribe, Whisper, or Ollama. Validate product behavior after **Deploy to AWS dev**.

## Project layout

```text
backend/
  api/routes/       # FastAPI routers
  core/             # Registries, exceptions, middleware
  domain/           # Pydantic domain models
  db/               # SQLAlchemy, Alembic helpers
  repositories/     # Persistence
  services/         # Business logic (Bedrock, Transcribe, workflows)
  schemas/          # JSON output schemas
config/
  modules/          # Module YAML
  workflows/        # Workflow YAML
  prompts/          # Markdown prompts
  framework/        # Shared compiler fragments
ui/                 # Streamlit (ECS UI image)
infra/dev/          # Terraform for AWS that
tests/
  fixtures/
Dockerfile.cloud    # API image
Dockerfile.ui       # UI image
```

## Tests

```powershell
pytest tests/ -q
```

`tests/conftest.py` forces an isolated **SQLite** DB per session (`ALEMBIC_AUTO_UPGRADE=false`). Most LLM/ASR calls are mocked.

### Test patterns

- **Unit** — parsers, validators, exploration logic
- **Integration** — API via `TestClient` with mocked Bedrock / Transcribe
- **Fixtures** — `tests/fixtures/golden_transcript.txt`, `sample_module_output.json`

## Database

| Context | Engine |
|---------|--------|
| pytest | SQLite (forced in conftest) |
| AWS | RDS PostgreSQL via Secrets Manager |

```powershell
alembic upgrade head
```

ECS uses `ALEMBIC_AUTO_UPGRADE=true` as configured in Terraform.

## Debugging on AWS

| Issue | Check |
|-------|-------|
| Module validation fails | `module_run.validation_errors`; CloudWatch `/rre/dev/api` |
| Workflow stuck | `GET /api/workflow-runs/{id}`; Insights by `module_run_id` |
| Prompt too long | `EVIDENCE_PROMPT_*` settings |

Ops: [aws-operations.md](aws-operations.md).

## Code conventions

- Python 3.11+ type hints
- Pydantic v2 for API and domain models
- Services as classes with module-level singletons
- Exceptions in `backend/core/exceptions.py` map to HTTP via `AppError`
- Keep changes focused; match surrounding style

## Related

- [architecture.md](architecture.md)
- [contributing.md](contributing.md)
- [api-reference.md](api-reference.md)
- [../planning/aws-deployment.md](../planning/aws-deployment.md)
