# Golden Fixture Evaluation Plan (v0.7 Priority 5)

Regression and quality foundation before growing the module set. Roadmap: [../planning/roadmap_v0.7_to_v1.0.md](../planning/roadmap_v0.7_to_v1.0.md). Related: [../design/14_testing_evaluation_and_safety.md](../design/14_testing_evaluation_and_safety.md), prior P1-5b / P1-6 fixture intent.

## Fixtures

Create **5–10** golden or synthetic transcripts under `tests/fixtures/transcripts/` (anonymized). Each module should be evaluable on at least one fixture.

## Automated checks

| Check | Intent |
|-------|--------|
| JSON validity | Structured outputs parse |
| Evidence quote validity | Quote IDs resolve to turns |
| Confidence ceiling violations | Ontology / module ceilings |
| Unsupported diagnostic language | Safety lint |
| Construct count | Against `expected_constructs` / minimums |
| Evidence coverage | Fraction of findings with quotes |
| Module completion status | No silent skips |

## Manual rubric

Short reviewer scoring for report usefulness, evidence grounding, speculation, and safety tone (doc + optional spreadsheet).

## Acceptance

Fixtures run locally; failures easy to inspect; prompt/compiler changes comparable to prior snapshots/contracts.

## Tests

`pytest` fixture validity; snapshot/contract tests for structured outputs; safety-language lint tests.
