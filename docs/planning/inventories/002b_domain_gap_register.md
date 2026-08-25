# 002-B Domain Gap Register

## Status

Accepted as the Phase 002-B domain gap register.

---

# Purpose

Identify domain-level gaps discovered while mapping accepted concepts to the existing domain model.

This register does not authorize implementation. It feeds later Phase 002 architecture plans.

---

# Priority Legend

| Priority | Meaning |
|---|---|
| P0 | Must be resolved before implementation refactoring begins |
| P1 | Should be resolved in the Phase 002 architecture roadmap |
| P2 | Can be deferred if explicitly tracked |

---

# Gaps

## P0 — Recording Lifecycle Is Not First-Class Enough

Accepted concept:

```text
Recording is an ephemeral input artifact.
```

Current mapping:

- `SourceType.AUDIO`
- upload/transcription flow
- transcript source metadata

Gap:

The domain model needs an explicit way to express that audio exists only temporarily, has a retry/debug TTL, and should delete after successful transcription.

Feeds:

```text
002-C — Data Lifecycle and Retention Architecture Plan
```

---

## P0 — Retention Rule Is Not a First-Class Domain Concept

Accepted concept:

```text
Each artifact has a retention policy.
```

Current mapping:

- no confirmed first-class `RetentionRule` in reviewed domain files
- retention described in concept docs, not domain model

Gap:

Need architecture for draft expiration, saved transcript durability, case-promoted retention, derived artifact inheritance, export retention, and deletion cascade.

Feeds:

```text
002-C
```

---

## P0 — Privacy Boundary Is Not Yet Domain-Aligned

Accepted concept:

```text
Sensitive content is private by default and owner-scoped.
```

Current mapping:

- auth/security docs
- deployment posture
- no confirmed first-class privacy boundary in domain files reviewed

Gap:

Need an architecture representation for owner scope, content access, logs, redaction, export, encryption, and least privilege.

Feeds:

```text
002-D — Privacy Boundary and Encryption Architecture Plan
```

---

## P0 — Hypothesis Needs a Bounded Domain Representation

Accepted concept:

```text
Psychological Hypothesis is evidence-limited and not a diagnosis.
```

Current mapping:

- `FindingType.HYPOTHESIS`
- exploratory hypotheses in report language
- module/lens output conventions

Gap:

A hypothesis should preserve source, support level, evidence, contradiction/alternative explanations, confidence ceiling, and non-diagnostic guardrails.

Feeds:

```text
002-E — Analysis Boundary, Hypothesis, and Safety Architecture Plan
```

---

## P0 — Safety Override Needs More Than a Boolean

Accepted concept:

```text
Safety-aware framing overrides ordinary reflection and mutual-improvement framing.
```

Current mapping:

- `WorkflowRun.safety_mode`
- `ModuleRun.safety_flags`

Gap:

Need explicit safety posture/severity/reasoning representation so safety can affect prompt selection, report structure, framing, skipped sections, UI banners, and evaluation gates.

Feeds:

```text
002-E
```

---

## P1 — Reflection Point Should Replace Recommendation/Intervention Semantics

Accepted concept:

```text
Reflection Point is a non-prescriptive self-review prompt.
```

Current mapping:

- `recommendations`
- `FindingType.INTERVENTION`
- report guidance

Gap:

The implementation should avoid treatment-like or directive language by mapping recommendations/interventions to bounded reflection points or repair possibilities.

Feeds:

```text
002-E, 002-G
```

---

## P1 — Cost State Needs a Concept-to-Architecture Representation

Accepted concept:

```text
Cost State is first-class for personal mode.
```

Current mapping:

- AWS operations docs
- sleep/wake deployment behavior
- no reviewed core domain representation

Gap:

Need to decide whether Cost State lives as deployment policy, status endpoint, app state, or operational record.

Feeds:

```text
002-F — Cost State and Personal Deployment Architecture Plan
```

---

## P1 — Export Artifact Needs Explicit Semantics

Accepted concept:

```text
Export is deliberate and portable.
```

Current mapping:

- report ZIP/export behavior
- no explicit domain treatment in reviewed domain docs

Gap:

Need architecture for export creation, redaction, server retention, deletion, and evidence/version binding.

Feeds:

```text
002-C, 002-D, 002-G
```

---

## P1 — Confidence Vocabulary Needs Reconciliation

Accepted concept levels include:

```text
observed
likely
possible
insufficient evidence
contraindicated
```

Current enum includes:

```text
observed
high
moderate
low
exploratory
insufficient_evidence
```

Gap:

Need to decide whether to keep implementation levels, add concept-level aliases, or update schemas.

Feeds:

```text
002-E, 002-H
```

---

## P2 — Conversation Record Aggregate Needs Clarification

Accepted concept:

```text
Conversation Record is the source conversation represented by transcript and optional recording.
```

Current mapping:

- `Transcript` acts as the root object

Gap:

May not require a new table/class, but architecture should decide whether `Transcript` remains the aggregate root or whether a broader `ConversationRecord` concept is needed.

Feeds:

```text
002-B follow-up if needed; otherwise 002-C
```

---

# Register Decision

These gaps should not trigger immediate implementation.

They are inputs to Phase 002-C through 002-H.

The next subgroup, 002-C, should start with P0 lifecycle and retention gaps.
