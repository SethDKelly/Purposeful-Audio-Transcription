# 003-C Deletion Cascade Gate Checklist

## Status

Accepted as the Phase 003-C deletion cascade gate checklist.

---

# Purpose

Define the minimum questions later implementation must answer before deletion, expiration, purge, export cleanup, or graph/corpus staleness behavior is accepted.

This checklist is not code.

---

# Gate Principle

```text
A delete is not complete until dependent sensitive artifacts are deleted, invalidated, stale-marked, recomputed, or explicitly preserved under a separate user-authorized boundary.
```

---

# Universal Checklist

Every lifecycle delete/expire/purge implementation must answer:

1. What artifact class is being removed?
2. Who owns the artifact?
3. What user action, TTL, or policy triggered removal?
4. Is removal immediate, asynchronous, or staged?
5. Which dependent artifacts are deleted?
6. Which dependent artifacts are stale-marked or invalidated?
7. Which dependent artifacts are preserved and why?
8. Does preservation require explicit user intent?
9. Are lifecycle events content-free?
10. Are logs content-free?
11. Can the operation safely retry?
12. Can the user understand the consequence before destructive action?
13. Does any corpus/report/graph claim still rely on deleted evidence?
14. Does export behavior clearly distinguish server-retained copies from downloaded user copies?

---

# Operation-Specific Checks

## Recording / audio purge

Required checks:

- audio bytes are removed after successful transcription
- failed audio has a bounded retry/debug TTL, recommended max 24h
- purge leaves no transcript text in audio lifecycle logs
- source metadata is content-free
- purge does not delete a saved transcript created from the recording

Blocking failure examples:

- audio retained silently after transcription
- file path/object key logged with sensitive context
- failed upload has no expiry path

---

## Transcript draft expiration

Required checks:

- draft TTL exists and is visible to the user
- expiration deletes draft text, draft turns, draft speakers, draft evidence, draft runs, and draft reports
- expiration does not delete an explicitly saved transcript
- lifecycle event records reason without content

Blocking failure examples:

- draft becomes durable without explicit save or case assignment
- draft expiry leaves usable report or evidence artifacts behind

---

## Save transcript / keep after analysis

Required checks:

- user intent is explicit
- state changes from draft/review to saved
- retention rule changes from temporary to durable-until-delete
- evidence/version dependencies remain intact
- save action is owner-scoped

Blocking failure examples:

- analysis run silently saves transcript
- saved transcript lacks owner scope

---

## Assign transcript to case

Required checks:

- user sees case assignment as retention-significant
- transcript becomes case-retained or inherits case-retention policy
- transcript versions and evidence basis remain available for case evidence corpus
- corpus eligibility is explicit
- hidden account-wide inference remains blocked

Blocking failure examples:

- case membership treated as cosmetic foldering only
- corpus claim created without transcript-version/evidence lineage

---

## Remove transcript from case

Required checks:

- unlinking removes case/corpus association
- unlinking does not delete the transcript unless explicitly requested
- corpus summaries/graph claims are recomputed, stale-marked, or invalidated
- report scope reflects changed case membership

Blocking failure examples:

- old case-level pattern still counts unlinked transcript as active evidence
- unlink performs destructive transcript delete without explicit confirmation

---

## Delete saved transcript

Required checks:

- user sees deletion cascade preview
- transcript text, speakers, turns, versions, evidence quotes, reflection runs, module/lens runs, findings, hypotheses, reflection points, reports, graph nodes/edges, and case links are deleted or rendered inaccessible
- case/corpus summaries are recomputed, stale-marked, or invalidated
- server-retained exports are handled by explicit export policy
- operation is idempotent

Blocking failure examples:

- deleted transcript still supports an active corpus pattern
- report remains visible without source evidence basis
- cascade logs transcript body or quote text

---

## Delete case

Required checks:

- user chooses between case wrapper deletion and destructive case-plus-contained-transcripts deletion
- wrapper-only deletion unlinks transcripts and invalidates/recomputes case-corpus outputs
- destructive deletion cascades through contained transcripts and dependent artifacts
- user warning is explicit

Blocking failure examples:

- deleting case silently deletes transcripts
- deleting case wrapper leaves active case-corpus claims without case scope

---

## Delete report

Required checks:

- report materialization is deleted or hidden
- source transcript and evidence are preserved unless explicitly deleted
- export copies are handled separately
- report-derived graph summaries are deleted, stale-marked, or recomputed if required

Blocking failure examples:

- report deletion deletes source transcript by surprise
- stale report-derived claims remain active as if current

---

## Delete export

Required checks:

- server-retained export bytes are deleted
- export metadata retention is explicit and content-free
- downloaded user copies are acknowledged as outside application boundary
- export lifecycle event excludes report body/transcript text

Blocking failure examples:

- export retained server-side silently
- lifecycle event stores export body or transcript excerpts

---

## Transcript version staleness

Required checks:

- edits after completed analysis create or preserve version semantics
- retained reports remain bound to the version they analyzed
- current-version changes do not rewrite old evidence basis
- stale-current warnings are available for old reports/corpus claims

Blocking failure examples:

- old report silently points to new transcript text
- evidence quote IDs are reused across versions in a way that breaks traceability

---

# Required Test Families

Later implementation should add tests for:

```text
audio_temp_cleanup
failed_audio_ttl
transcript_draft_expiry
save_promotion
case_assignment_retention_promotion
case_unlink_corpus_staleness
transcript_delete_cascade
case_delete_wrapper_only
case_delete_destructive
report_delete_without_source_delete
export_expiry
content_free_lifecycle_events
idempotent_delete_retry
version_bound_report_staleness
```

---

# Decision

This checklist carries forward to later implementation phases as part of the deletion cascade gate, retention gate, lifecycle event redaction gate, corpus staleness gate, export boundary gate, and regression gate.
