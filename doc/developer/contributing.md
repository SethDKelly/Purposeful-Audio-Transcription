# Contributing

## Workflow

1. Fork / branch from `main`
2. Make focused changes with tests
3. Install hooks once: `pip install -e ".[dev]" && pre-commit install`
4. Run `pre-commit run --all-files` (or rely on the git hook) and `pytest tests/ -q`
5. Open a PR with summary and test plan

### Pre-commit gates (Tier 1 + 2)

| Hook | What it catches |
|------|-----------------|
| YAML syntax (`scripts/validate_yaml.py`) | Broken YAML under `config/`, workflows, fixtures |
| Config registries (`scripts/validate_config.py`) | Missing prompts, unknown module IDs, meta-synthesis not last |
| Ruff lint/format | Python style and unused imports |
| actionlint | GitHub Actions workflow mistakes |
| terraform fmt (when `terraform` is installed) | Infra formatting drift |
| Targeted pytest | Registries, parser, Bedrock provider, P1-4 workflows |

Deploy CI also runs `validate_yaml` + `validate_config` before full pytest.

## Branch naming

```text
phase-m-feature-name
fix/short-description
docs/topic
```

## Commits

- Complete sentences; explain **why**
- One logical change per commit when possible
- Do not commit `.env`, `data/`, or personal notes

## Adding a module

1. **Prompt** — `config/prompts/NN Module Name.md` (follow existing structure)
2. **YAML** — `config/modules/module_id.yaml`:

```yaml
id: my_module
name: "My Module"
version: "1.0.0"
enabled: true
prompt_file: "NN Module Name.md"
output_schema: module_output_v1
input_type: transcript
# … see existing modules for full fields
```

3. **Tests** — extend `test_module_registry.py` if needed
4. **Workflow** — add module ID to a workflow YAML or document as API-only
5. **Docs** — update `config/prompts/README.md`

Output must validate against `module_output_v1`: findings with `evidence_quote_ids`, confidence, alternatives.

## Adding a workflow

Create `config/workflows/my_workflow.yaml`:

```yaml
id: my_workflow
name: "My Workflow"
description: "…"
estimated_runtime: "2-5 min"
output_tone: practical
modules:
  - relationship_conversation_analysis
  - nvc_analysis
meta_synthesis: false
```

Add integration test with mocked LLM in `tests/test_workflow_engine.py` or similar.

## API changes

- Add Pydantic schemas in `backend/api/schemas.py`
- Map domain errors to `AppError` subclasses
- Document in [api-reference.md](api-reference.md)

## Testing requirements

- New behavior needs tests (unit or API integration)
- Mock Ollama in tests unless explicitly testing live LLM
- Do not reduce coverage of safety validator or output parser

## Documentation

- User-facing changes → `doc/user/`
- Developer / API changes → `doc/developer/`
- Planning / phases → `doc/planning/`
- Update [../README.md](../README.md) index when adding major surfaces

## Code review checklist

- [ ] `pytest tests/ -q` passes
- [ ] No secrets in diff
- [ ] Evidence IDs preserved in new finding paths
- [ ] Safety validator considered for new LLM output types

## Related

- [development.md](development.md)
- [architecture.md](architecture.md)
- [../planning/implementing.md](../planning/implementing.md)
- [../planning/completed.md](../planning/completed.md)
