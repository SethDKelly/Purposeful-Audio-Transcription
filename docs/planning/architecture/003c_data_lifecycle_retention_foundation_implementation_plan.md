# 003-C Data Lifecycle / Retention Foundation Implementation Plan

## Status

Accepted as the Phase 003-C data lifecycle and retention foundation implementation plan.

This document converts the accepted Phase 002 lifecycle architecture into implementation-ready work packages and gates.

It does not authorize code changes, schema migrations, retention workers, cloud lifecycle rules, encryption changes, UI changes, prompt changes, or production data migrations by itself.

---

# Purpose

Prepare lifecycle and retention implementation work without weakening the current concept authority:

```text
Audio is ephemeral.
Transcript drafts are temporary.
Saved transcripts are durable until deleted.
Case assignment implies durable longitudinal retention.
Derived analysis inherits the retention of its evidence basis.
Exports are explicit and portable.
Deletion cascades must be meaningful and visible.
```

003-C turns that architecture into staged implementation planning for:

- source artifacts and recordings
- transcription artifacts
- transcript draft state
- saved transcript promotion
- case-retained transcript semantics
- transcript versions and evidence quotes
- derived reflection runs, findings, hypotheses, reflection points, graph objects, and reports
- explicit export artifacts
- deletion cascades
- non-content lifecycle events
- retention workers and gates

---

# Governing Inputs

Primary authority:

- `docs/concepts/013_data_lifecycle_decision.md`
- `docs/concepts/014_retention_and_encryption_decision.md`
- `docs/planning/architecture/002c_data_lifecycle_retention_architecture_plan.md`
- `docs/planning/inventories/002c_artifact_retention_matrix.md`
- `docs/planning/architecture/002d_privacy_boundary_encryption_architecture_plan.md`
- `docs/planning/architecture/003a_documentation_authority_cleanup_plan.md`
- `docs/planning/architecture/003b_domain_terminology_concept_mapping_implementation_plan.md`

Implementation reference inspected:

- `backend/api/routes/transcribe.py`
- `backend/api/routes/transcripts.py`
- `backend/services/audio_service.py`
- `backend/services/transcript_service.py`
- `backend/repositories/transcript_repository.py`
- `backend/db/models.py`
- `config/settings.py`

---

# Current Implementation Baseline

The prototype already has useful lifecycle foundations:

1. Audio uploads are written to a temporary path and removed when the context exits.
2. The transcribe endpoint returns transcript text and segment metadata rather than making audio durable by default.
3. Transcript ingest creates a `Transcript`, first `TranscriptVersion`, speakers, turns, and evidence quotes.
4. Evidence quotes are already tied to transcript versions where available.
5. Editing turns clears readiness and can create a new transcript version when completed workflow runs exist.
6. A transcript delete API path calls service-level deletion.
7. The repository contains a `delete_cascade` path that deletes dependent transcript artifacts.
8. A coarse `transcript_retention_days` setting and purge method exist.
9. Database rows already include transcripts, versions, evidence quotes, workflow runs, module runs, findings, constructs, reports, cases, users, sessions, and auth audit events.

The baseline is useful but incomplete for the accepted concept model.

Current gaps:

- no explicit `SourceArtifact` / `RecordingArtifact` domain lifecycle record
- no first-class `RetentionRule` model or equivalent policy registry
- no explicit transcript draft state separate from `analysis_ready`
- no artifact-level `expires_at`, `deleted_at`, `purged_at`, or retention status across sensitive objects
- no complete export artifact lifecycle model
- no formal lifecycle event model for content-free retention/deletion audit
- no explicit graph/corpus staleness contract tied to deletion
- global transcript retention is too coarse for draft/saved/case/export distinctions

---

# Accepted Implementation Principle

```text
Implement lifecycle as explicit artifact policy before expanding corpus reasoning, report retention, exports, or automation.
```

Retention cannot be an implicit side effect of tables, folder membership, or job cleanup.

Deletion cannot only remove a visible row while leaving active evidence, graph, report, or corpus claims behind.

---

# Implementation Planning Decisions

## 1. Transcript remains the lifecycle aggregate for retained conversation text

`Transcript` remains the near-term aggregate root for conversation text, speakers, turns, transcript versions, and evidence quotes.

`ConversationRecord` remains conceptual unless source-artifact complexity later proves a separate aggregate is necessary.

## 2. SourceArtifact / RecordingArtifact should be planned before audio persistence changes

`SourceType.AUDIO` is not enough to represent recording lifecycle.

Later implementation should add a `SourceArtifact` / `RecordingArtifact` equivalent with content-free metadata, storage reference, state, owner scope, expiration, deletion, purge status, retry count, and linked transcript ID.

This does not mean audio should become durable.

The default remains ephemeral audio deletion after successful transcription.

## 3. RetentionRule should begin as an explicit policy registry or schema object

A full database model may not be the first step, but implementation must expose equivalent retention semantics for each artifact class.

Minimum rule attributes:

```text
artifact_class
owner_scope_required
default_retention
promotion_trigger
ttl_or_expiration_basis
delete_cascade_behavior
derived_artifact_inheritance
user_visibility_required
audit_event_required
```

## 4. Draft, saved, case-retained, deleted, expired, and purged states must be explicit

Current readiness fields are useful but not enough to distinguish retention state.

Later implementation should plan a transcript lifecycle state or equivalent fields that can distinguish:

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

## 5. Case assignment is a retention promotion

Case assignment is not only organization.

It should promote a transcript into a durable case evidence corpus boundary.

Implementation planning must ensure the user can later see that case assignment affects retention and corpus eligibility.

## 6. Version and evidence retention must be dependency-aware

Transcript versions and evidence quotes should be retained while they support retained reflection runs, findings, reports, graph objects, hypotheses, reflection points, or case/corpus claims.

Retained analysis should eventually require transcript-version-bound evidence.

## 7. Derived artifacts inherit source retention

Reflection runs, lens/module runs, findings, hypotheses, reflection points, graph objects, and reports should not outlive the retained source evidence unless they are part of an explicit export boundary.

## 8. ExportArtifact should be planned as a deliberate portable output

Exports should not be treated as incidental files.

Later implementation should define an `ExportArtifact` equivalent with source report, source transcript versions, scope, format, owner, created/downloaded/expires/deleted timestamps, retention behavior, and encryption posture.

## 9. Lifecycle events must be content-free

Lifecycle/audit events should record artifact class, ID, owner, state transition, reason, and timing.

They must not record audio bytes, transcript bodies, quote text, prompt payloads, model completions, report bodies, exports, secrets, session tokens, or login codes.

## 10. Deletion cascade must become a gateable contract

The existing repository cascade is useful, but later implementation needs a formal deletion contract that covers every artifact class and corpus/graph consequence.

Deleting or expiring evidence must stale-mark, recompute, invalidate, or delete dependent corpus-level claims.

---

# Proposed Implementation Sequence

## Stage 0 — Lifecycle authority lock

Create a concise lifecycle authority note near implementation planning docs that points to Phase 002/003 decisions.

Do not alter runtime behavior yet.

## Stage 1 — Artifact-state and retention-rule design

Define exact enum/field/model approach for source artifacts, transcript lifecycle state, retention rule, export artifact, and lifecycle events.

## Stage 2 — Migration plan

Plan additive migrations before destructive changes.

Migration should tolerate existing rows and avoid reclassifying historical rows without an explicit rule.

## Stage 3 — Service contract plan

Define service-level behavior for ingestion, audio transcription, draft expiration, save/promotion, case assignment, delete transcript, delete case, delete report, delete export, and purge jobs.

## Stage 4 — Cascade and staleness plan

Define exact dependent artifacts for deletion and how graph/corpus/report claims become deleted, stale, recomputed, or invalidated.

## Stage 5 — Worker/job plan

Prepare idempotent workers for recording purge, failed transcription cleanup, draft expiration, export expiration, lifecycle-event emission, and deletion cascade.

## Stage 6 — Test/evaluation plan

Define tests for audio cleanup, draft expiry, save/case promotion, delete cascade, export expiry, content-free lifecycle events, and corpus staleness.

---

# Required Gates

003-C carries forward or introduces these gates for later implementation:

- retention gate
- deletion cascade gate
- lifecycle event redaction gate
- privacy boundary gate
- log redaction gate
- export boundary gate
- corpus staleness gate
- report scope gate
- evaluation gate
- regression gate

---

# Handoff to 003-D

003-D should use this plan to prepare privacy and encryption implementation planning for:

- owner scope on lifecycle artifacts
- service-purpose access to source artifacts and transcript content
- content-free lifecycle events
- encrypted retained transcripts, evidence, reports, exports, and case/corpus objects
- log redaction verification
- export encryption posture
- deletion and purge audit behavior

---

# Non-goals

003-C does not implement:

- code changes
- schema migrations
- retention workers
- object storage lifecycle rules
- deletion cascade changes
- report or export renderer changes
- privacy/encryption implementation
- UI changes
- prompt changes
- tests
- production data migration

---

# Acceptance Result

The lifecycle and retention foundation implementation plan is ready to feed 003-D and the Phase 003 exit review.

Proceed next to:

```text
003-D — Privacy Boundary / Encryption Baseline Implementation Plan
```
