# 02 — v1.2 Evaluation, Safety, API Contracts, and React Readiness

## Phase Goal

Make the system measurable, safer, and ready for a React client.

v1.2 should not primarily add new user-facing product scope. It should establish the quality and contract foundation that future product growth depends on.

---

# Primary Outcomes

By the end of v1.2:

- golden evaluation harness exists
- safety red-team fixtures exist
- forbidden/unsafe claims are scored
- module versions can be compared
- API v1 contracts are documented and tested
- OpenAPI is stable enough for client generation
- Streamlit operates as an API client
- React stack and migration plan are selected

---

# Workstream A — Golden Evaluation Harness

## Implementation Tasks

- [ ] Create an evaluation runner for golden fixtures.
- [ ] Support running selected workflows against selected fixtures.
- [ ] Store structured eval outputs outside fixture files.
- [ ] Score required signals from `expected_assertions.yaml`.
- [ ] Score forbidden or low-confidence claim categories.
- [ ] Track schema validity.
- [ ] Track evidence quote coverage.
- [ ] Track unsupported inference rate.
- [ ] Track construct coverage.
- [ ] Track confidence ceiling violations.
- [ ] Generate Markdown/JSON eval reports.
- [ ] Add release-gate thresholds for critical tests.

## Suggested Metrics

```yaml
fixture_id: GT001
workflow_id: full_suite
module_id: nvc_analysis
schema_valid: true
finding_count: 8
construct_count: 6
evidence_coverage_rate: 0.95
required_signal_hit_rate: 0.85
forbidden_claim_count: 0
unsupported_claim_count: 0
confidence_ceiling_violations: 0
```

## Acceptance Criteria

- Golden evals can run locally.
- Eval reports are saved and comparable.
- Failing forbidden-claim tests are visible.
- Eval output can guide prompt/module revisions.

---

# Workstream B — Safety Red-Team Fixtures

## Implementation Tasks

Create synthetic fixtures for explicit threats, coercive control indicators, stalking/monitoring behavior, severe humiliation/intimidation, self-harm language, ambiguous high-conflict language, false-positive ordinary conflict, and manipulation-like but evidence-limited scenarios.

For each fixture, add transcript, metadata, expected safety behavior, forbidden outputs, expected UI warning mode, and expected module suppression rules where applicable.

## Required Safety Assertions

The system should avoid diagnosing, avoid determining abuse as fact from insufficient evidence, avoid mutualizing serious safety concerns, recommend appropriate support language when severe risk appears, distinguish high-risk evidence from ordinary conflict, and preserve uncertainty where evidence is ambiguous.

## Acceptance Criteria

- At least 5 safety red-team fixtures exist.
- Safety mode behavior is testable.
- False-positive and false-negative risks are tracked.
- Safety fixture tests are part of release checks.

---

# Workstream C — Forbidden-Claim and Confidence Scoring

## Implementation Tasks

- [ ] Define forbidden/high-risk claim taxonomy.
- [ ] Add detector/scorer for high-risk claims.
- [ ] Flag diagnosis, personality disorder determination, narcissism determination, abuse determination, coercive control determination, intentional manipulation determination, trauma-history claim, stable attachment-style claim, and relationship prognosis.
- [ ] Allow exploratory discussion only with low/moderate confidence and caveats.
- [ ] Add tests ensuring speculative domains remain appropriately caveated.

## Acceptance Criteria

- High-risk claims are automatically flagged in eval runs.
- Confidence misuse is detectable.
- Outputs with forbidden determinations fail safety evals.

---

# Workstream D — Module Version Comparison

## Implementation Tasks

- [ ] Store module ID, module version, prompt version, compiler hash, and model ID.
- [ ] Run same fixture/module across two module versions.
- [ ] Compare schema validity, signal hit rate, evidence coverage, construct count, forbidden claim count, cost/latency, and human review score.
- [ ] Generate comparison reports.

## Acceptance Criteria

- Developers can compare module versions on golden fixtures.
- Regression risk is visible before release.
- Prompt changes become testable.

---

# Workstream E — API v1 Contract Stabilization

## Recommended API Surface

```text
POST   /api/v1/transcripts
GET    /api/v1/transcripts/{id}
PATCH  /api/v1/transcripts/{id}/turns
POST   /api/v1/workflow-runs
GET    /api/v1/workflow-runs/{id}
GET    /api/v1/workflow-runs/{id}/status
GET    /api/v1/reports/{id}
GET    /api/v1/reports/{id}/findings
GET    /api/v1/reports/{id}/evidence
POST   /api/v1/findings/{id}/feedback
GET    /api/v1/cases/{id}
GET    /api/v1/cases/{id}/timeline
POST   /api/v1/exports
```

## Implementation Tasks

- [ ] Formalize `/api/v1`.
- [ ] Add response schema versioning.
- [ ] Generate OpenAPI spec.
- [ ] Add OpenAPI snapshot tests.
- [ ] Create frontend-facing DTOs.
- [ ] Ensure API errors use a stable shape with `error_code`, `message`, `request_id`, and safe `details`.
- [ ] Add API contract tests.

## Acceptance Criteria

- API contracts are documented.
- OpenAPI can generate a TypeScript client.
- Breaking changes are detectable.
- Streamlit uses the same API surface React will use.

---

# Workstream F — React Readiness

## Implementation Tasks

- [ ] Choose React stack.
- [ ] Create screen inventory.
- [ ] Create component inventory.
- [ ] Document product flows.
- [ ] Decide Streamlit long-term role.
- [ ] Define generated API client approach.
- [ ] Define frontend auth/API-key/session approach.
- [ ] Define frontend deployment target.
- [ ] Create `docs/planning/react_frontend_plan.md`.

## Recommended Stack

```text
Vite
React
TypeScript
TanStack Query
React Router
Zod
Tailwind or shadcn/ui
OpenAPI-generated API client
React Flow or Cytoscape.js for graph views
Vitest
Playwright
```

## Acceptance Criteria

- React stack decision is documented.
- API is stable enough to start React MVP.
- Streamlit has been constrained to API-client behavior.
- No React implementation is required to complete v1.2, but the path is clear.

---

# v1.2 Exit Criteria

v1.2 is complete when the golden evaluation harness exists, safety red-team fixtures exist, forbidden claim scoring exists, module version comparison exists or is scaffolded, `/api/v1` is stable enough for React, OpenAPI is generated and tested, React stack and migration plan are documented, and Streamlit behaves like an external API client.
