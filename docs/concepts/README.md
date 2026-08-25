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

## Read Order

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
| 001-C — Hypothesis-Aware Reflection and Non-Diagnostic Boundary | Next | TBD |
| 001-D — Personal Operating Model, User Role, and Cost State | Planned | TBD |
| 001-E — Concept Acceptance and Refactor Readiness | Planned | TBD |

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

## Design Authority

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
