# 004-B Domain Contract Surface Inventory

## Status

Accepted as the Phase 004-B domain contract surface inventory.

---

# Purpose

Record the code and documentation surfaces created or affected by the 004-B compatibility implementation.

This inventory supports later Phase 004 subgroups so they can use concept-safe contracts without reintroducing destructive rename pressure.

---

# Implementation Surfaces

| Surface | Status | Role | Notes |
|---|---|---|---|
| `backend/domain/concept_contracts.py` | Added | Runtime compatibility and concept contract surface | New additive module; no persisted schema change |
| `backend/domain/__init__.py` | Updated | Package export surface | Re-exports concept contracts and aliases through package namespace |
| `tests/test_domain_concept_contracts.py` | Added | Regression/contract tests | Verifies aliases, mappings, scope, support/confidence separation, safety posture, reflection point, corpus, report scope |
| `docs/domain/README.md` | Added | Implementation-facing domain glossary | Compact guide for developers/agents |
| `docs/planning/architecture/004b_domain_terminology_compatibility_concept_contract_implementation.md` | Added | 004-B implementation record | Captures header, gates, decisions, compatibility, deferred work |
| `docs/planning/inventories/004b_domain_contract_surface_inventory.md` | Added | This inventory | Records affected implementation and documentation surfaces |
| `docs/planning/inventories/004b_domain_compatibility_gate_checklist.md` | Added | Gate verification checklist | Defines minimum checks for this and later domain compatibility work |
| `docs/planning/phases/004b_domain_terminology_compatibility_concept_contract_implementation.md` | Added | Subgroup completion summary | Records 004-B closure and 004-C handoff |

---

# Alias Surface

Runtime aliases created in `backend/domain/concept_contracts.py`:

| Alias | Existing class | Purpose |
|---|---|---|
| `ReflectionRun` | `WorkflowRun` | Concept-safe name for analysis execution over declared evidence scope |
| `ReflectionLens` | `ModuleDefinition` | Concept-safe name for lens/module definition compatibility |
| `LensExecution` | `ModuleRun` | Concept-safe name for module run / lens execution |
| `ReflectionReport` | `SynthesisReport` | Concept-safe name for integrated report output |
| `CaseEvidenceCorpus` | `CaseDetail` | Concept-safe name for retained case/corpus boundary |

---

# Contract Surface

Runtime contracts created:

| Contract | Purpose | Later subgroup likely to use it |
|---|---|---|
| `DomainTermMapping` | Maps legacy/current terms to accepted concept terms | 004-B, 004-H, later audits |
| `AnalysisScope` | Declares evidence basis before analysis/report/corpus use | 004-E, 004-G |
| `ReflectionLensContract` | Wraps module definitions with concept-safe lens metadata | 004-E, 004-G |
| `HypothesisSupportAssessment` | Separates hypothesis relation from evidence confidence | 004-E, 004-G |
| `PsychologicalHypothesis` | Separates bounded hypothesis from ordinary finding/diagnosis | 004-E, 004-G |
| `SafetyPosture` | Structured safety posture for behavior/report/UI | 004-E, 004-F, 004-G |
| `ReflectionPoint` | Product-safe replacement target for recommendation/intervention language | 004-E, 004-G |
| `CorpusPatternAssessment` | Multi-transcript pattern contract with version/quote lineage | 004-E, 004-G |
| `ReportScope` | Report scope/header contract for validation, safety, staleness, export readiness | 004-E, 004-G |

---

# Enum Surface

Runtime enums created:

| Enum | Purpose |
|---|---|
| `CompatibilityPosture` | Classifies retain/harden/alias/split/new/defer posture |
| `AnalysisScopeType` | Declares single transcript, selected set, case corpus, or future explicit workspace corpus |
| `HypothesisSupportLevel` | Distinguishes evidence relation to a hypothesis from confidence |
| `SafetyPostureLevel` | Encodes none/elevated/high-risk/immediate safety posture labels |
| `ValidationStatus` | Minimal validation-state vocabulary for concept contracts |

---

# Preserved Surfaces

004-B intentionally preserves these surfaces unchanged:

```text
backend/domain/enums.py
backend/domain/finding.py
backend/domain/workflow.py
backend/domain/synthesis.py
backend/domain/case.py
backend/domain/transcript.py
backend/api/*
backend/services/*
alembic/versions/*
frontend-react/*
config/*
```

Existing code remains implementation evidence and runtime behavior.

It is not yet physically renamed.

---

# Work Packages Executed

| Phase 003 package | 004-B result |
|---|---|
| DTM-WP-001 — Domain authority and glossary lock | Executed through `docs/domain/README.md` and contract mappings |
| DTM-WP-002 — Transcript aggregate decision record | Executed through `TRANSCRIPT_AGGREGATE_DECISION` and docs |
| DTM-WP-003 — TranscriptVersion and EvidenceQuote hardening plan | Not fully executed; version IDs represented in `AnalysisScope`, `CorpusPatternAssessment`, and `ReportScope` |
| DTM-WP-004 — ReflectionRun compatibility mapping | Executed through alias and mapping |
| DTM-WP-005 — ReflectionLens contract mapping | Executed through alias and `ReflectionLensContract` |
| DTM-WP-006 — Hypothesis separation plan | Foundation executed through `PsychologicalHypothesis` and `HypothesisSupportAssessment` |
| DTM-WP-007 — SafetyPosture migration plan | Foundation executed through `SafetyPosture` and `SafetyPostureLevel` |
| DTM-WP-008 — ReflectionPoint migration plan | Foundation executed through `ReflectionPoint` |
| DTM-WP-009 — Case Evidence Corpus mapping plan | Foundation executed through alias and `CorpusPatternAssessment` |
| DTM-WP-010 — Reasoning graph edge vocabulary expansion | Deferred |
| DTM-WP-011 — Confidence/support-level mapping | Executed through separate support and confidence enums |
| DTM-WP-012 — ReflectionReport compatibility mapping | Foundation executed through alias and `ReportScope` |
| DTM-WP-013 — API/DTO terminology audit | Deferred |
| DTM-WP-014 — Physical code rename decision | Deferred |
| DTM-WP-015 — Future enterprise naming reservation | Deferred |

---

# Gates Partially Prepared for Later Subgroups

004-B prepares but does not complete behavioral enforcement for:

- analysis scope gate
- transcript version basis gate
- evidence linkage gate
- hypothesis boundary gate
- safety posture gate
- reflection point gate
- corpus scope gate
- report scope gate
- export readiness gate
- UI terminology gate

Later subgroups must wire and test behavior before claiming these gates fully pass.

---

# Decision

The 004-B domain contract surface is additive, compatibility-preserving, and ready to support 004-C through 004-G.
