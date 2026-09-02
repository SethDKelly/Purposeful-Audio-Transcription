# 003-E — Analysis Boundary / Validation Implementation Plan

## Status

Complete.

This subgroup converts accepted analysis-boundary architecture into implementation-ready validation plans.

It does not implement code, schema migrations, prompt rewrites, validator changes, safety detection changes, report renderer changes, graph storage changes, corpus retrieval changes, export changes, UI changes, tests, deployment changes, or production data migrations.

---

# Purpose

003-E prepares analysis-boundary and validation work so later implementation can enforce evidence-limited reflection before expanding corpus reasoning, hypothesis handling, retained reports, exports, or automation.

It answers:

- Which analysis-boundary foundations already exist in the prototype?
- Where should `AnalysisScope` enter the execution flow?
- How should module definitions become product-safe `ReflectionLensContract` surfaces?
- How should psychological hypotheses split from ordinary findings?
- How should support levels remain distinct from confidence?
- How should safety posture become structured rather than a boolean?
- How should recommendations/interventions migrate toward `ReflectionPoint`?
- How should corpus-level reasoning preserve lineage, contradictions, recurrence thresholds, and staleness?
- How should validation results govern display, retention, export, and corpus reuse?

---

# Outputs

| Output | Document |
|---|---|
| Analysis boundary / validation implementation plan | `../architecture/003e_analysis_boundary_validation_implementation_plan.md` |
| Analysis validation surface matrix | `../inventories/003e_analysis_validation_surface_matrix.md` |
| Analysis validation work packages | `../inventories/003e_analysis_validation_work_packages.md` |
| Analysis validation gate checklist | `../inventories/003e_analysis_validation_gate_checklist.md` |

---

# Implementation Reference Reviewed

003-E reviewed the accepted Phase 002 analysis architecture, prior Phase 003 foundation plans, and current implementation references including:

```text
docs/planning/architecture/002e_analysis_boundary_hypothesis_safety_architecture_plan.md
docs/planning/inventories/002e_analysis_boundary_contracts.md
docs/planning/inventories/002e_validation_gate_matrix.md
docs/planning/architecture/003b_domain_terminology_concept_mapping_implementation_plan.md
docs/planning/architecture/003c_data_lifecycle_retention_foundation_implementation_plan.md
docs/planning/architecture/003d_privacy_boundary_encryption_baseline_implementation_plan.md
backend/core/module_registry.py
backend/domain/enums.py
backend/domain/finding.py
backend/domain/synthesis.py
backend/domain/workflow.py
backend/schemas/module_output_v1.py
backend/services/prompt_compiler.py
backend/services/module_runner.py
backend/services/module_output_validator.py
backend/services/output_parser.py
backend/services/safety_validator.py
backend/services/safety_policy.py
backend/services/workflow_engine.py
backend/services/structured_graph_service.py
backend/services/graph_merge_service.py
backend/services/longitudinal_synthesis_service.py
config/framework/shared_instructions.md
config/safety_policy.yaml
```

---

# Current Baseline Findings

The prototype already has useful analysis-boundary foundations:

- module metadata with lens-like fields, inference depth, and confidence ceiling
- shared framework rules for evidence-first reasoning, quote IDs, small spans, alternatives, limitations, and boundaries
- prompt compiler validation instructions and safety overlays
- structured module output schema
- output parser with JSON extraction, normalization, enum coercion, IDs, and default alternatives
- module output validator for evidence, quote IDs, confidence ceilings, evidence precision, construct coverage, and alternatives
- safety validator for diagnostic/clinical labeling, adjudicative abuse/manipulation labels, legal/medical claims, hidden intent, trauma/attachment determinations, mutualization, and reconciliation pressure
- safety policy-driven module suppression and modification
- workflow runs with transcript-version identity
- structured graph handoff and graph merge/convergence foundations
- case-level longitudinal synthesis requiring at least two transcripts and carrying transcript/run/version context

The prototype is not yet sufficient for the accepted analysis-boundary model because `AnalysisScope`, `ReflectionLensContract`, `PsychologicalHypothesis`, `HypothesisSupportAssessment`, `SafetyPosture`, `ReflectionPoint`, `CorpusPatternAssessment`, `AnalysisValidationResult`, `ReportScope`, and `ExportValidationResult` are not first-class enough.

---

# Accepted Decisions

## 1. Validation must be explicit and multi-layered

Prompting alone is not sufficient. Schemas, validators, report rendering, graph rules, corpus handoffs, export checks, and evaluation fixtures must enforce the same boundary.

## 2. AnalysisScope must precede prompt construction

Every retained analysis must declare its owner-scoped evidence basis before prompt construction.

## 3. ReflectionLensContract should wrap modules

Existing module definitions remain useful, but future implementation should expose product-safe reflection lens semantics.

## 4. Hypothesis support must split from diagnosis-like findings

Hypothesis support levels should be first-class and must not imply diagnosis, identity, or clinical certainty.

## 5. User-provided diagnosis remains context only

The system may compare transcript evidence to user-provided hypotheses, but must not confirm, rule in, rule out, detect, or diagnose a condition.

## 6. SafetyPosture should drive output behavior

Safety posture must influence enabled lenses, prompt overlays, report sections, reflection points, hypothesis framing, corpus language, export readiness, and validation strictness.

## 7. ReflectionPoint should replace recommendation/intervention semantics

Reflection points are evidence-linked, non-prescriptive, self-review oriented, safety-aware, and bounded by limitations.

## 8. CorpusPatternAssessment should govern multi-transcript claims

Corpus claims must preserve scope, transcript version IDs, quote IDs, contradictions, duplicate evidence controls, limitations, and staleness status.

## 9. Report/export readiness are validation surfaces

Reports and exports must verify scope, evidence, safety, hypothesis, corpus, confidence, limitations, and product-boundary language before display or export.

---

# Work Package Summary

003-E defines work packages for:

```text
ABV-WP-001 — AnalysisScope execution contract
ABV-WP-002 — Transcript-version and evidence-basis hardening
ABV-WP-003 — ReflectionLensContract compatibility plan
ABV-WP-004 — Unified AnalysisValidationResult plan
ABV-WP-005 — PsychologicalHypothesis and support assessment plan
ABV-WP-006 — SafetyPosture implementation plan
ABV-WP-007 — ReflectionPoint migration plan
ABV-WP-008 — CorpusPatternAssessment and corpus validation plan
ABV-WP-009 — Boundary-aware text validation plan
ABV-WP-010 — Prompt boundary and repair flow plan
ABV-WP-011 — ReportScope and report validation plan
ABV-WP-012 — Reasoning graph boundary vocabulary plan
ABV-WP-013 — Export readiness validation plan
ABV-WP-014 — Analysis validation test and fixture plan
ABV-WP-015 — UI validation state handoff
```

P2 decisions remain for advanced lens/source-framework registry, advanced corpus trend scoring, and future workspace corpus support.

---

# Gates Carried Forward

003-E carries forward these gates:

- analysis scope gate
- transcript version basis gate
- evidence linkage gate
- reflection lens contract gate
- hypothesis boundary gate
- support-level separation gate
- user-provided diagnosis handling gate
- diagnosis/labeling prohibition gate
- intent-as-fact gate
- therapeutic authority gate
- safety posture gate
- safety override gate
- reflection point gate
- corpus reasoning gate
- corpus scope gate
- corpus staleness gate
- reasoning graph boundary gate
- prompt boundary gate
- report scope gate
- report language gate
- export readiness gate
- privacy boundary gate
- log redaction gate
- evaluation gate
- regression gate
- release readiness gate

---

# Handoff to 003-F

003-F should prepare cost-state and control-plane implementation planning for queued/in-flight analysis, retries, cancellation, job-safe sleep, wake/resume, and shutdown behavior without corrupting analysis scope, transcript-version basis, safety posture, validation state, corpus scope, graph/report claims, or validation events.

---

# Handoff to 003-G

003-G should prepare UI/report implementation planning for displaying evidence scope, validation warnings, hypothesis support levels, safety posture, reflection points, corpus recurrence/change/contradiction language, and export-readiness boundaries.

---

# Non-goals

003-E does not implement:

- code changes
- schema migrations
- prompt rewrites
- validator logic changes
- safety detection changes
- report renderer changes
- graph storage changes
- corpus retrieval changes
- export changes
- UI changes
- tests
- deployment changes
- production data migration

---

# Exit Criteria

003-E is complete when:

- analysis-boundary implementation plan exists
- analysis validation surface matrix exists
- analysis validation work packages exist
- analysis validation gate checklist exists
- current implementation references are reviewed at planning level
- 003-F and 003-G handoffs are explicit
- Phase 003 indexes are updated
- broad implementation remains blocked

All criteria are satisfied.

---

# Next Phase

Proceed to:

```text
003-F — Cost-State Control Plane Implementation Plan
```
