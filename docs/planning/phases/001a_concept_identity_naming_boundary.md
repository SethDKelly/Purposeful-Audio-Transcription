# Phase 001-A — Product Identity, Naming, and Conceptual Boundary

## Status

Accepted concept-design subgroup.

This phase closes the first set of concept reset decisions: what the product is, what its names mean, and where the conceptual boundary sits.

---

# Purpose

Define the product identity and conceptual boundary before any implementation refactor begins.

This phase prevents future work from drifting back into implementation-first design or treating audio transcription as the product center.

---

# Source Documents

This phase is based on:

```text
docs/concepts/000_concept_reset_charter.md
docs/concepts/001_product_premise.md
docs/concepts/010_open_questions.md
```

It produces:

```text
docs/concepts/011_product_identity_decision.md
docs/concepts/012_concept_boundary_decision.md
```

---

# Decisions Closed

## 1. Product Identity

The product is a secure conversation analysis and reflection system.

It is not conceptually an audio transcription app.

## 2. Naming Roles

```text
Purposeful Audio Transcription
  → historical repository / legacy project shell

Relationship Reasoning Engine (RRE)
  → internal analysis engine identity

Audio transcription
  → input capability

Secure Conversation Analysis and Reflection System
  → working concept-design product identity
```

## 3. Conceptual Boundary

The product supports private, evidence-linked reflection over conversation transcripts.

It may use psychological, behavioral, therapeutic, cognitive, and relational lenses to generate hypotheses and reflection points.

It must preserve uncertainty, avoid diagnosis, avoid adjudication, protect sensitive data, and keep the user responsible for decisions.

---

# In Scope

- transcripts from recordings or pasted/uploaded text
- evidence quotes
- transcript versions
- reflection runs
- psychological hypotheses as reflection contexts
- CBT-style reflection
- DBT-style reflection
- behavioral analysis
- psychodynamic or psychoanalytic hypothesis-aware reflection
- communication analysis
- relationship analysis
- business meeting reflection
- therapy-session transcript reflection, when legally and ethically appropriate
- cases for longitudinal reflection
- cost-state aware personal operation

---

# Out of Scope

- diagnosis
- proving personality disorders
- hidden intent as fact
- clinical treatment plans
- legal conclusions
- abuse adjudication as settled fact
- workplace surveillance
- HR decision automation
- covert recording encouragement
- replacement for therapy, mediation, or professional judgment

---

# Acceptance Criteria

This phase is complete when:

- product identity is defined
- naming roles are clarified
- audio transcription is demoted from product center to input path
- RRE is retained as internal engine identity
- in-bound and out-of-bound concepts are documented
- future phases can rely on the accepted product boundary

---

# Follow-On Phase

Proceed next to:

```text
Phase 001-B — Data Lifecycle, Retention, and Encryption Decisions
```

That phase should resolve:

- audio retention
- transcript retention
- case retention
- encryption posture
- deletion semantics
- export retention
