# Golden Transcript Fixtures — Implementation Note

**Status:** Active evaluation substrate for **v0.7 Priority 5** (and usable earlier for ingest/quote/workflow smoke).  
**Canonical plan:** [implementing.md](implementing.md) · [../evaluation/golden_fixture_evaluation_plan.md](../evaluation/golden_fixture_evaluation_plan.md)

## Location

```text
tests/fixtures/golden_transcripts/
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
| `metadata.yaml` | Stable machine metadata (id, participants, tags, recommended workflows) |
| `expected_assertions.yaml` | Machine-checkable assertions for automated / golden tests |

## Why these fixtures exist

Golden transcripts are needed to:

- Regression-test ingest → quote ID assignment without depending on live Bedrock
- Smoke-test workflows/modules with **mocked** LLM outputs against realistic multi-turn dialogue
- Anchor human + automated evaluation (construct signals, safety bounds) before growing the module set
- Optionally run **live model** golden checks marked `@pytest.mark.integration` + `@pytest.mark.golden` (not in default CI)

## Pytest coverage expectations

1. Load each fixture's `transcript.json` (schema sanity: `fixture_id`, `turns`, speakers)
2. Generate/validate sequential quote IDs (`Q001`…) after ingest
3. Parse `expected_assertions.yaml` successfully
4. Smoke-test workflow/module execution against fixtures with mocked LLM outputs
5. Optional live Bedrock golden tests: `@pytest.mark.integration` and `@pytest.mark.golden` (skipped unless explicitly selected)

## Adding a new fixture

1. Create `tests/fixtures/golden_transcripts/<ID>_<slug>/`
2. Add the five files above (signals + assertions should agree on high-confidence targets)
3. Extend `tests/test_golden_transcripts.py` discovery (auto-discovers subdirs with `transcript.json`)
4. Prefer anonymized content; keep `safety_level` accurate in metadata

## Related

- Loader helper: `tests/helpers/golden_transcripts.py`
- Tests: `tests/test_golden_transcripts.py`
