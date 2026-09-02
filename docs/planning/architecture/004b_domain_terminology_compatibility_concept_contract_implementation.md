# 004-B Domain Terminology Compatibility and Concept Contract Implementation

## Status

Accepted as the Phase 004-B implementation record.

This subgroup implements the first compatibility layer for accepted domain terminology and concept contracts.

It does not perform destructive class renames, table renames, database migrations, route rewrites, API response migrations, prompt rewrites, validator changes, report renderer changes, UI changes, deployment changes, GitHub Actions restoration, cloud infrastructure changes, or production data migrations.

---

# Required Implementation Header

```text
Phase 004 subgroup: 004-B — Domain Terminology Compatibility and Concept Contract Implementation
Phase 003 work packages executed: DTM-WP-001, DTM-WP-002, DTM-WP-004, DTM-WP-005, DTM-WP-006, DTM-WP-007, DTM-WP-008, DTM-WP-009, DTM-WP-011, DTM-WP-012
Applicable gates: documentation authority, terminology drift, domain compatibility, analysis scope, transcript version basis, evidence linkage, hypothesis boundary, support-level separation, safety posture, reflection point, corpus scope, report scope, regression
Compatibility posture: additive aliases and contracts only; existing implementation classes and persisted fields remain stable
Migration posture: no schema/data migration; destructive physical renames deferred
Tests / verification: tests/test_domain_concept_contracts.py added; readback verification recorded; runtime test execution not performed in this chat
Deferred or explicitly not touched: lifecycle implementation, privacy owner-scope hardening, validators, prompts, report renderer, UI, exports, cost-state behavior, GitHub Actions, production data
```

---

# Purpose

004-B begins controlled foundation implementation by giving the codebase a concept-safe domain compatibility surface.

It answers:

- How can later implementation refer to accepted concept terms without immediately renaming stable prototype classes?
- How should legacy/current implementation terms map to accepted product/domain concepts?
- Which concept contracts should exist before lifecycle, privacy, analysis, report, export, corpus, UI, and cost-state work expands?
- How do we keep hypothesis support separate from confidence?
- How do we introduce SafetyPosture and ReflectionPoint without changing existing persisted report fields yet?
- How do we create tests that prevent accidental terminology regressions?

---

# Governing Inputs

Primary guardrails:

```text
AGENTS.md
.cursor/rules/concept-refactor-guardrails.mdc
docs/planning/implementation_guardrails.md
docs/planning/phases/004_controlled_foundation_refactor_implementation.md
```

Phase 003 domain authority:

```text
docs/planning/architecture/003b_domain_terminology_concept_mapping_implementation_plan.md
docs/planning/inventories/003b_domain_concept_mapping_inventory.md
docs/planning/inventories/003b_domain_terminology_migration_work_packages.md
```

Implementation reference:

```text
backend/domain/enums.py
backend/domain/finding.py
backend/domain/workflow.py
backend/domain/synthesis.py
backend/domain/case.py
backend/domain/transcript.py
```

---

# Implementation Completed

004-B adds:

```text
backend/domain/concept_contracts.py
backend/domain/__init__.py
tests/test_domain_concept_contracts.py
docs/domain/README.md
```

It also adds this implementation record, a surface inventory, a gate checklist, and the 004-B subgroup summary.

---

# Runtime Contract Additions

`backend/domain/concept_contracts.py` introduces additive concept-safe aliases:

```text
ReflectionRun = WorkflowRun
ReflectionLens = ModuleDefinition
LensExecution = ModuleRun
ReflectionReport = SynthesisReport
CaseEvidenceCorpus = CaseDetail
```

These aliases are intentionally runtime-compatible with existing classes.

No persisted schema names changed.

No API fields changed.

No routes changed.

---

# Concept Contract Additions

004-B introduces additive Pydantic contract models:

```text
DomainTermMapping
AnalysisScope
ReflectionLensContract
HypothesisSupportAssessment
PsychologicalHypothesis
SafetyPosture
ReflectionPoint
CorpusPatternAssessment
ReportScope
```

It also introduces supporting enums:

```text
CompatibilityPosture
AnalysisScopeType
HypothesisSupportLevel
SafetyPostureLevel
ValidationStatus
```

These contracts are a foundation for later subgroups, not a full behavioral implementation.

---

# Accepted Decisions

## 1. Compatibility aliases are the correct first implementation step

Aliases let later code use accepted concept names while preserving existing prototype objects.

This satisfies the compatibility-first rule from 003-B and 004-A.

## 2. `Transcript` remains the near-term aggregate root

004-B records the decision as a runtime constant:

```text
TRANSCRIPT_AGGREGATE_DECISION
```

`ConversationRecord` remains conceptual and deferred.

## 3. `AnalysisScope` is additive and explicit

`AnalysisScope` now gives later code a small object for declaring:

```text
single transcript version
selected transcript set
case evidence corpus
future explicit workspace corpus
```

This does not yet wire scope into prompt construction, services, UI, reports, or exports.

That remains for later subgroups.

## 4. Hypothesis support is separate from confidence

`HypothesisSupportLevel` is separate from `Confidence`.

This prevents the system from collapsing hypothesis relation semantics into evidentiary strength.

## 5. `SafetyPosture` is introduced without changing legacy safety fields

Boolean `safety_mode` and list-style `safety_flags` remain intact.

`SafetyPosture` is the compatibility target for later validation/report/UI behavior.

## 6. `ReflectionPoint` is introduced without removing legacy intervention fields

`ReflectionPoint` exists as the target product-safe contract.

Legacy `FindingType.INTERVENTION` and report `interventions` remain until later report/API/UI migration gates are satisfied.

## 7. `CorpusPatternAssessment` requires explicit version lineage

The contract encodes transcript-version and evidence-quote lineage for future corpus claims.

It also exposes a basic `has_longitudinal_basis` property so tests can distinguish single-transcript and multi-transcript claims.

## 8. `ReportScope` exists before report/UI expansion

`ReportScope` gives later report work a compatibility target for scope, lenses, validation, safety posture, staleness, export readiness, and product-boundary reminder.

---

# Gates Addressed

| Gate | Result | Notes |
|---|---|---|
| documentation authority gate | Pass | `docs/domain/README.md` and 004-B records point to accepted authority |
| terminology drift gate | Pass | legacy/current terms mapped to accepted concept terms |
| domain compatibility gate | Pass | aliases/contracts added without destructive rename |
| analysis scope gate | Partial / foundation | `AnalysisScope` exists; service enforcement deferred |
| transcript version basis gate | Partial / foundation | scope carries version IDs; enforcement deferred |
| evidence linkage gate | Partial / foundation | hypothesis, reflection, corpus contracts carry evidence IDs |
| hypothesis boundary gate | Partial / foundation | `PsychologicalHypothesis` and support contract added; validators deferred |
| support-level separation gate | Pass | support level separated from `Confidence` |
| safety posture gate | Partial / foundation | `SafetyPosture` added; behavioral enforcement deferred |
| reflection point gate | Partial / foundation | `ReflectionPoint` added; UI/report migration deferred |
| corpus scope gate | Partial / foundation | `AnalysisScope` and `CorpusPatternAssessment` added; query enforcement deferred |
| report scope gate | Partial / foundation | `ReportScope` added; renderer/API integration deferred |
| regression gate | Partial / foundation | contract tests added; runtime execution not performed in this chat |

---

# Compatibility Notes

The following remain unchanged:

- existing domain class names
- database table and column names
- Alembic migrations
- API route paths
- API response field names
- prompt construction
- validator behavior
- report renderer behavior
- UI labels and components
- export behavior
- corpus retrieval behavior
- cost-state control behavior

This is intentional.

004-B is a compatibility foundation, not a rename/migration phase.

---

# Verification

Verification performed in this subgroup:

- read Phase 004 guardrails and 003-B work packages
- inspected existing domain classes and enums
- added additive runtime aliases and concept contracts
- exposed contract exports through `backend/domain/__init__.py`
- added contract tests for aliases, mappings, analysis scope explicitness, support/confidence separation, safety override levels, reflection points, corpus basis, report scope, and alias construction
- added implementation-facing domain guide
- updated planning indexes

Runtime tests were added but not executed here because this chat is operating through repository edits, and GitHub Actions remain intentionally disabled.

---

# Deferred Work

Deferred to later subgroups:

- make `AnalysisScope` mandatory in execution flow
- require transcript-version-bound evidence for retained analysis
- add lifecycle/retention fields or migrations
- add privacy owner-scope changes
- wire `ReflectionLensContract` into module registry and prompt compiler
- replace validator behavior around hypotheses and safety posture
- migrate report renderer from `interventions` to `ReflectionPoint`
- migrate UI labels/components
- expose `ReportScope` through API responses
- enforce corpus scope and staleness behavior
- decide physical class/table/API renames
- execute any production migration

---

# Handoff to 004-C

004-C should use the concept contracts without changing their compatibility posture.

Relevant 004-B foundations for 004-C:

```text
AnalysisScope
CaseEvidenceCorpus
CorpusPatternAssessment
ReportScope
TRANSCRIPT_AGGREGATE_DECISION
docs/domain/README.md
```

004-C should focus on lifecycle, retention, source-artifact, and deletion-cascade foundation work.

---

# Decision

004-B passes as a controlled compatibility implementation subgroup.

Proceed next to:

```text
004-C — Lifecycle, Retention, SourceArtifact, and Deletion-Cascade Foundation
```
