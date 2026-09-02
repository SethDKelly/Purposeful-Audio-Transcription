# 003-C Retention and Deletion Work Packages

## Status

Accepted as the Phase 003-C retention and deletion implementation-planning work package inventory.

These packages are not implementation authorization.

---

# Purpose

Break the lifecycle/retention foundation into later implementation-ready work packages.

Each package must be gated before code, schema, worker, UI, report, export, or data migration changes are accepted.

---

# Work Package Legend

| Field | Meaning |
|---|---|
| ID | Stable Phase 003-C work package identifier |
| Priority | P0, P1, or P2 |
| Target | Main implementation area later affected |
| Gate | Acceptance gate that must pass before implementation is accepted |

---

# P0 Work Packages

## DLR-WP-001 — SourceArtifact / RecordingArtifact lifecycle plan

Priority: P0

Target:

```text
backend/domain/transcript.py
backend/services/audio_service.py
backend/api/routes/transcribe.py
future persistence/migration plan
```

Purpose:

Represent audio as an ephemeral source artifact with lifecycle metadata rather than only `SourceType.AUDIO`.

Required planning outcomes:

- state model for upload, staged, processing, failed, deleted, purged
- owner scope requirement
- temporary storage reference policy
- successful transcription deletion rule
- failed transcription retry/debug TTL, recommended max 24h
- content-free lifecycle event plan

Gate:

```text
retention_gate
lifecycle_event_redaction_gate
privacy_boundary_gate
```

---

## DLR-WP-002 — RetentionRule policy registry

Priority: P0

Target:

```text
config/settings.py
future domain/persistence layer
retention worker planning
```

Purpose:

Replace coarse global retention behavior with artifact-specific policy semantics.

Required planning outcomes:

- artifact classes covered
- default retention behavior
- promotion triggers
- expiration basis
- deletion cascade behavior
- user-visible warning requirement
- audit/lifecycle event requirement

Gate:

```text
retention_gate
documentation_authority_gate
```

---

## DLR-WP-003 — Transcript lifecycle state plan

Priority: P0

Target:

```text
backend/domain/transcript.py
backend/db/models.py
backend/repositories/transcript_repository.py
backend/services/transcript_service.py
```

Purpose:

Plan explicit lifecycle states beyond `analysis_ready`, `skip_review`, and `ready_at`.

Required planning states:

```text
draft
ready_for_review
saved
case_retained
delete_requested
cascade_deleting
deleted
expired
purged
```

Gate:

```text
retention_gate
domain_mapping_gate
```

---

## DLR-WP-004 — Draft expiration plan

Priority: P0

Target:

```text
transcript repository/service
retention worker
tests
UI handoff
```

Purpose:

Implement a clear draft TTL path before retained/corpus behavior expands.

Required planning outcomes:

- default draft expiration, recommended 7 days
- fields/config needed for expiry
- worker behavior
- user-visible deadline
- cascade behavior for draft versions/evidence/runs/reports

Gate:

```text
retention_gate
deletion_cascade_gate
retention_visibility_gate
```

---

## DLR-WP-005 — Save and case-retention promotion plan

Priority: P0

Target:

```text
transcript service
case service
case repository
UI/report handoff
```

Purpose:

Make save and case assignment explicit retention promotions.

Required planning outcomes:

- save/keep-after-analysis state transition
- case assignment state transition
- user-facing retention warning
- case evidence corpus eligibility rule
- unlink-from-case behavior

Gate:

```text
retention_gate
corpus_reasoning_gate
privacy_boundary_gate
```

---

## DLR-WP-006 — Version and evidence retention hardening

Priority: P0

Target:

```text
backend/domain/transcript.py
backend/repositories/transcript_repository.py
backend/db/models.py
analysis/report services
```

Purpose:

Harden transcript-version-bound evidence as the retained analysis basis.

Required planning outcomes:

- retained analysis requires transcript version ID
- evidence quotes inherit version retention
- old versions retained while reports/graph/corpus objects depend on them
- stale/current version semantics
- migration strategy for optional `transcript_version_id`

Gate:

```text
analysis_boundary_gate
report_scope_gate
corpus_staleness_gate
```

---

## DLR-WP-007 — DeletionCascadeContract

Priority: P0

Target:

```text
backend/repositories/transcript_repository.py
backend/services/transcript_service.py
case/report/graph repositories
future worker
```

Purpose:

Turn deletion from an implementation path into a documented, testable cascade contract.

Required planning outcomes:

- transcript deletion dependency graph
- case deletion options
- report deletion behavior
- export deletion behavior
- derived artifact deletion/invalidation/stale marking
- idempotent retry behavior

Gate:

```text
deletion_cascade_gate
corpus_staleness_gate
regression_gate
```

---

## DLR-WP-008 — Content-free lifecycle events

Priority: P0

Target:

```text
audit/lifecycle event model
logging middleware
retention workers
```

Purpose:

Provide lifecycle auditability without leaking sensitive content.

Required planning outcomes:

- allowed event metadata
- forbidden event metadata
- event names for create, stage, process, save, case-promote, expire, delete-request, cascade-delete, purge, export, export-delete
- owner/resource references
- operational retention window

Gate:

```text
lifecycle_event_redaction_gate
log_redaction_gate
privacy_boundary_gate
```

---

# P1 Work Packages

## DLR-WP-009 — ExportArtifact lifecycle plan

Priority: P1

Target:

```text
report/export services
future storage layer
UI/export flow
```

Purpose:

Make exports explicit portable artifacts with bounded server retention.

Gate:

```text
export_boundary_gate
privacy_boundary_gate
retention_visibility_gate
```

---

## DLR-WP-010 — Derived artifact retention inheritance plan

Priority: P1

Target:

```text
workflow/module run services
finding repository
construct/graph repositories
synthesis report repository
```

Purpose:

Define how reflection runs, findings, hypotheses, reflection points, graph objects, and reports inherit retention from source transcript versions and case/corpus scope.

Gate:

```text
retention_gate
analysis_boundary_gate
corpus_staleness_gate
```

---

## DLR-WP-011 — Retention worker and scheduler plan

Priority: P1

Target:

```text
worker process
background jobs
settings
operational docs
```

Purpose:

Plan idempotent workers for recording purge, failed transcription cleanup, draft expiration, export expiration, and cascade cleanup.

Gate:

```text
retention_gate
job_safe_shutdown_gate
regression_gate
```

---

## DLR-WP-012 — Lifecycle API/DTO visibility plan

Priority: P1

Target:

```text
backend/api/schemas.py
backend/api/routes/transcripts.py
backend/api/routes/cases.py
frontend views
```

Purpose:

Plan safe API exposure for lifecycle state, retention deadline, case retention, deletion preview, and export expiry without exposing sensitive content.

Gate:

```text
retention_visibility_gate
privacy_boundary_gate
ui_language_gate
```

---

## DLR-WP-013 — Retention and deletion tests

Priority: P1

Target:

```text
tests/
future evaluation fixtures
```

Purpose:

Define tests for temp audio deletion, draft expiry, save/case promotion, delete cascade, export expiry, graph/corpus staleness, and content-free lifecycle events.

Gate:

```text
evaluation_gate
regression_gate
release_readiness_gate
```

---

# P2 Work Packages

## DLR-WP-014 — Long-term audio retention decision

Priority: P2

Target:

```text
future product/security planning
```

Purpose:

Decide whether explicit long-term audio retention is ever supported.

Default remains no.

Gate:

```text
retention_gate
privacy_boundary_gate
```

---

## DLR-WP-015 — Physical ConversationRecord reassessment

Priority: P2

Target:

```text
future domain ADR
```

Purpose:

Reassess whether `ConversationRecord` needs to become a separate implementation aggregate after `SourceArtifact` planning is complete.

Gate:

```text
domain_mapping_gate
retention_gate
```

---

## DLR-WP-016 — Advanced export retention options

Priority: P2

Target:

```text
future export settings
```

Purpose:

Consider optional encrypted export archives, redaction levels, and user-configured server retention after baseline export semantics are safe.

Gate:

```text
export_boundary_gate
encryption_target_gate
ui_language_gate
```

---

# Dependency Order

Recommended order for later implementation:

```text
DLR-WP-001
DLR-WP-002
DLR-WP-003
DLR-WP-004
DLR-WP-005
DLR-WP-006
DLR-WP-007
DLR-WP-008
DLR-WP-009 through DLR-WP-013
```

Do not expand case-corpus reasoning or report exports before DLR-WP-005, DLR-WP-006, and DLR-WP-007 are planned and gated.

---

# Decision

These packages are ready to feed 003-D, 003-E, 003-G, and the 003-H exit review.
