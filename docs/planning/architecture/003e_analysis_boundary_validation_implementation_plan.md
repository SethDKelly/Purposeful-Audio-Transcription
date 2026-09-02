# 003-E Analysis Boundary / Validation Implementation Plan

## Status

Accepted as the Phase 003-E analysis boundary and validation implementation plan.

This document converts the accepted Phase 002 analysis-boundary architecture into implementation-ready work packages and gates.

It does not implement code changes, schema migrations, prompt rewrites, validator changes, report renderer changes, graph storage changes, evaluation fixtures, UI changes, export changes, deployment changes, or production data migrations by itself.

---

# Purpose

Prepare analysis-boundary and validation implementation work so later implementation can enforce evidence-limited reflection before broader corpus reasoning, hypothesis handling, report retention, export, and automation expand.

003-E turns the accepted analysis architecture into staged implementation planning for:

- explicit analysis scope
- transcript-version-bound evidence use
- reflection lens contracts
- bounded psychological hypothesis handling
- hypothesis support assessment
- structured safety posture
- corpus pattern assessment
- confidence and support-level separation
- reflection point replacement of recommendations/interventions
- reasoning graph boundary rules
- prompt construction boundaries
- model-output validation gates
- report/export readiness checks
- evaluation fixtures and regression gates

---

# Governing Inputs

Primary authority:

- `docs/concepts/015_hypothesis_reflection_boundary.md`
- `docs/concepts/016_therapeutic_lens_language_decision.md`
- `docs/concepts/017_safety_boundary_decision.md`
- `docs/planning/architecture/002e_analysis_boundary_hypothesis_safety_architecture_plan.md`
- `docs/planning/inventories/002e_analysis_boundary_contracts.md`
- `docs/planning/inventories/002e_validation_gate_matrix.md`
- `docs/planning/inventories/002d_corpus_reasoning_scope_rules.md`
- `docs/planning/architecture/003b_domain_terminology_concept_mapping_implementation_plan.md`
- `docs/planning/architecture/003c_data_lifecycle_retention_foundation_implementation_plan.md`
- `docs/planning/architecture/003d_privacy_boundary_encryption_baseline_implementation_plan.md`

Implementation reference inspected:

- `backend/core/module_registry.py`
- `backend/domain/enums.py`
- `backend/domain/finding.py`
- `backend/domain/synthesis.py`
- `backend/domain/workflow.py`
- `backend/schemas/module_output_v1.py`
- `backend/services/prompt_compiler.py`
- `backend/services/module_runner.py`
- `backend/services/module_output_validator.py`
- `backend/services/output_parser.py`
- `backend/services/safety_validator.py`
- `backend/services/safety_policy.py`
- `backend/services/workflow_engine.py`
- `backend/services/structured_graph_service.py`
- `backend/services/graph_merge_service.py`
- `backend/services/longitudinal_synthesis_service.py`
- `config/framework/shared_instructions.md`
- `config/framework/output_schema_instructions.md`
- `config/modules/`
- `config/prompts/`
- `config/safety_policy.yaml`

---

# Accepted Analysis Principle

```text
Analysis boundaries must be enforceable through scope, schemas, validators, graph rules, report rendering, and evaluation fixtures, not only through prompt wording.
```

The system may use therapeutic, psychological, behavioral, cognitive, relational, attachment-informed, trauma-informed, and diagnostic-framework-informed concepts as evidence-limited reasoning references.

It must not diagnose, label, adjudicate, prove hidden intent, present treatment authority, use a single conversation as proof of a stable trait, silently perform account-wide corpus reasoning, or mutualize serious safety concerns.

---

# Current Implementation Baseline

The prototype already has useful analysis-boundary foundations:

1. Module definitions include lens-like metadata: primary lens, analytical level, unit of analysis, inference depth, confidence ceiling, expected constructs, output schema, dependencies, and prompt files.
2. Prompt compilation injects shared framework instructions, module role, validation requirements, evidence index, confidence ceiling, and optional safety-mode overlays.
3. Shared analytical framework rules already require evidence-first reasoning, quote IDs, small evidence spans, observation/interpretation separation, confidence labels, alternatives, limitations, and boundary language.
4. Module output schema already requires structured findings, constructs, relationships, recommendations, limitations, and optional raw markdown.
5. Output parsing extracts JSON, normalizes common aliases, coerces enums, generates default IDs, and inserts a default alternative explanation for inferred findings when omitted.
6. Module output validation checks module/version consistency, executive summary presence, finding evidence, quote ID validity, confidence ceilings, evidence item limits, paragraph-length evidence warnings, construct coverage, relationship rationale, and alternatives for inferred claims.
7. Safety validation checks generated text for diagnostic/clinical labeling, definitive abuse/manipulation labels, legal/medical determinations, outcome prediction, intent-as-fact language, trauma/attachment determinations, mutualization, and reconciliation pressure.
8. Safety policy can suppress exploratory psychological and narrative modules and modify selected modules when safety mode is active.
9. Workflow execution persists transcript-version identity on workflow runs and uses transcript-version-aware bundles for module execution when available.
10. Structured graph services provide normalized findings, constructs, relationships, quote IDs, and compact synthesis handoffs.
11. Graph merge/convergence logic already attempts to merge duplicate constructs and preserve evidence quote references.
12. Longitudinal synthesis already requires at least two case transcripts with completed runs and includes transcript IDs, labels, dates, workflow run IDs, transcript version IDs, structured inventories, and guidance for recurrence claims.

The baseline is useful, but incomplete for the accepted concept model.

Current gaps and risks:

- no first-class `AnalysisScope` object declares single-transcript, selected-transcript-set, case-corpus, or future workspace-corpus scope before execution
- module definitions are not yet explicit `ReflectionLensContract` records with forbidden claims, source-framework authority boundaries, safety behavior, and output object expectations
- `FindingType.HYPOTHESIS` is still an ordinary finding type rather than a bounded `PsychologicalHypothesis` plus `HypothesisSupportAssessment`
- `recommendations` and `interventions` remain in schemas and reports instead of product-safe `ReflectionPoint` semantics
- `safety_mode` is still mostly a boolean and safety flags are string lists, not structured `SafetyPosture`
- corpus reasoning exists in longitudinal synthesis but lacks a reusable `CorpusPatternAssessment` contract, scope object, stale/deleted evidence controls, and duplicate-evidence safeguards
- report/export readiness is not yet represented as a validation result tied to scope, version basis, and safety posture
- validators catch important text patterns but do not yet provide a unified `AnalysisValidationResult` across module, synthesis, report, corpus, and export outputs
- prompt repair currently includes raw output in the follow-up context; later privacy work should review whether this is acceptable or should be minimized/hashed/redacted by validator category
- generated validation errors and warnings need a content-free event/log posture coordinated with 003-D

---

# Accepted Implementation Principle

```text
No analysis output should be displayed, retained, exported, or reused as corpus evidence until it passes explicit boundary validation for its declared scope.
```

Prompt instructions are necessary but not sufficient.

Validators, schemas, report rendering, corpus handoffs, graph edges, and evaluation fixtures must enforce the same boundary.

---

# Implementation Planning Decisions

## 1. AnalysisScope should precede prompt construction

Later implementation should define an `AnalysisScope` or equivalent contract before the prompt compiler assembles evidence.

Minimum scope types:

```text
single_transcript_version
selected_transcript_set
case_evidence_corpus
future_explicit_workspace_corpus
```

The scope must include owner, transcript version IDs, excluded versions, case ID when applicable, requested lens IDs, analysis purpose, user-provided context, user-provided hypotheses, retention/privacy posture, and corpus eligibility.

Default rule:

```text
Do not silently analyze all retained account transcripts.
```

## 2. ReflectionLensContract should wrap legacy module metadata

Current module YAML and `ModuleConfig` are useful foundations.

Later implementation should add a compatibility layer or extended config that represents each module as a `ReflectionLensContract`.

Required additions:

- product-facing lens name
- lens family
- source-framework references
- permitted inference depth
- confidence ceiling
- evidence requirements
- whether corpus reasoning is supported
- whether hypothesis output is supported
- safety behavior
- forbidden claims
- required limitations
- expected output object types

Implementation may keep module IDs internally while exposing reflection-lens language externally.

## 3. Hypothesis handling should split from ordinary findings

A hypothesis should not be just a `FindingType.HYPOTHESIS` row.

Later implementation should split or wrap hypothesis output into:

```text
PsychologicalHypothesis
HypothesisSupportAssessment
```

This preserves evidence for, evidence against, missing evidence, alternatives, support level, confidence, inference depth, source, safety considerations, and non-diagnostic boundary text.

Support level must remain separate from confidence.

## 4. User-provided diagnosis or hypothesis must remain context, not validation target

User-provided diagnostic language may be used as context for cautious hypothesis support analysis.

The system must not say a transcript confirms, proves, rules in, rules out, clinically establishes, detects, or diagnoses a condition.

Acceptable outputs use support levels such as:

```text
consistent_with_hypothesis
partially_consistent_with_hypothesis
contradicts_hypothesis
insufficient_evidence
alternative_explanation_likely
```

## 5. SafetyPosture should become structured and upstream

Current safety mode and safety flags are useful foundations.

Later implementation should define structured `SafetyPosture` before or during analysis and use it to modify:

- allowed lenses
- prompt overlays
- report order
- reflection-point generation
- hypothesis framing
- corpus summary language
- export readiness
- validation strictness

Suggested posture values:

```text
none_detected
elevated_caution
high_risk
immediate_or_crisis_indicators
```

These are output-framing states, not legal or clinical determinations.

## 6. ReflectionPoint should replace recommendation/intervention semantics

Legacy `recommendations` and `interventions` can remain temporarily for compatibility.

Later implementation should add or map to `ReflectionPoint` objects that are:

- evidence-linked
- non-prescriptive
- self-review oriented
- safety-aware
- bounded by limitations
- not treatment instructions
- not confrontation or reconciliation pressure in high-risk contexts

## 7. CorpusPatternAssessment should govern multi-transcript claims

Longitudinal synthesis is valuable, but corpus reasoning needs a reusable contract.

A `CorpusPatternAssessment` should distinguish:

```text
recurrence
contradiction
strengthening
weakening
context_split
temporal_change
insufficient_corpus_evidence
```

Corpus claims must preserve case/selected scope, transcript version IDs, quote IDs, contradictions, limitations, and staleness status.

Prior model conclusions are not evidence.

## 8. Reasoning graph edges need boundary-aware vocabulary

Graph relationships should distinguish evidence support from causal, motive, identity, recommendation, and corpus recurrence claims.

Causal or motive-like relationships require stricter confidence ceilings and alternative explanations.

Later implementation should add or map edge types for:

```text
supports
partially_supports
contradicts
alternative_to
recurs_across
strengthens
weakens
contextualizes
requires_safety_override
limited_by
```

## 9. AnalysisValidationResult should become the central gate record

Module validation, safety validation, report validation, corpus validation, and export validation should eventually feed a unified result object.

The object should identify:

- run ID
- scope ID
- validator version
- passed/failed status
- critical failures
- warnings
- blocked output sections
- required revisions
- content-free event metadata

## 10. Report and export readiness must be validation surfaces

Reports and exports should not only render whatever module outputs produce.

They must verify:

- declared report scope
- transcript version basis
- evidence linkage
- safety posture
- hypothesis support boundaries
- corpus lineage
- confidence limitations
- no forbidden diagnosis/treatment/adjudication language
- export source/version metadata

---

# Proposed Implementation Sequence

## Stage 0 — Analysis authority lock

Create implementation-facing documentation that points developers to current analysis-boundary authority.

Do not change runtime behavior yet.

## Stage 1 — Surface inventory and compatibility map

Inventory module configs, prompt templates, output schemas, parser aliases, validators, safety policy, synthesis reports, graph relationships, and longitudinal synthesis outputs against accepted contracts.

## Stage 2 — AnalysisScope design

Define exact representation for analysis scope and how it is passed through route, workflow, prompt compiler, module runner, report, export, graph, and corpus layers.

## Stage 3 — ReflectionLensContract design

Add a compatibility plan for module-to-lens mapping before changing module YAML or public UI labels.

## Stage 4 — Validator unification plan

Define `AnalysisValidationResult` as a logical umbrella over existing module output, safety, corpus, report, and export validation.

## Stage 5 — Hypothesis and support-level plan

Define bounded hypothesis and support assessment objects, including migration from `FindingType.HYPOTHESIS` and report `exploratory_hypotheses`.

## Stage 6 — SafetyPosture plan

Define structured safety posture and how it drives module suppression, prompt overlays, report sections, reflection points, and stricter validation.

## Stage 7 — ReflectionPoint plan

Define mapping from legacy recommendations/interventions to reflection points with safety constraints.

## Stage 8 — Corpus validation plan

Define corpus pattern assessment, recurrence thresholds, contradiction handling, duplicate-evidence controls, owner/scope/version enforcement, and staleness handling.

## Stage 9 — Report/export validation plan

Define report scope and export-readiness validators before report/export expansion.

## Stage 10 — Evaluation fixture plan

Define golden fixtures for diagnostic overreach, user-provided diagnosis, hidden intent, safety mutualization, high-risk reconciliation pressure, evidence-less claims, corpus overreach, stale evidence, and reflection-point safety.

---

# Required Gates

003-E carries forward or introduces these gates for later implementation:

- analysis scope gate
- transcript version basis gate
- evidence linkage gate
- reflection lens contract gate
- hypothesis boundary gate
- support-level separation gate
- user-provided diagnosis handling gate
- safety posture gate
- safety override gate
- reflection point gate
- corpus reasoning gate
- corpus staleness gate
- reasoning graph boundary gate
- prompt boundary gate
- report scope gate
- export readiness gate
- log redaction gate
- privacy boundary gate
- evaluation gate
- regression gate

---

# Handoff to 003-F

003-F should use this plan to prepare cost-state and control-plane implementation planning without confusing operational state with analysis state.

Cost-state shutdown, worker recovery, retries, cancellation, and queued jobs must not corrupt:

- analysis scope
- transcript version basis
- in-flight validation state
- safety posture
- corpus scope
- retained graph/report claims
- deletion/corpus staleness propagation
- content-free validation events

---

# Handoff to 003-G

003-G should use this plan to align UI/report implementation with:

- explicit evidence scope display
- single-transcript vs case-corpus report labeling
- hypothesis support labels
- safety posture language
- reflection-point wording
- corpus recurrence/contradiction/change language
- validation failure/warning display
- export-readiness language

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

# Acceptance Result

The analysis boundary and validation implementation plan is ready to feed 003-F, 003-G, and the Phase 003 exit review.

Proceed next to:

```text
003-F — Cost-State Control Plane Implementation Plan
```
