# Concept Design Foundation

## Purpose

This folder is the conceptual design foundation for the conversation analysis application.

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

## What This Is

This is product philosophy, concept catalog, conceptual boundary, security/privacy model, cost/availability model, analysis philosophy, future enterprise transition framing, and refactor mapping.

## What This Is Not

This is not a sprint plan, feature checklist, clinical protocol, diagnostic framework, database schema spec, or code migration guide.

## Core Premise

The application is a secure conversation analysis and reflection system.

It analyzes transcripts, which may be derived from recordings, using evidence-based psychological, behavioral, therapeutic, cognitive, and relational lenses. It supports reflection and longitudinal understanding.

The application may consider psychological or diagnostic hypotheses as reflection contexts, but it must not diagnose, label, adjudicate, or claim clinical certainty.

---

# Active Decision Phase

The current concept-design phase is:

```text
Phase 001-A — Product Identity, Naming, and Conceptual Boundary
```

Phase 001-A decision outputs:

```text
011_product_identity_decision.md
012_concept_boundary_decision.md
```

These decisions establish that:

- the product is not conceptually an audio transcription app
- audio transcription is an input path
- the product is a secure conversation analysis and reflection system
- Relationship Reasoning Engine remains an internal engine identity
- psychological hypotheses are permitted only as evidence-limited reflection contexts
- diagnosis, adjudication, surveillance, and professional replacement are out of bounds

---

# Read Order

## Foundation

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

## Decision Closure

12. `011_product_identity_decision.md`
13. `012_concept_boundary_decision.md`

---

# Next Concept Phase

After Phase 001-A, proceed to:

```text
Phase 001-B — Data Lifecycle, Retention, and Encryption Decisions
```

That phase should close decisions around:

- recording retention
- transcript retention
- case retention
- encryption posture
- deletion semantics
- export retention
