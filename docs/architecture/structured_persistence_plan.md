# Structured Persistence Plan (v0.8)

Normalize findings, constructs, evidence, and relationships out of module JSON blobs into queryable product objects. Roadmap: [../planning/roadmap_v0.7_to_v1.0.md](../planning/roadmap_v0.7_to_v1.0.md). Design anchors: [../design/05_data_model_and_schemas.md](../design/05_data_model_and_schemas.md), [../design/03_domain_model.md](../design/03_domain_model.md).

## Priority 1 — Findings

Suggested entities: `findings`, `finding_evidence_quotes`, `finding_alternative_explanations`, `finding_module_sources`.

Fields (minimum): ID, workflow_run_id, module_run_id, source module ID/version, text, construct/category type, confidence, evidence quote IDs, alternative explanations, limitations, created_at.

**Acceptance:** Findings queryable without parsing raw JSON; links to module runs + quotes retained; reports use normalized data or safe JSON fallback.

## Priority 2 — Constructs

Entities: `constructs`, `construct_evidence_quotes`, `construct_sources`.

Fields: construct ID, ontology type, label, description, confidence, source module IDs, evidence quote IDs, optional canonical value.

**Acceptance:** Types validated against [ontology_v1.md](ontology_v1.md); evidence traceability preserved.

## Priority 3 — Relationships

Entity: `construct_relationships` — source ID, relationship type, target ID, confidence, evidence quote IDs, source module ID.

**Acceptance:** Queryable; ontology-validated types; invalid links rejected or stored with warnings.

## Priority 4 — Merge / deduplication

Similarity pass across modules; merge near-duplicates; preserve sources; merged confidence from evidence + convergence; track contributing modules.

## Priority 5 — Convergence scoring

Deterministic inputs: supporting module count, evidence quality, confidence ratings, contradictions, ontology confidence ceilings. UI explains strong vs weak ratings without relying only on model prose.

## Priority 6 — Exploration UI

Table-first explorer: constructs, relationships, findings, quotes, modules, confidence, convergence. Filters by type/confidence/module/quote.

## Priority 7 — Synthesis over structured objects

Meta-synthesis prompt primary input = structured inventory; narrative still LLM-written; cites normalized IDs; separates robust vs exploratory.

## Implementation notes

- Alembic migrations under `alembic/versions/`.
- Keep raw module JSON for audit/replay during transition.
- TODO: exact ORM table names when implementing — align with existing SQLAlchemy models.
