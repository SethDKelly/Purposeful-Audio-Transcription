# Golden Transcript Fixtures

Signal-based regression fixtures for the Relationship Reasoning Engine (RRE). These are **test inputs and evaluation targets**, not production configuration.

## Layout

Each fixture lives in its own subdirectory:

```text
tests/fixtures/golden_transcripts/
  README.md
  GT001_missed_dinner_couple/
    transcript.md              # Human-readable dialogue
    transcript.json            # Machine-readable turns + metadata
    expected_signals.md        # Human evaluator guide
    metadata.yaml              # Stable machine metadata
    expected_assertions.yaml   # Machine-checkable signal assertions
  GT002_caregiving_siblings/
    …
```

## Principles

1. **Test signals, not prose** — assert constructs, evidence citations, and confidence bounds; avoid snapshotting LLM paragraphs.
2. **Evidence traceability** — important findings must cite quote IDs that exist in the evidence index.
3. **Negative assertions** — `forbidden_or_low_confidence` guards against unsupported clinical/diagnostic claims.
4. **Stable fixtures** — treat transcript edits like schema changes; update metadata, signals, and assertions together.
5. **Separate run outputs** — do not overwrite fixture files with model outputs; store golden run artifacts under `tests/golden_results/` (future) or local `tmp/golden_runs/`.

## Pytest markers

| Marker | Purpose |
|--------|---------|
| `golden` | Uses golden transcript fixtures |
| `integration` | Multiple services or external deps |
| `live_model` | Calls a real LLM provider |
| `slow` | Longer-running checks |

Examples:

```bash
pytest -m golden
pytest -m "golden and not live_model"
pytest -m "golden and integration"
RUN_LIVE_GOLDEN_TESTS=1 pytest -m "golden and live_model"
```

## Adding a fixture

1. Create `tests/fixtures/golden_transcripts/<ID>_<slug>/` with all five required files.
2. Keep `metadata.yaml` and `expected_assertions.yaml` aligned on `fixture_id`.
3. Ensure `required_quote_substrings` and each signal's `must_reference_any` appear in `transcript.json`.
4. Run `pytest -m golden` — discovery is automatic for directories containing `transcript.json`.

## Related

- Loader and evaluation helpers: `tests/helpers/golden_transcripts.py`
- Planning note: `docs/planning/golden_transcript_fixtures.md`
- Evaluation plan: `docs/evaluation/golden_fixture_evaluation_plan.md`
