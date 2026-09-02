# Implementation Guardrails

## Status

Accepted as the Phase 004-A implementation guardrail surface.

These guardrails apply to all contributors, Cursor sessions, Codex sessions, and agentic implementation work in this repository.

---

# Purpose

Prevent implementation work from bypassing the accepted concept model, Phase 003 gates, and Phase 004 subgroup boundaries.

This document is intentionally concise enough for agents to reference without importing the entire planning corpus into every context window.

---

# Canonical Authority Stack

When sources conflict, use this order:

```text
1. docs/concepts/
2. docs/planning/architecture/003h_phase_003_exit_review_consolidation.md
3. docs/planning/inventories/003h_phase_004_authorized_scope.md
4. docs/planning/phases/004_controlled_foundation_refactor_implementation.md
5. accepted Phase 004 subgroup summary for the current work
6. directly relevant Phase 003 architecture plan, matrix, work packages, and gate checklist
7. reconciled implementation docs
8. current code
9. legacy/reference/historical docs
```

Current code is important implementation evidence, but it is not product authority when it conflicts with accepted concepts.

---

# Required Work Pattern

Every implementation change must state:

```text
Phase 004 subgroup:
Phase 003 work packages executed:
Applicable gates:
Compatibility posture:
Migration posture:
Tests or verification:
Deferred / not touched:
```

This may be recorded in the subgroup phase summary, pull request body, commit notes, or implementation note.

---

# Current Phase

```text
Phase 004 — Controlled Foundation Refactor Implementation
```

Completed subgroups:

```text
004-A — Implementation Authority Lock, Agent Rules, and Documentation Guardrails
004-B — Domain Terminology Compatibility and Concept Contract Implementation
```

Next subgroup:

```text
004-C — Lifecycle, Retention, SourceArtifact, and Deletion-Cascade Foundation
```

Mandatory exit gate:

```text
004-I — Phase 004 Exit Review and Consolidation
```

---

# Current 004-C Read Set

Before 004-C implementation work, read:

```text
docs/planning/architecture/003c_data_lifecycle_retention_foundation_implementation_plan.md
docs/planning/inventories/003c_lifecycle_artifact_implementation_matrix.md
docs/planning/inventories/003c_retention_deletion_work_packages.md
docs/planning/inventories/003c_deletion_cascade_gate_checklist.md
docs/planning/architecture/004b_domain_terminology_compatibility_concept_contract_implementation.md
backend/domain/concept_contracts.py
docs/domain/README.md
```

---

# Product Boundary

The accepted product concept is:

```text
Secure Conversation Analysis and Reflection System
```

The historical repository shell remains:

```text
Purposeful Audio Transcription
```

The internal analysis engine remains:

```text
Relationship Reasoning Engine / RRE
```

Audio transcription is an input capability, not the product identity.

---

# Implementation Boundaries

Do not implement broad rewrite work merely because Phase 004 is active.

Do not start a later subgroup's implementation early unless the current accepted phase document explicitly allows it.

Do not let legacy names become product-facing authority without reconciliation.

Do not delete historical/reference docs only because they are outdated.

Do not restore GitHub Actions until the GitHub Actions restoration gate, job-safe shutdown gate, privacy boundary gate, cost-state gate, and release readiness gate are satisfied.

Do not introduce enterprise org/workspace/RBAC/SSO/compliance/billing or always-on availability as Phase 004 baseline scope.

---

# Mandatory Gate Families

Use the smallest relevant gate set for the work, but never ignore a relevant gate.

Carry forward these families:

```text
documentation authority gate
terminology drift gate
domain compatibility gate
retention gate
deletion cascade gate
privacy boundary gate
owner scope gate
owner inheritance gate
service-purpose access gate
encryption baseline gate
log redaction gate
analysis scope gate
evidence linkage gate
hypothesis boundary gate
support-level separation gate
safety posture gate
safety override gate
reflection point gate
corpus scope gate
corpus staleness gate
reasoning graph boundary gate
prompt boundary gate
report scope gate
report language gate
export readiness gate
cost state contract gate
blocking job registry gate
job-safe shutdown gate
UI terminology gate
case evidence corpus gate
evaluation gate
regression gate
release readiness gate
```

---

# Sensitive Data Rules

Never log or intentionally expose:

- audio bodies
- transcript bodies
- long evidence passages
- prompt payloads
- raw model completions
- report bodies in operational logs
- export contents in operational logs
- session tokens
- login codes
- secrets

Operational events should be content-free and identify state transitions, IDs, counts, durations, and non-sensitive error categories only.

---

# Analysis Output Rules

The system may use therapeutic, psychological, behavioral, cognitive, relational, and diagnostic-framework-informed concepts as evidence-limited reasoning references.

It must not:

- diagnose people
- confirm or rule out user-provided diagnoses
- label people as having disorders or fixed trait identities
- present clinical or treatment authority
- state hidden intent as fact without direct evidence
- adjudicate legal/professional misconduct
- mutualize serious safety concerns without evidence
- pressure reconciliation in high-risk contexts

---

# Compatibility Rule

Prefer compatibility layers, aliases, adapters, and additive contracts before destructive renames.

Physical class/table/API field renames require explicit compatibility, migration, regression, and release-readiness gates.

004-B added the initial concept-safe domain compatibility surface at:

```text
backend/domain/concept_contracts.py
docs/domain/README.md
```

---

# Documentation Rule

When implementation changes alter concepts, gates, flows, or operational behavior, update the relevant documentation in the same subgroup.

Do not create a new status source that can drift from `docs/planning/phases/README.md`.

---

# Testing Rule

Implementation is not complete unless applicable tests or verification steps are recorded.

For planning-only changes, verification may be document readback and index consistency.

For code changes, verification should include relevant unit, integration, API, UI, fixture, or manual checks as applicable.

---

# Stop Conditions

Stop and record a blocker if work would require:

- crossing into another subgroup without authorization
- unplanned production data migration
- destructive rename without migration plan
- sensitive logging expansion
- all-account hidden corpus inference
- export expansion without export-readiness gate
- GitHub Actions restoration without restoration gates
- enterprise baseline expansion
- broad rewrite outside subgroup scope
