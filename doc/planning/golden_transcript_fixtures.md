# Golden Transcript Fixtures — Implementation Note

**Status:** Active evaluation substrate for **v0.7 Priority 5**.  
**Canonical plan:** [implementing.md](implementing.md) · [../evaluation/golden_fixture_evaluation_plan.md](../evaluation/golden_fixture_evaluation_plan.md)

## Location

```text
tests/fixtures/golden_transcripts/
  README.md
  GT001_missed_dinner_couple/
  GT002_caregiving_siblings/
  …
```

One subdirectory per fixture. Existing short `.txt` fixtures under `tests/fixtures/transcripts/` remain for parser smoke; **rich golden scenarios** live here.

## Required files per fixture

| File | Role |
|------|------|
| `transcript.md` | Human-readable labeled dialogue |
| `transcript.json` | Machine-readable turns + scenario metadata fields |
| `expected_signals.md` | Human evaluator guide (construct targets, module expectations) |
| `metadata.yaml` | Stable machine metadata (id, participants, patterns, safety bounds) |
| `expected_assertions.yaml` | Signal-based machine assertions (`required_signals`, forbidden claims) |

## Why these fixtures exist

Golden transcripts support:

- Regression-test ingest → quote ID assignment without live Bedrock
- Smoke-test workflows/modules with **mocked** LLM outputs against realistic dialogue
- Signal-based evaluation (constructs, evidence, confidence bounds) — not prose snapshots
- Optional **live model** golden checks (`RUN_LIVE_GOLDEN_TESTS=1`)

## Pytest coverage

| File | Purpose |
|------|---------|
| `test_golden_fixture_loading.py` | Directory layout, JSON/YAML validity |
| `test_golden_expected_assertions.py` | Assertion schema, signal structure |
| `test_golden_evidence_index.py` | Quote IDs, required substring presence |
| `test_golden_module_contracts.py` | Mocked module output + evidence validation |
| `test_golden_workflow_smoke.py` | Mocked workflow smoke; optional live ingest |

Run:

```bash
pytest -m golden
pytest -m "golden and not live_model"
RUN_LIVE_GOLDEN_TESTS=1 pytest -m "golden and live_model"
```

## Adding a new fixture

1. Create `tests/fixtures/golden_transcripts/<ID>_<slug>/` with all five files.
2. Align `metadata.yaml` and `expected_assertions.yaml` on `fixture_id`.
3. Ensure `required_quote_substrings` and each signal's `must_reference_any` appear in `transcript.json`.
4. Discovery is automatic — no test file edits required.

## Related

- Fixture README: `tests/fixtures/golden_transcripts/README.md`
- Loader + evaluation helpers: `tests/helpers/golden_transcripts.py`
