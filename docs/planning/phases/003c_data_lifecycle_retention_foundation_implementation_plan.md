# 003-C — Data Lifecycle / Retention Foundation Implementation Plan

## Status

Complete.

This subgroup converts accepted lifecycle and retention architecture into implementation-ready foundation plans.

It does not implement code, schema migrations, retention workers, deletion cascades, UI changes, privacy/encryption changes, prompt changes, deployment changes, or data migrations.

---

# Purpose

003-C prepares lifecycle and retention work so later implementation can handle recordings, transcripts, cases, reports, exports, graph objects, and corpus evidence without silent retention or incomplete deletion.

It answers:

- Which lifecycle concepts already exist in the prototype?
- Which lifecycle concepts need first-class implementation planning?
- How should recordings and audio source artifacts be represented?
- How should transcript draft, saved, and case-retained states be distinguished?
- How should derived artifacts inherit retention from transcript versions and evidence?
- How should deletion cascades and corpus staleness be gated?
- What should 003-D use for privacy and encryption planning?

---

# Outputs

| Output | Document |
|---|---|
| Data lifecycle / retention foundation implementation plan | `../architecture/003c_data_lifecycle_retention_foundation_implementation_plan.md` |
| Lifecycle artifact implementation matrix | `../inventories/003c_lifecycle_artifact_implementation_matrix.md` |
| Retention and deletion work packages | `../inventories/003c_retention_deletion_work_packages.md` |
| Deletion cascade gate checklist | `../inventories/003c_deletion_cascade_gate_checklist.md` |

---

# Implementation Reference Reviewed

003-C reviewed the accepted Phase 002 lifecycle architecture and current implementation references including:

```text
docs/planning/architecture/002c_data_lifecycle_retention_architecture_plan.md
docs/planning/inventories/002c_artifact_retention_matrix.md
backend/api/routes/transcribe.py
backend/api/routes/transcripts.py
backend/services/audio_service.py
backend/services/transcript_service.py
backend/repositories/transcript_repository.py
backend/db/models.py
config/settings.py
```

---

# Current Baseline Findings

The prototype already has useful lifecycle foundations:

- temporary audio upload cleanup
- transcription endpoint returning transcript text and metadata
- transcript ingest into Transcript, TranscriptVersion, speakers, turns, and evidence quotes
- version-aware evidence rebuilding
- readiness state around transcript review
- transcript delete route
- repository-level delete cascade path
- coarse transcript retention purge setting
- owner linkage on transcript and case rows

The prototype is not yet sufficient for the accepted lifecycle model because it lacks explicit source-artifact lifecycle records, per-artifact retention rules, draft/saved/case-retained lifecycle states, export artifact semantics, formal content-free lifecycle events, and graph/corpus staleness handling.

---

# Accepted Decisions

## 1. Implement lifecycle policy before expanding retained/corpus behavior

Corpus reasoning, retained reports, export behavior, and graph enrichment should not expand until retention and deletion semantics are explicit.

## 2. Transcript remains the retained text aggregate

`Transcript` remains the near-term aggregate for retained conversation text, speakers, turns, versions, and evidence quotes.

`ConversationRecord` remains conceptual unless source-artifact planning later proves a separate implementation object is needed.

## 3. Recording lifecycle needs SourceArtifact / RecordingArtifact semantics

`SourceType.AUDIO` can remain a source marker, but it is not a retention boundary.

Later implementation should plan a `SourceArtifact` / `RecordingArtifact` equivalent for ephemeral audio lifecycle metadata.

## 4. RetentionRule needs explicit policy representation

A policy registry or schema object should define artifact-specific retention behavior, promotion triggers, expiration rules, cascade behavior, user visibility, and lifecycle event requirements.

## 5. Transcript lifecycle state should become explicit

Readiness flags are useful but insufficient.

Later implementation should plan states such as draft, ready for review, saved, case-retained, delete-requested, cascade-deleting, deleted, expired, and purged.

## 6. Save and case assignment are retention promotions

Saving a transcript and assigning a transcript to a case should both be treated as explicit retention-promoting actions.

Case assignment also makes the transcript eligible for Case Evidence Corpus reasoning.

## 7. Version and evidence retention must be dependency-aware

Transcript versions and evidence quotes should remain available while retained reports, findings, hypotheses, reflection points, graph objects, or corpus claims depend on them.

Retained analysis should eventually require transcript-version-bound evidence.

## 8. Derived artifacts inherit source retention

Reflection runs, lens/module runs, findings, hypotheses, reflection points, graph objects, and reports should inherit retention from their evidence basis unless intentionally exported.

## 9. ExportArtifact should become a deliberate lifecycle concept

Exports should have explicit source report/version scope, owner scope, created/downloaded/expires/deleted timestamps, server-retention behavior, and encryption posture.

## 10. Deletion cascade must handle graph and corpus staleness

Deleting, expiring, or purging evidence must delete, invalidate, stale-mark, or recompute dependent graph, report, and corpus-level claims.

## 11. Lifecycle events must be content-free

Lifecycle events may record artifact class, IDs, owner, state transition, reason, and time.

They must not include transcript bodies, evidence quote text, prompt payloads, model completions, report bodies, export bodies, secrets, session tokens, or login codes.

---

# Work Package Summary

003-C defines work packages for:

```text
DLR-WP-001 — SourceArtifact / RecordingArtifact lifecycle plan
DLR-WP-002 — RetentionRule policy registry
DLR-WP-003 — Transcript lifecycle state plan
DLR-WP-004 — Draft expiration plan
DLR-WP-005 — Save and case-retention promotion plan
DLR-WP-006 — Version and evidence retention hardening
DLR-WP-007 — DeletionCascadeContract
DLR-WP-008 — Content-free lifecycle events
DLR-WP-009 — ExportArtifact lifecycle plan
DLR-WP-010 — Derived artifact retention inheritance plan
DLR-WP-011 — Retention worker and scheduler plan
DLR-WP-012 — Lifecycle API/DTO visibility plan
DLR-WP-013 — Retention and deletion tests
```

P2 decisions remain for possible long-term audio retention, physical `ConversationRecord` reassessment, and advanced export-retention options.

---

# Gates Carried Forward

003-C carries forward these gates:

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
- retention visibility gate
- job-safe shutdown gate, for retention workers

---

# Handoff to 003-D

003-D should prepare privacy and encryption implementation planning for:

- owner scope on lifecycle artifacts
- service-purpose access to source artifacts and retained transcripts
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

# Exit Criteria

003-C is complete when:

- lifecycle/retention implementation plan exists
- lifecycle artifact implementation matrix exists
- retention/deletion work packages exist
- deletion cascade gate checklist exists
- current implementation references are reviewed at planning level
- 003-D handoff is explicit
- Phase 003 indexes are updated
- broad implementation remains blocked

All criteria are satisfied.

---

# Next Phase

Proceed to:

```text
003-D — Privacy Boundary / Encryption Baseline Implementation Plan
```
