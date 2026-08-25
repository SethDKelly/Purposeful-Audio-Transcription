# 002-H — Refactor Backlog, Sequencing, and Acceptance Gates

## Status

Complete.

This subgroup translates Phase 002 architecture decisions into a candidate refactor backlog, implementation wave sequence, and acceptance-gate model.

---

# Purpose

002-H prepares the project for the mandatory 002-I exit review.

It answers:

- What backlog items follow from Phase 002?
- Which items are P0/P1/P2?
- What sequence should implementation refactoring follow?
- Which gates should block unsafe implementation?
- What should 002-I use to authorize or block Phase 003?

---

# Outputs

| Output | Document |
|---|---|
| Refactor backlog, sequencing, and acceptance-gate plan | `../architecture/002h_refactor_backlog_sequencing_acceptance_gates.md` |
| Refactor backlog inventory | `../inventories/002h_refactor_backlog.md` |
| Acceptance gate matrix | `../inventories/002h_acceptance_gate_matrix.md` |

---

# Accepted Decisions

## 1. Refactoring should proceed in controlled waves

The project should avoid a broad rewrite that changes domain model, retention, privacy, prompts, reports, UI, and deployment all at once.

## 2. Documentation authority cleanup comes first

Old or stale planning material should not reassert product authority during implementation.

## 3. Domain and lifecycle foundations should precede prompt/report/UI polish

The UI and report layer should depend on stable concepts for transcript versions, evidence quotes, retention rules, privacy boundary, corpus scope, hypotheses, safety posture, and cost state.

## 4. Privacy, retention, and deletion gates are blocking gates

Implementation should not expand retained data, corpus reasoning, exports, or logs unless privacy and lifecycle gates pass.

## 5. Analysis boundaries must be enforceable beyond prompting

Prompt instructions alone are insufficient.

Schemas, validators, report rendering, graph rules, and evaluation fixtures should enforce non-diagnostic, evidence-linked, safety-aware, corpus-scoped behavior.

## 6. Cost-state deployment work needs a new design path

The old GitHub Actions workflows were intentionally removed.

Any restored automation should follow the 002-F control-plane and job-safety architecture rather than being reintroduced by habit.

## 7. 002-I must authorize or block Phase 003

002-H prepares the backlog and gates.

002-I remains the mandatory exit review and must decide implementation readiness.

---

# Recommended Implementation Waves

002-H recommends the following candidate sequence:

```text
Wave 0 — Pre-implementation authority lock
Wave 1 — Domain terminology and aggregate alignment
Wave 2 — Data lifecycle and retention foundation
Wave 3 — Privacy boundary and encryption baseline
Wave 4 — Analysis boundary, hypothesis, safety, and corpus reasoning
Wave 5 — Cost state and personal deployment control plane
Wave 6 — UI/UX and report alignment
Wave 7 — Evaluation, fixtures, and regression gates
```

---

# Candidate Phase 003 Shape

002-H proposes, subject to 002-I review:

```text
Phase 003 — Foundation Refactor Planning and Authority Cleanup
```

Candidate groups:

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

002-I may accept, modify, or replace this recommendation.

---

# Minimum P0 Gates for Implementation Start

002-H identifies these as minimum P0 gates for any implementation-starting phase:

- documentation authority gate
- terminology drift gate
- domain mapping gate
- retention gate
- deletion cascade gate
- privacy boundary gate
- log redaction gate
- analysis boundary gate
- hypothesis boundary gate
- safety override gate
- corpus reasoning gate
- cost state gate
- job-safe shutdown gate
- workflow replacement gate
- evaluation gate

---

# Handoff to 002-I

002-I should consolidate:

- accepted decisions from 002-A through 002-H
- complete output inventory
- deferred decisions
- stale/superseded documentation list
- P0/P1/P2 backlog summary
- mandatory gate set
- recommended Phase 003 scope
- implementation readiness result

002-I should explicitly decide one of:

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
- prompt changes
- validators
- UI changes
- deployment changes
- GitHub Actions
- tests
- encryption changes
- retention workers

Implementation remains blocked until Phase 002-I exit review authorizes the next phase.

---

# Exit Criteria

002-H is complete when:

- refactor sequencing plan exists
- backlog inventory exists
- acceptance gate matrix exists
- minimum P0 gate set is identified
- candidate Phase 003 shape is proposed
- 002-I handoff is explicit
- implementation remains blocked until 002-I

All criteria are satisfied.

---

# Next Phase

Proceed to the mandatory gate:

```text
002-I — Phase 002 Exit Review and Consolidation
```