# Phase 004 Division Verification

## Status

Accepted.

Phase 004 has been reviewed after the Phase 003 exit review and is appropriately divided for controlled foundation refactor implementation.

---

# Governing Input

Primary source:

```text
docs/planning/inventories/003h_phase_004_authorized_scope.md
```

Supporting source:

```text
docs/planning/architecture/003h_phase_003_exit_review_consolidation.md
```

---

# Verification Result

```text
Phase 004 is appropriately divided.
Proceed with 004-A.
```

The division is accepted without modification.

---

# Accepted Phase 004 Division

| Subphase | Status | Purpose |
|---|---|---|
| 004-A — Implementation Authority Lock, Agent Rules, and Documentation Guardrails | Proceed | Install contributor/agent guardrails before code implementation begins |
| 004-B — Domain Terminology Compatibility and Concept Contract Implementation | Planned | Add aliases/contracts/DTO posture for accepted domain language without destructive rename-first refactor |
| 004-C — Lifecycle, Retention, SourceArtifact, and Deletion-Cascade Foundation | Planned | Implement lifecycle/retention foundations and deletion cascade contracts incrementally |
| 004-D — Privacy Boundary, Owner Scope, Route, Redaction, and Encryption Baseline | Planned | Harden owner scope, route access, redaction, lifecycle events, and baseline encryption verification |
| 004-E — AnalysisScope, ValidationResult, SafetyPosture, Hypothesis, and Corpus Gates | Planned | Implement analysis-boundary contracts and validators before expanding reports/corpus/export behavior |
| 004-F — Cost-State Control Plane, Blocking Jobs, Idle, Wake, and Shutdown Safety | Planned | Implement or reconcile control-plane contracts and job-safe shutdown behavior |
| 004-G — UI/Report Alignment, Scope Display, Export/Delete Previews, and Status Surfaces | Planned | Align user-facing surfaces after supporting contracts/gates exist |
| 004-H — Evaluation, Regression, Release Readiness, and Implementation Backlog Closure | Planned | Consolidate tests, regressions, release gates, and implementation backlog status |
| 004-I — Phase 004 Exit Review and Consolidation | Mandatory gate | Decide whether implementation phase passes and whether another phase is authorized |

---

# Why the Division Is Logical

## 1. It starts with authority lock

004-A occurs before code, schema, prompt, UI, or deployment changes. This is correct because Phase 004 is the first controlled implementation phase, and agents/contributors need guardrails before touching implementation surfaces.

## 2. It preserves dependency order

Domain terminology and concept contracts come before lifecycle, privacy, analysis, cost-state, UI, and release work.

Lifecycle and retention work comes before broader privacy, analysis, corpus, report, export, and UI expansion.

Privacy and owner scope hardening comes before expanding retained analysis, corpus reasoning, exports, or automation.

Analysis validation foundations come before persuasive reports, corpus outputs, prompt replacement, and export expansion.

Cost-state control-plane work comes before restoring automation or relying on job-safe shutdown behavior.

UI/report alignment comes after stable contracts exist.

Evaluation and release readiness come before exit review.

## 3. It avoids broad rewrite authorization

The sequence forces implementation through bounded subgroups rather than a repository-wide rewrite.

## 4. It keeps GitHub Actions restoration gated

The division does not place deployment automation restoration early. That remains blocked until cost-state, privacy, job-safety, and release-readiness gates are satisfied.

## 5. It keeps enterprise expansion deferred

No subgroup introduces enterprise org/workspace/RBAC/SSO/compliance/billing or always-on availability as baseline Phase 004 scope.

## 6. It includes the mandatory phase exit gate

004-I is present as the required consolidation step before any next numbered phase.

---

# Minor Clarification Accepted

004-A should include not only documentation guardrails but also concrete repository-facing rule surfaces for agents and contributors, such as:

```text
AGENTS.md
.cursor/rules/
docs/planning/implementation_guardrails.md
```

This clarification does not change the Phase 004 subdivision. It clarifies the expected 004-A outputs.

---

# Decision

Phase 004 is appropriately divided.

Proceed with:

```text
004-A — Implementation Authority Lock, Agent Rules, and Documentation Guardrails
```
