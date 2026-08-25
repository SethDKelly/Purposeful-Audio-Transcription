# Concept Design Foundation

## Purpose

This folder is the new conceptual design foundation for the conversation analysis application.

The application began from a plausible product idea and then moved quickly into implementation. That produced useful code, but implementation details began to become the design authority.

This folder resets the design from ground zero.

## Design Method

The documents use a concept-design approach inspired by Daniel Jackson’s software design work:

- identify the concepts users and designers must understand
- give each concept a clear purpose
- define each concept’s operational principle
- describe how concepts compose
- identify tensions, misfits, and invariants
- only then map concepts back to implementation

## Core Premise

The application is a secure conversation analysis and reflection system.

It analyzes transcripts, which may be derived from recordings, using evidence-based psychological, behavioral, therapeutic, cognitive, and relational lenses. It supports reflection and longitudinal understanding.

The application may consider psychological or diagnostic hypotheses as reflection contexts, but it must not diagnose, label, adjudicate, or claim clinical certainty.

## Foundation Read Order

1. `000_concept_reset_charter.md`
2. `001_product_premise.md`
3. `002_concept_design_method.md`
4. `003_concept_catalog.md`
5. `004_concept_composition.md`
6. `005_security_privacy_retention_concepts.md`
7. `006_cost_availability_concepts.md`
8. `007_analysis_philosophy.md`
9. `008_future_enterprise_transition.md`
10. `009_refactor_mapping.md`
11. `010_open_questions.md`

## Phase 001 Decision Closure

Phase 001 converts concept exploration into accepted design authority.

| Subphase | Status | Decision Docs |
|---|---|---|
| 001-A — Product Identity, Naming, and Conceptual Boundary | Accepted | `011_product_identity_decision.md`, `012_concept_boundary_decision.md` |
| 001-B — Data Lifecycle, Retention, and Encryption Decisions | Accepted | `013_data_lifecycle_decision.md`, `014_retention_and_encryption_decision.md` |
| 001-C — Hypothesis-Aware Reflection and Non-Diagnostic Boundary | Accepted | `015_hypothesis_reflection_boundary.md`, `016_therapeutic_lens_language_decision.md`, `017_safety_boundary_decision.md` |
| 001-D — Personal Operating Model, User Role, and Cost State | Accepted | `018_personal_operating_model_decision.md`, `019_cost_state_decision.md`, `020_future_enterprise_posture_decision.md` |
| 001-E — Concept Acceptance and Refactor Readiness | Complete | `021_concept_acceptance_summary.md`, `022_refactor_readiness_decision.md` |

## Current Working Identity

```text
Secure Conversation Analysis and Reflection System
```

## Name Roles

| Name | Role |
|---|---|
| Purposeful Audio Transcription | Historical repository name / legacy shell |
| Relationship Reasoning Engine (RRE) | Internal analysis-engine identity |
| Secure Conversation Analysis and Reflection System | Current concept-level product identity |
| Audio transcription | Input capability, not product identity |

## Current Lifecycle Defaults

| Artifact | Default |
|---|---|
| Audio recording | Ephemeral; delete after successful transcription |
| Failed transcription audio | Short retry/debug TTL; max 24 hours |
| Transcript draft | Temporary; recommended 7-day expiration unless saved/promoted |
| Saved transcript | Durable until user deletion |
| Case transcript | Durable; case assignment implies retention |
| Analysis output | Inherits retention from evidence basis |
| Export | Explicit user action; download-oriented by default |

## Current Analysis Boundary Defaults

| Area | Decision |
|---|---|
| Psychological hypotheses | Allowed as evidence-limited reflection contexts |
| User-provided diagnoses | Context only; never validated or diagnosed by the system |
| Therapeutic concepts | Framed as therapeutic reflection lenses |
| Diagnostic-framework-informed concepts | Allowed as reasoning references, not clinical authority |
| CBT/DBT/psychodynamic concepts | Allowed for reflection, not treatment or clinical authority |
| Diagnosis / labeling | Out of scope |
| Intent as fact | Out of scope unless directly evidenced |
| Safety-aware framing | Overrides ordinary coaching and mutual-improvement framing |

## Current Operating Defaults

| Area | Decision |
|---|---|
| User model | Personal owner/operator |
| Administrator | Same person as owner in near-term mode |
| Data owner | Same person as owner in near-term mode |
| Cost operator | Same person as owner in near-term mode |
| Cost state | First-class personal-mode concept |
| Availability posture | Aggressive sleep/wake for personal mode |
| Enterprise | Future policy/deployment layer |

## Accepted Concept Authority

The intended authority order is:

```text
Concept design
→ Product philosophy
→ Domain model
→ Security/privacy model
→ Analysis philosophy
→ Implementation architecture
→ Code
```

## Next Phase

Proceed to:

```text
Phase 002 — Concept-to-Architecture Refactor Roadmap
```

Phase 002 should map accepted concepts to the current implementation before code refactoring begins.
