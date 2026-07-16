# Golden Fixture Evaluation Plan (v0.7 Priority 5)

Regression and quality foundation before growing the module set. Roadmap: [../planning/roadmap_v0.7_to_v1.0.md](../planning/roadmap_v0.7_to_v1.0.md). Related: [../design/14_testing_evaluation_and_safety.md](../design/14_testing_evaluation_and_safety.md), prior P1-5b / P1-6 fixture intent.

**Layout & conventions (reference):** [../planning/golden_transcript_fixtures.md](../planning/golden_transcript_fixtures.md)

## Fixtures

Rich scenarios live under `tests/fixtures/golden_transcripts/<ID>_<slug>/` (one directory per fixture).

**Shipped:**

| ID | Slug | Theme |
|----|------|--------|
| GT001 | missed_dinner_couple | Romantic partners — missed dinner / repair |
| GT002 | caregiving_siblings | Adult siblings — caregiving + money |

**Target:** 5–10 golden fixtures total. Short parser samples remain under `tests/fixtures/transcripts/`.

### Per-fixture files

| File | Required |
|------|----------|
| `transcript.md` | yes |
| `transcript.json` | yes |
| `expected_signals.md` | yes (human) |
| `metadata.yaml` | yes |
| `expected_assertions.yaml` | yes (machine) |

## Automated checks

| Check | Intent |
|-------|--------|
| JSON validity | `transcript.json` loads; turns have speaker/text |
| Evidence quote validity | Sequential `Q001…` after ingest |
| Assertions YAML parse | `expected_assertions.yaml` loads |
| Mocked workflow smoke | `quick_review` (or recommended) with mocked LLM |
| Confidence ceiling / safety language | Expand as ontology (v0.7 P3–P4) lands |
| Construct count / evidence coverage | After module `expected_constructs` |

## Manual rubric

Use `expected_signals.md` for human review (construct targets, module expectations, safety bounds).

## Live golden tests

Mark with `@pytest.mark.integration` and `@pytest.mark.golden`. Skip unless `RUN_GOLDEN_LIVE=1`. Do not run in default Deploy CI.

## Acceptance

Fixtures run locally; failures easy to inspect; prompt/compiler changes comparable to prior snapshots/contracts.

## Tests

- `tests/helpers/golden_transcripts.py` — loader
- `tests/test_golden_transcripts.py` — load JSON, quote IDs, parse assertions, mocked smoke, optional live marker
