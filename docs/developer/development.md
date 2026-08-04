# Development guide

RRE is an **AWS-only** product. Develop on a laptop; run the application on ECS.

## Prerequisites

- Python 3.11+
- Node.js 22+ (for `frontend-react/` tooling)
- GitHub access to deploy workflows
- AWS operator access for integration checks (optional for most PRs)

## Setup (tests / tooling)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pre-commit install
copy .env.example .env   # tooling / pytest only — not a local server
```

There is no supported local API/UI against Bedrock, Transcribe, Whisper, or Ollama. Validate product behavior after **Deploy to AWS dev**.

Quick config gates (also in pre-commit / Deploy CI):

```powershell
python scripts/validate_yaml.py
python scripts/validate_config.py
pre-commit run --all-files
```

## Project layout

```text
backend/
  api/routes/       # FastAPI routers
  core/             # Registries, ontology, middleware
  domain/           # Pydantic domain models
  db/               # SQLAlchemy, Alembic helpers
  repositories/     # Persistence
  services/         # Business logic (Bedrock, Transcribe, workflows)
  schemas/          # JSON output schemas
config/
  modules/          # Module YAML (+ expected_constructs)
  ontology/         # Construct/relationship vocabulary
  workflows/        # Workflow YAML
  prompts/          # Markdown prompts
  framework/        # Shared compiler fragments
frontend-react/     # React product UI (Vite + react-router-dom)
ui/                 # Streamlit admin/eval UI (ECS UI image)
infra/dev/          # Terraform for AWS
docs/               # Product and developer documentation
tests/
  fixtures/
    golden_transcripts/
Dockerfile.cloud    # API image
Dockerfile.ui       # Streamlit UI image
frontend-react/Dockerfile  # React nginx image (rre-dev-web)
```

## React frontend

Primary product UI. Quick start and route map: [../../frontend-react/README.md](../../frontend-react/README.md).

```bash
cd frontend-react
cp .env.example .env
npm ci
npm run test
npm run lint
```

Leave `VITE_API_BASE_URL` empty for the Vite `/api` proxy. Boundary rules: [ui-api-boundary.md](ui-api-boundary.md).

## Tests

Prefer **`python -m pytest`** so the active interpreter’s environment is used (works without putting `.venv/Scripts` on `PATH`):

```powershell
.venv\Scripts\Activate.ps1   # optional but recommended
python -m pytest tests/ -q
# Golden fixtures (mocked):
python -m pytest -m "golden and not live_model" -q
```

After `pip install -e ".[dev]"` and with the venv activated, bare `pytest tests/ -q` also works.

CI and pre-commit use `python -m pytest` / `python scripts/run_venv.py -m pytest`.

`tests/conftest.py` forces an isolated **SQLite** DB per session (`ALEMBIC_AUTO_UPGRADE=false`). Most LLM/ASR calls are mocked.

### Test patterns

- **Unit** — parsers, validators, ontology, exploration logic
- **Integration** — API via `TestClient` with mocked Bedrock / Transcribe
- **Golden** — `tests/fixtures/golden_transcripts/` signal-based regression
- **Fixtures** — `tests/fixtures/golden_transcript.txt`, `sample_module_output.json`
- **React** — Vitest + Testing Library in `frontend-react/` (wrap router hooks with `MemoryRouter`); Playwright smoke via `npm run test:e2e`

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
- [ui-api-boundary.md](ui-api-boundary.md)
- [../../frontend-react/README.md](../../frontend-react/README.md)
- [aws-deployment.md](aws-deployment.md)
