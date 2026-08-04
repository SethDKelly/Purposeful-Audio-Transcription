# Module lifecycle (v1.4)

## Visibility

- Registry YAML: `config/modules/*.yaml`
- Prompts: `config/prompts/` (via `prompt_file`)
- Live inventory: `GET /api/v1/modules` and `GET /api/v1/modules/lifecycle` (includes `prompt_sha256`)
- React: Modules page

## Changelog practice

1. Bump `version` in the module YAML when prompts or output expectations change.
2. Note the change in the PR description and, for material changes, `docs/developer/api_changelog.md` if API shape is affected.
3. Compare prompt hashes via lifecycle endpoint before/after release.

## Deprecated modules

Set `enabled: false` in YAML. Lifecycle marks `deprecated: true`. Keep YAML for historical runs.

## Old report compatibility

- Persisted module runs store `module_id` and version metadata at execution time.
- Interpret historical reports with the **run-time** version, not only the live registry.
- Output schema field (`output_schema`, typically `module_output_v1`) gates parser expectations; do not silently reinterpret incompatible schemas.
- Migration: prefer additive fields; breaking output changes require a new schema id and dual-read period.

## Evaluation before release

Run golden eval (`scripts/run_golden_eval.py`) and safety fixtures when prompts change. Diff prompt sha256 in review.
