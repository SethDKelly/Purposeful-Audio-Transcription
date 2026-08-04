# Contributing

## Branching model

```text
feature / fix / docs branches
        ↓  PR
  pre-production     ← integration & pre-prod testing
        ↓  PR (when ready to release)
      main           ← production releases only
```

| Branch | Role |
|--------|------|
| **`main`** | Production. Deploy tags / production releases come from here. |
| **`pre-production`** | Integration line for testing before production. Basis: post-v1.0 backlog work through v2 foundation. |
| **Feature branches** | Cut from `pre-production`; merge back to `pre-production` via PR. Do not merge features straight to `main`. |

Promote `pre-production` → `main` only when intentionally shipping a production release (PR + review + tag as needed).

## Workflow

1. Branch from **`pre-production`** (not `main`, unless hotfixing production)
2. Make focused changes with tests
3. Install hooks once: `pip install -e ".[dev]" && pre-commit install`
4. Run `pre-commit run --all-files` (or rely on the git hook) and `python -m pytest tests/ -q`
5. Open a PR **into `pre-production`** with summary and test plan
6. After pre-prod validation, open a release PR **`pre-production` → `main`** when ready to deploy

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

Cut from `pre-production`:

```text
feature/short-description
fix/short-description
docs/topic
phase-m-feature-name
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
- Mock Bedrock in tests unless explicitly testing live LLM (`@pytest.mark.live_model`)
- Do not reduce coverage of safety validator or output parser

## Documentation

- User-facing changes → `docs/user/`
- Developer / API changes → `docs/developer/`
- Planning / phases → `docs/planning/`
- Update [../README.md](../README.md) index when adding major surfaces

## Product tenets (required for product changes)

New features and architecture changes must preserve the [core product tenets](../product/core_tenets.md):

| Tenet | Preserve |
|-------|----------|
| Evidence traceability | Claims cite stable quote IDs; concise spans |
| Confidence calibration | No overstated inferences |
| Multi-lens analysis | Module provenance; honest convergence/divergence |
| Non-diagnostic discipline | No clinical/abuse/personality determinations as fact |
| Longitudinal case tracking | Session/transcript-scoped evidence identity |
| Professional workflow fit | Reviewable outputs; version metadata |
| Safety-aware framing | Serious risk not mutualized; cautious language |
| Structured reasoning graph | Typed relationships with rationale/evidence where possible |

Use [pr_review_tenet_checklist.md](pr_review_tenet_checklist.md) on every product PR. GitHub PRs also load [`.github/pull_request_template.md`](../../.github/pull_request_template.md).

Do **not** specialize the core engine for one market (therapy, mediation, enterprise, coaching) — use templates/presets later.

## Code review checklist

- [ ] `pytest tests/ -q` passes
- [ ] No secrets in diff
- [ ] Evidence IDs preserved in new finding paths
- [ ] Safety validator considered for new LLM output types
- [ ] Tenet checklist reviewed for product-facing changes

## Related

- [development.md](development.md)
- [architecture.md](architecture.md)
- [pr_review_tenet_checklist.md](pr_review_tenet_checklist.md)
- [../product/core_tenets.md](../product/core_tenets.md)
- [../planning/phases/001_v2_1_phase_sequence_overview.md](../planning/phases/001_v2_1_phase_sequence_overview.md)
- [../planning/deferred_backlog.md](../planning/deferred_backlog.md)
- [../archived/planning/phases.md](../archived/planning/phases.md)
