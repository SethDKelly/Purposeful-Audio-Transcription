# 003-B Domain Terminology and Concept Mapping Implementation Plan

## Status

Accepted as the Phase 003-B domain terminology and concept mapping implementation plan.

This document converts the accepted concept/domain mapping into implementation-ready planning targets.

It does not authorize code changes, schema migrations, API rewrites, prompt rewrites, report renderer changes, UI changes, deployment changes, or production data migrations by itself.

---

# Purpose

Prepare the domain model for later implementation refactoring without allowing legacy code names or older design documents to override accepted product concepts.

003-B turns the Phase 002 concept-to-domain mapping into a practical implementation plan for:

- retained domain foundations
- transitional aliases
- product-facing terminology
- implementation-facing terminology
- eventual schema/API/report migration targets
- acceptance gates for later implementation

---

# Governing Inputs

Primary authority:

- `docs/concepts/`
- `docs/planning/architecture/002i_phase_002_exit_review_consolidation.md`
- `docs/planning/inventories/002i_phase_003_authorized_scope.md`
- `docs/planning/architecture/003a_documentation_authority_cleanup_plan.md`

Phase 002 domain inputs:

- `docs/planning/inventories/002b_concept_domain_model_mapping.md`
- `docs/planning/inventories/002b_domain_gap_register.md`
- `docs/planning/inventories/002e_analysis_boundary_contracts.md`
- `docs/planning/inventories/002h_refactor_backlog.md`

Reference materials inspected:

- `docs/design/03_domain_model.md`
- `backend/domain/transcript.py`
- `backend/domain/finding.py`
- `backend/domain/workflow.py`
- `backend/domain/case.py`
- `backend/domain/synthesis.py`
- `backend/domain/enums.py`

---

# Accepted Domain Refactor Principle

```text
Keep useful implementation foundations, introduce concept-safe aliases and contracts, and defer destructive renames until retention, privacy, analysis, and evaluation gates are ready.
```

The current domain model is useful prototype material.

It should not be discarded.

It also should not remain the sole authority for product language.

---

# Implementation Planning Decision Summary

## 1. Transcript remains the practical near-term aggregate root

`Transcript` should remain the near-term implementation aggregate for conversation text, speakers, turns, transcript versions, and evidence quotes.

`ConversationRecord` remains a conceptual umbrella for now.

A separate `ConversationRecord` implementation object is deferred unless later lifecycle or source-artifact planning shows that `Transcript` cannot safely represent the aggregate boundary.

## 2. TranscriptVersion is promoted as the stable evidence basis

`TranscriptVersion` already exists and should be preserved.

Later implementation should harden the rule that retained analysis binds to a transcript version.

`EvidenceQuote.transcript_version_id` should become required for retained analysis outputs once migration safety is planned.

## 3. WorkflowRun maps to ReflectionRun

`WorkflowRun` may remain an internal orchestration object initially.

Product-facing language, reports, and future API/resource naming should use `ReflectionRun` where the user is interacting with an analysis execution over a declared evidence scope.

Transitional implementation plan:

```text
WorkflowRun internal orchestration
ReflectionRun product/domain alias
```

Do not perform a broad class/table rename until schema, API, tests, and migrations are planned.

## 4. ModuleDefinition and ModuleRun map to ReflectionLens concepts

`ModuleDefinition` and `ModuleRun` may remain implementation names initially.

They should be wrapped or documented as implementation representations of `ReflectionLens` and lens execution.

Later implementation should add or map `ReflectionLensContract` fields rather than relying only on `primary_lens`, `inference_depth`, and `confidence_ceiling`.

## 5. Finding remains useful but Hypothesis needs stronger separation

`Finding` is a useful evidence-backed analytical claim object.

`FindingType.HYPOTHESIS` is not sufficient as the mature representation for a bounded psychological hypothesis.

Later implementation should introduce `PsychologicalHypothesis` and `HypothesisSupportAssessment` or a schema convention that keeps source, support level, evidence for, evidence against, alternatives, limitations, confidence, and non-diagnostic boundary separate from ordinary findings.

## 6. SynthesisReport maps to ReflectionReport

`SynthesisReport` remains useful as an integrated output object.

Product-facing language should move toward `ReflectionReport`.

The existing `interventions` field should be treated as transitional legacy terminology and mapped to `ReflectionPoint` semantics before UI/report polish.

## 7. Recommendation and Intervention language should migrate to ReflectionPoint

`FindingType.INTERVENTION`, report `interventions`, graph `INTERVENTION_FOR`, and UI/report recommendation language should be replaced or wrapped by `ReflectionPoint` semantics.

This should be a terminology and schema migration plan, not a casual copy edit.

Reflection points must remain evidence-linked, non-prescriptive, self-review oriented, and safety-bounded.

## 8. SafetyMode should migrate toward SafetyPosture

`WorkflowRun.safety_mode` and `ModuleRun.safety_flags` are useful signals but not a sufficient architecture target.

Later implementation should introduce or map `SafetyPosture` with posture value, trigger evidence, risk indicators, uncertainty, suppressed sections/lenses, and required report behavior.

## 9. Case should become the visible Case Evidence Corpus boundary

`Case` and case-linked transcript summaries should be preserved.

Later implementation should make case membership retention-significant and corpus-reasoning significant.

A `Case Evidence Corpus` should use included transcript versions and evidence quotes, not hidden account-wide history.

## 10. SourceType.AUDIO is not enough for Recording lifecycle

`SourceType.AUDIO` can continue to identify how a transcript originated.

It does not fully represent ephemeral audio retention, failed transcription TTL, source-artifact status, purge events, or deletion cascades.

003-C should plan `SourceArtifact` / `RecordingArtifact` or equivalent lifecycle semantics.

## 11. Confidence and hypothesis support should remain separate

The existing `Confidence` enum is usable as a transitional implementation scale.

Hypothesis support levels should not be forced into that enum.

Later implementation should map confidence to evidence strength while `HypothesisSupportAssessment.support_level` carries hypothesis relation semantics such as consistent, partially consistent, contradicted, insufficient evidence, or alternative explanation likely.

## 12. Domain terminology migration should prefer compatibility first

The safest implementation path is:

```text
inventory -> aliases/contracts -> adapters/DTOs -> validators/tests -> schema/API rename if still warranted
```

Avoid early destructive renames that could break persistence, migrations, reports, exports, or evaluation fixtures.

---

# Implementation Sequencing Recommendation

003-B recommends this sequence for later authorized implementation work:

1. Add domain glossary / authority note near domain docs or code package.
2. Preserve existing stable entities: Transcript, TranscriptVersion, EvidenceQuote, Finding, Case, graph objects.
3. Add concept aliases in documentation and implementation planning before renaming code.
4. Introduce `AnalysisScope` and version-binding semantics before prompt/report/corpus work.
5. Introduce or map `ReflectionLensContract` over module definitions.
6. Introduce or map `PsychologicalHypothesis`, `HypothesisSupportAssessment`, `SafetyPosture`, `ReflectionPoint`, and `CorpusPatternAssessment`.
7. Plan any schema/API/report field renames only after tests and validators exist.
8. Use 003-C through 003-G to attach lifecycle, privacy, analysis, cost-state, and UI gates.

---

# Recommended Domain Mapping Boundary

| Concept Layer | Implementation Strategy |
|---|---|
| Product language | Use accepted concept names immediately in docs/plans/reports/UI planning |
| Internal code names | Keep stable initially where changing them would be risky |
| API/DTO language | Add aliases or new fields only after migration plan |
| Database schema | Defer destructive rename; add new tables/fields only through gated implementation phase |
| Reports/exports | Prefer concept language; preserve source identifiers for traceability |
| Tests/evals | Add concept boundary tests before renames |

---

# Gates Required for Later Implementation

003-B carries forward these gates:

- documentation authority gate
- terminology drift gate
- domain mapping gate
- analysis boundary gate
- hypothesis boundary gate
- safety override gate
- corpus reasoning gate
- report scope gate
- reflection point gate
- evaluation gate
- regression gate

Additional gates from later subgroups apply before implementation:

- retention gate
- deletion cascade gate
- privacy boundary gate
- log redaction gate
- export boundary gate
- cost state gate
- job-safe shutdown gate
- workflow replacement gate

---

# Files Requiring Later Targeted Audit

Later implementation planning should inspect and map at least:

```text
backend/domain/transcript.py
backend/domain/finding.py
backend/domain/workflow.py
backend/domain/case.py
backend/domain/synthesis.py
backend/domain/enums.py
alembic/versions/*
backend/api/*
backend/services/*
frontend/*
docs/design/03_domain_model.md
docs/design/04_knowledge_ontology.md
docs/design/05_data_model_and_schemas.md
docs/design/06_analysis_modules.md
docs/design/08_workflow_engine.md
docs/design/09_evidence_confidence_and_citations.md
docs/design/10_synthesis_engine.md
docs/design/11_ui_ux_design.md
```

003-B does not complete those audits for every file.

It establishes the implementation plan and mapping obligations for later subgroups.

---

# Handoff to 003-C

003-C should use this domain mapping plan to prepare lifecycle and retention implementation planning for:

- `SourceArtifact` / `RecordingArtifact`
- transcript draft state
- saved transcript retention
- case assignment retention
- transcript version retention and staleness
- evidence quote retention
- derived report/graph/hypothesis retention inheritance
- export artifact lifecycle
- deletion cascades

---

# Non-goals

003-B does not implement:

- class renames
- table renames
- database migrations
- schema changes
- API field changes
- prompt changes
- report renderer changes
- UI changes
- validators
- tests
- data migrations

---

# Acceptance Result

The domain terminology and concept mapping implementation plan is ready to feed 003-C and later implementation phases.

Proceed next to:

```text
003-C — Data Lifecycle / Retention Foundation Implementation Plan
```
