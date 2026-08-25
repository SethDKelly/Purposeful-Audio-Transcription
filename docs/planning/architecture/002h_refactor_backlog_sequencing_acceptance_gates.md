# 002-H Refactor Backlog, Sequencing, and Acceptance Gates

## Status

Accepted as the Phase 002-H refactor backlog, sequencing, and acceptance-gate plan.

This document converts the Phase 002 concept-to-architecture work into an implementation-ready planning structure for later phases.

It does not authorize code, schema, infrastructure, prompt, UI, deployment, or pipeline changes by itself.

---

# Purpose

Define the backlog structure, implementation sequencing, and acceptance gates needed before the project moves from concept-to-architecture planning into implementation refactoring.

002-H is the bridge between architecture planning and the mandatory 002-I exit review.

It consolidates implementation work implied by:

- documentation authority and terminology inventory
- concept-to-domain mapping
- data lifecycle and retention architecture
- privacy boundary and encryption architecture
- analysis boundary, hypothesis, and safety architecture
- cost state and personal deployment architecture
- UI/UX concept alignment

---

# Accepted Refactor Principle

```text
Refactor concept-first, preserve useful prototype structure, and gate implementation by privacy, evidence, safety, retention, and cost-state correctness.
```

The current implementation should not be discarded wholesale.

However, it must no longer define product authority.

---

# Architecture Decision Summary

## 1. Implementation refactoring should proceed in controlled waves

The project should not jump directly into broad UI, backend, deployment, prompt, and schema changes at once.

Refactoring should proceed in waves that preserve a usable system and protect sensitive data.

## 2. Documentation authority cleanup comes first

Before implementation changes, stale authority surfaces must be marked, reconciled, or replaced so old v2.1 or prototype assumptions do not drive code changes.

## 3. Domain and schema work should precede prompt/report/UI work

The accepted concepts require stable representations for lifecycle, retention, evidence scope, privacy boundary, hypotheses, safety posture, corpus reasoning, and cost state.

Prompt, report, and UI changes should depend on those semantics rather than inventing local wording.

## 4. Privacy and retention gates block unsafe implementation

No implementation phase should retain more content, widen corpus scope, restore logs, or introduce exports without passing privacy, retention, and deletion gates.

## 5. Analysis gates must be enforceable beyond prompting

Non-diagnostic discipline, safety-aware override, evidence linkage, corpus scope, confidence calibration, and reflection-point semantics must be supported by schemas, validators, report rendering, and evaluation fixtures.

## 6. Cost-state work must not corrupt jobs or analysis semantics

Sleep/wake behavior must remain a control-plane concern.

It must not change transcript, evidence, report, hypothesis, case, corpus, or graph meanings.

## 7. UI/UX work should follow concept language and expose scope

UI and report surfaces should make evidence scope, retention state, safety posture, corpus use, export boundaries, and cost state visible without product authority drift.

## 8. 002-I must authorize or block Phase 003

002-H prepares a candidate implementation sequence.

The next subgroup, 002-I, must decide whether the project is ready to enter implementation refactoring and name the authorized Phase 003 scope.

---

# Recommended Implementation Wave Sequence

## Wave 0 — Pre-implementation authority lock

Purpose:

Prevent stale documentation, legacy workflow assumptions, or ambiguous product framing from guiding implementation.

Candidate work:

- mark older v2.1 planning docs as reference or superseded where appropriate
- update living indexes and root-level authority references
- ensure `docs/concepts/` and Phase 002 architecture docs are cited as current authority
- add a design-authority note to implementation planning docs
- define no-implementation-until-authorized warning for Phase 002 outputs

Primary gate:

```text
documentation_authority_gate
```

## Wave 1 — Domain terminology and aggregate alignment

Purpose:

Align code-facing concepts with accepted domain semantics without necessarily renaming every implementation artifact immediately.

Candidate work:

- map `WorkflowRun` to product `ReflectionRun`
- map `ModuleDefinition` / modules to product `ReflectionLens`
- clarify whether `Transcript` remains the practical aggregate root
- add concept mappings in domain docs or code comments where useful
- preserve existing useful `TranscriptVersion`, `EvidenceQuote`, `Finding`, `Case`, and graph structures

Primary gates:

```text
domain_mapping_gate
terminology_drift_gate
```

## Wave 2 — Data lifecycle and retention foundation

Purpose:

Make lifecycle behavior explicit before adding deeper corpus and reporting behavior.

Candidate work:

- add or map `SourceArtifact` / `RecordingArtifact`
- add or map `RetentionRule` semantics
- add artifact lifecycle events without sensitive content
- implement or plan purge workers for recordings, transcription artifacts, drafts, exports, and deletion cascades
- ensure transcript drafts, saved transcripts, transcript versions, evidence, reports, cases, and exports have retention semantics

Primary gates:

```text
retention_gate
deletion_cascade_gate
lifecycle_event_redaction_gate
```

## Wave 3 — Privacy boundary and encryption baseline

Purpose:

Protect retained sensitive artifacts before expanding analysis, exports, corpus use, or UI surface area.

Candidate work:

- owner-scope retained sensitive artifacts
- enforce service-purpose access boundaries
- verify infrastructure encryption posture
- plan application-level / field-level encryption for mature personal mode
- ensure logs and telemetry remain content-free
- define export encryption/retention posture
- confirm corpus summaries and graph objects are sensitive retained content

Primary gates:

```text
privacy_boundary_gate
encryption_baseline_gate
log_redaction_gate
export_boundary_gate
```

## Wave 4 — Analysis boundary, hypothesis, safety, and corpus reasoning

Purpose:

Convert analysis principles into enforceable schemas, prompts, validators, report rendering, and evaluation fixtures.

Candidate work:

- add or map `AnalysisScope`
- add or map `ReflectionLensContract`
- add or map `PsychologicalHypothesis`
- add or map `HypothesisSupportAssessment`
- add or map `SafetyPosture`
- add or map `ReflectionPoint`
- add or map `CorpusPatternAssessment`
- implement validation gates for evidence linkage, scope, diagnosis prohibition, safety override, corpus overreach, confidence calibration, and report language
- ensure prior model conclusions are not treated as evidence

Primary gates:

```text
analysis_boundary_gate
hypothesis_boundary_gate
safety_override_gate
corpus_reasoning_gate
validation_gate
```

## Wave 5 — Cost state and personal deployment control plane

Purpose:

Restore or redesign low-cost personal-mode operation without relying on deleted legacy workflows.

Candidate work:

- add or map `CostStateRecord`
- add or map `BlockingJobRecord`
- define wake/sleep control surface
- define idle evaluator
- define safe shutdown coordinator
- define failed wake and maintenance states
- add non-content operational lifecycle events
- decide whether GitHub Actions, scripts, cloud automation, or another mechanism should implement sleep/wake later

Primary gates:

```text
cost_state_gate
job_safe_shutdown_gate
workflow_replacement_gate
```

## Wave 6 — UI/UX and report alignment

Purpose:

Make user-facing surfaces reflect the accepted concepts and architecture.

Candidate work:

- replace product framing that makes the app look like only audio transcription
- expose analysis scope on setup and reports
- make case evidence corpus visible
- display transcript version and evidence quote basis
- add hypothesis/support/alternatives/limitations sections
- add safety posture behavior
- replace recommendation/intervention wording with reflection-point semantics
- expose retention, deletion, export, and cost-state behavior

Primary gates:

```text
ui_language_gate
report_scope_gate
retention_visibility_gate
safety_ux_gate
cost_state_ux_gate
```

## Wave 7 — Evaluation, fixtures, and regression gates

Purpose:

Ensure implementation changes preserve the concept foundation.

Candidate work:

- add evaluation fixtures for non-diagnostic output
- add safety-aware override fixtures
- add corpus reasoning fixtures
- add retention/deletion cascade tests
- add log redaction checks
- add report language checks
- add cost-state transition and blocking-job tests
- add export-boundary checks

Primary gates:

```text
evaluation_gate
regression_gate
release_readiness_gate
```

---

# Candidate Phase 003 Shape

002-H recommends that Phase 003 should not be a broad rewrite.

Candidate next numbered phase after 002-I:

```text
Phase 003 — Foundation Refactor Planning and Authority Cleanup
```

Potential Phase 003 groups:

```text
003-A — Documentation Authority Cleanup and Historical Material Reconciliation
003-B — Domain Terminology and Concept Mapping Implementation Plan
003-C — Data Lifecycle / Retention Foundation Implementation Plan
003-D — Privacy Boundary / Encryption Baseline Implementation Plan
003-E — Analysis Boundary / Validation Implementation Plan
003-F — Cost-State Control Plane Implementation Plan
003-G — UI/Report Alignment Implementation Plan
003-H — Phase 003 Exit Review and Consolidation
```

002-I may accept, modify, or replace this candidate sequence.

---

# Backlog Classification

Use these classifications in the detailed backlog.

| Classification | Meaning |
|---|---|
| `P0` | Blocks implementation refactor safety or authority |
| `P1` | Required for coherent concept-to-architecture implementation |
| `P2` | Useful but can be deferred with tracking |
| `Decision` | Requires design decision before implementation |
| `Implementation` | Build/change task after authorization |
| `Validation` | Test, evaluation, or gate task |
| `Documentation` | Authority, terminology, or docs task |
| `Security` | Privacy, encryption, access, logging, retention, or export task |
| `UX` | User-facing language, flow, or report task |
| `Operations` | Cost state, deployment, wake/sleep, job safety, or monitoring task |

---

# Acceptance Gate Categories

The following gates should be used by 002-I and later implementation phases.

1. Documentation authority gate
2. Terminology drift gate
3. Domain mapping gate
4. Retention gate
5. Deletion cascade gate
6. Privacy boundary gate
7. Encryption baseline gate
8. Log redaction gate
9. Export boundary gate
10. Analysis boundary gate
11. Hypothesis boundary gate
12. Safety override gate
13. Corpus reasoning gate
14. Reflection point gate
15. Report scope gate
16. UI language gate
17. Cost state gate
18. Job-safe shutdown gate
19. Workflow replacement gate
20. Evaluation/regression gate

---

# Phase 002-H Decision

The project has enough concept-to-architecture material to build a refactor backlog and candidate implementation sequence.

The project should still not begin implementation refactoring until 002-I completes the exit review and explicitly authorizes the next numbered phase.

---

# Handoff to 002-I

002-I should consolidate:

- accepted decisions from 002-A through 002-H
- unresolved decisions and deferrals
- stale/superseded documentation list
- recommended Phase 003 scope
- implementation readiness result
- mandatory gates for the next phase

002-I should either:

```text
authorize Phase 003 with explicit scope
```

or:

```text
block implementation and require additional planning
```

---

# Non-goals

002-H does not implement:

- code changes
- schema migrations
- prompt rewrites
- UI changes
- deployment changes
- GitHub Actions restoration
- tests or evaluations
- encryption changes
- data migrations

Implementation remains blocked until Phase 002-I exit review authorizes the next phase.
