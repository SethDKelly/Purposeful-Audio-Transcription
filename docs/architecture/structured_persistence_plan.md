# Structured Persistence Plan (v0.8) — **Shipped in v0.8.0**

Normalize findings, constructs, evidence, and relationships out of module JSON blobs into queryable product objects. Roadmap: [../archived/planning/phases.md](../archived/planning/phases.md#phase-31--normalized-findings-persistence). Release notes: [../releases/v0.8.0.md](../releases/v0.8.0.md).

## Priority 1 — Findings — Done

Entities: `findings`, `finding_evidence_quotes`, `finding_alternative_explanations`.

**Acceptance met:** Findings queryable without parsing raw JSON; links to module runs + quotes retained; exploration prefers DB with JSON fallback.

## Priority 2 — Constructs — Done

Entities: `constructs`, `construct_evidence_quotes`, `construct_sources`.

**Acceptance met:** Types validated against [ontology_v1.md](ontology_v1.md); unknown types stored with warnings; evidence traceability preserved.

## Priority 3 — Relationships — Done

Entity: `construct_relationships` (+ optional evidence quotes table).

**Acceptance met:** Queryable; ontology-validated types; dangling links stored with warnings.

## Priority 4 — Merge / deduplication — Done

`GraphMergeService` similarity pass; absorbed constructs keep `merged_into_id`; sources preserved on canonical rows.

## Priority 5 — Convergence scoring — Done

`ConvergenceScoringService` writes `convergence_score` + rationale JSON (`strong` / `moderate` / `weak` / `contested`).

## Priority 6 — Exploration UI — Done

`GET /api/workflow-runs/{id}/structured-graph` + Streamlit **Structured inventory** tab (filters by type/confidence/module).

## Priority 7 — Synthesis over structured objects — Done

Meta-synthesis handoff prefers `structured_inventory`; merge/score before synthesis; prompt cites finding/construct IDs.

## Implementation notes

- Alembic: `005_normalized_findings`, `006_normalized_constructs`, `007_construct_relationships`.
- Raw module JSON kept on `module_runs.parsed_output` for audit/replay.
- ORM: `backend/db/models.py` (`FindingRow`, `ConstructRow`, `ConstructRelationshipRow`, …).
