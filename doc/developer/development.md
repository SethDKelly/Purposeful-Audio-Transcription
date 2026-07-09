# Development guide

## Prerequisites

Same as [../user/getting-started.md](../user/getting-started.md): Python 3.11+, ffmpeg, Ollama.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
copy .env.example .env
```

Set `DEFAULT_OLLAMA_MODEL` in `.env` for integration tests that call Ollama (most tests mock the LLM).

## Run locally

```powershell
.\scripts\run_dev.ps1
```

Or separately:

```powershell
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
streamlit run ui/streamlit_app.py
```

## Project layout

```text
backend/
  api/routes/       # FastAPI routers
  core/             # Registries, exceptions, middleware
  domain/           # Pydantic domain models
  db/               # SQLAlchemy, Alembic helpers
  repositories/     # Persistence
  services/         # Business logic
  schemas/          # JSON output schemas (module_output_v1, …)
config/
  modules/          # Module YAML
  workflows/        # Workflow YAML
  prompts/          # Markdown prompts
  framework/        # Shared compiler fragments
ui/
  streamlit_app.py
  api_client.py
  components/
tests/
  fixtures/         # Golden transcripts, sample JSON
alembic/            # DB migrations
scripts/            # Dev and release scripts
doc/
  user/             # User guides
  developer/        # This section
  design/           # Design package 01–16
  planning/         # Implementation plans
```

## Tests

```powershell
pytest tests/ -q
pytest tests/test_workflow_engine.py -v
```

`tests/conftest.py` uses an isolated SQLite DB per test with `ALEMBIC_AUTO_UPGRADE=false`.

### Test patterns

- **Unit** — parsers, validators, exploration logic
- **Integration** — API via `TestClient` with mocked `ollama`
- **Fixtures** — `tests/fixtures/golden_transcript.txt`, `sample_module_output.json`

## Database

**SQLite (default):** `create_all` on test startup.

**Migrations:**

```powershell
alembic upgrade head
```

Set `ALEMBIC_AUTO_UPGRADE=true` in `.env` for PostgreSQL auto-migrate on API start.

## Debugging

| Issue | Check |
|-------|-------|
| Module validation fails | `module_run.validation_errors` in API response |
| Workflow stuck | `GET /api/workflow-runs/{id}` status; logs with `LOG_JSON=true` |
| Prompt too long | `EVIDENCE_PROMPT_*` settings |

API interactive docs: http://127.0.0.1:8000/docs

## Code conventions

- Python 3.11+ type hints
- Pydantic v2 for API and domain models
- Services as classes with module-level singletons (`workflow_engine = WorkflowEngine()`)
- Exceptions in `backend/core/exceptions.py` map to HTTP status via `AppError`
- Keep changes focused; match surrounding style

## Related

- [architecture.md](architecture.md)
- [contributing.md](contributing.md)
- [api-reference.md](api-reference.md)
