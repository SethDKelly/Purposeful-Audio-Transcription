# 022 — Refactor Readiness Decision

## Status

Accepted as the Phase 001 refactor-readiness decision.

This document determines whether the concept foundation is sufficiently closed to begin implementation refactor planning.

---

# Decision Summary

The product is ready for refactor planning.

It is not yet ready for broad implementation changes without a refactor roadmap.

The correct next step is:

```text
Phase 002 — Concept-to-Architecture Refactor Roadmap
```

This should translate accepted concepts into implementation phases, not immediately modify core application behavior.

---

# Refactor Readiness Result

## Ready

The concept foundation is ready to govern refactor planning because the following decisions are closed:

- product identity
- conceptual boundary
- data lifecycle
- retention defaults
- encryption posture
- hypothesis-aware reflection boundary
- therapeutic reflection lens language
- safety-aware override behavior
- personal owner/operator model
- cost-state model
- future enterprise posture

## Not Yet Ready For

The project is not yet ready for immediate feature expansion in the old architecture.

Avoid starting unrelated implementation work until the refactor roadmap maps current code to accepted concepts.

---

# Refactor Planning Principles

## 1. Concepts Before Code

Every refactor task should name the concept it serves.

Example:

```text
Transcript Version
Evidence Quote
Retention Rule
Cost State
Psychological Hypothesis
Privacy Boundary
```

## 2. Preserve Working Prototype Value

The existing application should not be discarded blindly.

The current implementation has useful assets:

- transcription flow
- transcript preparation
- evidence quote indexing
- analysis modules
- workflow execution
- reports
- cases
- graph/ontology work
- React UI work
- AWS sleep/wake mechanism
- security improvements
- deployment artifacts

These should be mapped, retained, revised, or retired deliberately.

## 3. Do Not Let Old Names Reassert Authority

Implementation packages, old README wording, old screenshots, and old deployment docs may still use legacy terminology.

Those should be updated only after the roadmap identifies a safe sequence.

## 4. Security and Retention Are Not Optional Polish

Because the product handles sensitive conversations, privacy, encryption, retention, deletion, and redacted logs are core concepts.

They should be treated as architecture drivers.

## 5. Personal Mode Comes First

The first refactor target is the personal owner-operated app.

Enterprise capability should be preserved through clean policy boundaries, not implemented prematurely.

## 6. Analysis Must Remain Evidence-Limited

Refactoring prompts, schemas, validators, UI labels, and report language should all preserve:

- evidence traceability
- confidence calibration
- non-diagnostic discipline
- hypothesis boundaries
- safety-aware override behavior

---

# Recommended Phase 002 Structure

Phase 002 should be split into subgroups rather than one-shotted.

Recommended subphases:

```text
002-A — Documentation Authority and Terminology Inventory
002-B — Concept-to-Domain Model Mapping
002-C — Data Lifecycle and Retention Architecture Plan
002-D — Privacy Boundary and Encryption Architecture Plan
002-E — Analysis Boundary, Hypothesis, and Safety Architecture Plan
002-F — Cost State and Personal Deployment Architecture Plan
002-G — UI/UX Concept Alignment Plan
002-H — Refactor Backlog, Sequencing, and Acceptance Gates
```

## Why Not One-Shot Phase 002

The current application contains many implementation areas. A single large refactor plan would risk becoming vague or mixing unrelated concerns.

The accepted concepts are separable enough to support iterative refactor planning.

---

# First Implementation Targets After Phase 002

The likely first implementation targets are:

1. documentation authority and terminology cleanup
2. transcript/recording/data lifecycle alignment
3. retention state fields and policies
4. transcript version/evidence binding hardening
5. privacy boundary and encryption design
6. hypothesis-aware reflection objects and output schema
7. safety-aware gating and report behavior
8. cost state visibility and operational invariants
9. UI copy and navigation alignment

These are not Phase 001 implementation tasks. They are candidates for Phase 003+ after Phase 002 planning.

---

# Refactor Readiness Checklist

Before implementation begins, Phase 002 should produce:

- concept-to-code inventory
- terminology migration plan
- accepted domain model changes
- accepted data lifecycle architecture
- accepted privacy/encryption architecture
- accepted analysis boundary architecture
- accepted cost state architecture
- UI alignment plan
- test/evaluation gate plan
- refactor sequence
- explicit non-goals

---

# Current Recommendation

Proceed to:

```text
Phase 002 — Concept-to-Architecture Refactor Roadmap
```

Do not proceed directly to code refactoring without that roadmap.

---

# Decision

The concept foundation is accepted.

The project is ready for refactor planning.

The project is not yet ready for direct implementation refactoring without Phase 002.
