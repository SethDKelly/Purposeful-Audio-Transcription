# 004-B — Domain Terminology Compatibility and Concept Contract Implementation

## Status

Complete.

This subgroup implements the first additive compatibility layer for accepted domain terminology and concept contracts.

It does not perform destructive class renames, table renames, database migrations, route rewrites, API response migrations, prompt rewrites, validator changes, report renderer changes, UI changes, deployment changes, GitHub Actions restoration, cloud infrastructure changes, or production data migrations.

---

# Purpose

004-B begins controlled foundation implementation by installing concept-safe domain contracts while preserving stable prototype classes and persisted shapes.

It answers:

- How should current implementation terms map to accepted concepts?
- How can later code import concept-safe names without breaking current classes?
- Which contracts are needed before lifecycle, privacy, analysis, report, corpus, export, UI, and cost-state work expands?
- How should hypothesis support remain distinct from confidence?
- How should SafetyPosture, ReflectionPoint, CorpusPatternAssessment, and ReportScope enter the codebase safely?

---

# Outputs

| Output | Document / Surface |
|---|---|
| Domain concept compatibility contracts | `../../../backend/domain/concept_contracts.py` |
| Domain package exports | `../../../backend/domain/__init__.py` |
| Domain concept contract tests | `../../../tests/test_domain_concept_contracts.py` |
| Domain terminology compatibility guide | `../../domain/README.md` |
| 004-B implementation record | `../architecture/004b_domain_terminology_compatibility_concept_contract_implementation.md` |
| 004-B surface inventory | `../inventories/004b_domain_contract_surface_inventory.md` |
| 004-B gate checklist | `../inventories/004b_domain_compatibility_gate_checklist.md` |

---

# Implementation Completed

004-B adds additive aliases:

```text
ReflectionRun = WorkflowRun
ReflectionLens = ModuleDefinition
LensExecution = ModuleRun
ReflectionReport = SynthesisReport
CaseEvidenceCorpus = CaseDetail
```

004-B adds additive contracts and enums:

```text
DomainTermMapping
CompatibilityPosture
AnalysisScope
AnalysisScopeType
ReflectionLensContract
HypothesisSupportLevel
HypothesisSupportAssessment
PsychologicalHypothesis
SafetyPostureLevel
SafetyPosture
ReflectionPoint
CorpusPatternAssessment
ReportScope
ValidationStatus
```

004-B also adds helper functions:

```text
get_domain_term_mapping()
concept_term_for()
```

---

# Accepted Decisions

## 1. Compatibility-first implementation is accepted

The implementation uses aliases and additive contracts instead of destructive renames.

Existing runtime classes remain unchanged and available.

## 2. Product-safe names now have a code entry point

Later subgroups can import concept-safe terms from:

```text
backend.domain.concept_contracts
```

## 3. Domain package exports are available

The domain package now re-exports the 004-B compatibility contracts through:

```text
backend.domain
```

## 4. Hypothesis support remains separate from confidence

`HypothesisSupportLevel` is distinct from `Confidence` and is tested as separate.

## 5. Safety posture and reflection points enter as contracts, not behavior changes

`SafetyPosture` and `ReflectionPoint` are now available for later subgroups, but validators, reports, UI, and exports are not changed by 004-B.

## 6. Corpus and report scope foundations exist

`CorpusPatternAssessment` and `ReportScope` are now available as concept-safe structures for later analysis/report/UI work.

## 7. Physical rename remains deferred

No code-level destructive rename decision is made.

Physical class/table/API rename remains a later P2 decision that requires compatibility, migration, regression, and release-readiness gates.

---

# Work Packages Executed

004-B executes or partially executes these 003-B work packages:

```text
DTM-WP-001 — Domain authority and glossary lock
DTM-WP-002 — Transcript aggregate decision record
DTM-WP-004 — ReflectionRun compatibility mapping
DTM-WP-005 — ReflectionLens contract mapping
DTM-WP-006 — Hypothesis separation plan
DTM-WP-007 — SafetyPosture migration plan
DTM-WP-008 — ReflectionPoint migration plan
DTM-WP-009 — Case Evidence Corpus mapping plan
DTM-WP-011 — Confidence/support-level mapping
DTM-WP-012 — ReflectionReport compatibility mapping
```

004-B only lays foundation for DTM-WP-003 because version IDs are represented in contracts, but retained analysis enforcement is deferred.

DTM-WP-010, DTM-WP-013, DTM-WP-014, and DTM-WP-015 remain deferred.

---

# Gates Addressed

004-B satisfies or prepares:

- documentation authority gate
- terminology drift gate
- domain compatibility gate
- analysis scope gate foundation
- transcript version basis gate foundation
- evidence linkage gate foundation
- hypothesis boundary gate foundation
- support-level separation gate
- safety posture gate foundation
- reflection point gate foundation
- corpus scope gate foundation
- report scope gate foundation
- regression gate foundation

Behavioral enforcement remains for later subgroups.

---

# Tests / Verification

004-B adds:

```text
tests/test_domain_concept_contracts.py
```

The tests cover:

- runtime alias preservation
- legacy/current term mapping
- explicit `AnalysisScope` behavior
- separation between support level and `Confidence`
- safety posture override detection
- non-prescriptive `ReflectionPoint` default
- corpus longitudinal-basis distinction
- `ReportScope` boundary/validation visibility
- alias construction through `ReflectionRun`

Runtime test execution was not performed in this chat because work was completed through repository edits and GitHub Actions remain intentionally disabled.

---

# Deferred / Not Touched

004-B does not touch:

- existing domain class definitions except package exports
- database models
- Alembic migrations
- API schemas or routes
- services
- prompt compiler
- validators
- report renderer
- UI
- export behavior
- corpus retrieval
- cost-state behavior
- deployment
- GitHub Actions
- production data

---

# Handoff to 004-C

004-C should proceed to lifecycle, retention, SourceArtifact, and deletion-cascade foundation work.

It should use 004-B contracts only as additive compatibility surfaces.

Relevant foundations:

```text
backend/domain/concept_contracts.py
docs/domain/README.md
docs/planning/architecture/004b_domain_terminology_compatibility_concept_contract_implementation.md
docs/planning/inventories/004b_domain_contract_surface_inventory.md
docs/planning/inventories/004b_domain_compatibility_gate_checklist.md
```

Expected 004-C posture:

```text
lifecycle/retention foundation first
no production data migration without explicit gate
no deletion cascade behavior without tests/gates
no broad rewrite
```

---

# Exit Criteria

004-B is complete when:

- domain concept compatibility contracts exist
- concept-safe aliases exist
- package exports are available
- domain terminology guide exists
- implementation record exists
- surface inventory exists
- gate checklist exists
- tests exist for the compatibility foundation
- living indexes show 004-B complete and 004-C next
- broad rewrite remains blocked

All criteria are satisfied.

---

# Next Phase

Proceed to:

```text
004-C — Lifecycle, Retention, SourceArtifact, and Deletion-Cascade Foundation
```
