# 002-C Data Lifecycle and Retention Architecture Plan

## Status

Accepted as the Phase 002-C architecture plan.

This document translates accepted data lifecycle and retention decisions into architecture requirements for later implementation phases.

It does not authorize code or schema changes by itself.

---

# Purpose

Define how recordings, transcription artifacts, transcript drafts, saved transcripts, transcript versions, evidence, analysis outputs, reports, cases, and exports should move through the system.

The plan resolves the Phase 002-B P0 lifecycle gaps:

- recording lifecycle is not first-class enough
- retention rule is not a first-class domain concept

It also prepares handoff requirements for 002-D privacy/encryption planning.

---

# Accepted Lifecycle Principle

```text
Audio is ephemeral.
Transcript drafts are temporary.
Saved transcripts are durable until deleted.
Case assignment implies durable longitudinal retention.
Derived analysis inherits the retention of its evidence basis.
Exports are explicit and portable.
Deletion cascades must be meaningful and visible.
```

---

# Architecture Decision Summary

## 1. Transcript remains the primary durable aggregate

`Transcript` remains the practical aggregate root for retained conversation text.

A broader `ConversationRecord` concept may remain conceptual for now unless later implementation needs a separate object.

## 2. Recording becomes an explicit transient artifact boundary

Recording should no longer be represented only as `SourceType.AUDIO`.

Architecture should model recording as a transient source artifact or lifecycle record with explicit state, retention deadline, deletion status, and transcript linkage.

This does not require retaining audio content in the database. The persisted record may track lifecycle metadata while the audio bytes live only in temporary object storage.

## 3. Retention Rule becomes a first-class policy concept

Each artifact class needs an explicit retention rule, even if implementation starts with configuration and background jobs rather than a full database table.

A retention rule should describe:

- artifact class
- owner scope
- default retention behavior
- retention trigger
- expiration deadline
- deletion cascade behavior
- legal/explicit hold behavior, if ever introduced
- audit/event requirements

## 4. Derived artifacts inherit evidence-basis retention

Findings, hypotheses, reflection points, reasoning graph nodes/edges, reports, and synthesis outputs must not outlive the transcript version or case context that supports them, except as deliberate exports.

## 5. Case assignment is privacy-significant

Assigning a transcript to a case should be treated as explicit durable retention.

The user should understand that case membership preserves transcript/version/evidence history for longitudinal reflection.

## 6. Exports need independent semantics

Exports are portable user artifacts.

Default architecture should generate exports for download and avoid long-term server retention unless explicitly configured.

If retained server-side, exports require owner scoping, encryption, deletion, and audit handling.

---

# Artifact Lifecycle State Model

Use this conceptual state vocabulary for lifecycle planning.

```text
Created
Staged
Processing
ReadyForReview
Draft
Saved
Versioned
Analyzed
CaseRetained
Exported
ExpirationPending
DeleteRequested
CascadeDeleting
Deleted
Purged
Failed
Expired
```

The exact implementation may use narrower enums by artifact type, but these states define the architecture semantics.

## Recording states

```text
Created
→ Staged
→ Processing
→ Deleted/Purged
```

Failure path:

```text
Processing
→ Failed
→ ExpirationPending
→ Deleted/Purged
```

## Transcript states

```text
Draft
→ ReadyForReview
→ Saved
→ Versioned
→ Analyzed
```

Expiration path:

```text
Draft
→ ExpirationPending
→ Deleted/Purged
```

Case path:

```text
Saved
→ CaseRetained
```

## Derived analysis states

```text
Created
→ Analyzed
→ Retained with source
or
→ ExpirationPending
→ Deleted/Purged
```

## Export states

```text
Created
→ Exported
→ Downloaded
→ Deleted/Purged
```

Optional server-retained path:

```text
Created
→ Exported
→ Retained by explicit setting
→ ExpirationPending/DeleteRequested
→ Deleted/Purged
```

---

# Artifact Retention Matrix

| Artifact | Default | Retention Trigger | Expiration / Deletion |
|---|---|---|---|
| Recording/audio upload | Ephemeral | Upload for transcription | Delete after successful transcription; failed audio max 24h retry/debug TTL |
| Transcription provider artifact | Temporary | Transcription job | Purge after transcript reconciliation; retain only non-content metadata if needed |
| Transcript draft | Temporary | Paste/import/audio transcript creation | Expire after configurable draft TTL, recommended 7 days |
| Saved transcript | Durable | Explicit save, keep-after-analysis, or case assignment | Retain until user deletion |
| Transcript version | Evidence integrity artifact | Analysis, report, case dependency | Retain while dependent evidence/report/case exists |
| Evidence quote | Derived evidence artifact | Finding/report/graph dependency | Delete with transcript version or dependent report/case |
| Reflection run / workflow run | Derived processing artifact | Analysis execution | Inherit source transcript/report/case retention |
| Finding / hypothesis / reflection point | Derived analysis artifact | Reflection run completion | Inherit evidence-basis retention |
| Reasoning graph node/edge | Derived structured artifact | Analysis/synthesis | Inherit evidence-basis retention |
| Report | User-facing derived artifact | Report generation over transcript version | Retain only with retained source transcript/case |
| Case | Durable longitudinal artifact | Explicit case creation / assignment | Retain until user deletion |
| Export | Portable user artifact | Explicit export action | Download-only by default; optional server retention must be explicit |
| Logs/telemetry | Operational artifact | System operation | Operational retention only; no transcript bodies or sensitive content |

---

# Deletion Semantics

## Delete recording

Deletes audio bytes and transient transcription artifacts.

Does not delete a saved transcript created from the recording.

## Delete transcript draft

Deletes draft transcript, draft versions, draft evidence, draft analysis outputs, and temporary reports.

## Save transcript

Promotes a draft to durable user-retained artifact.

Saving should set or imply a durable retention rule.

## Assign transcript to case

Promotes transcript and dependent evidence basis to case-retained durability.

This should be visible as a privacy-significant action.

## Delete saved transcript

Deletes or renders inaccessible:

- transcript versions
- evidence quotes
- reflection runs
- findings
- hypotheses
- reflection points
- graph nodes/edges derived from the transcript
- reports
- case links

If the transcript belongs to a case, the user should be warned that longitudinal history will change.

## Remove transcript from case

Removes the longitudinal association.

It should not automatically delete the transcript unless the user chooses deletion.

## Delete case

The user must choose between:

```text
delete case wrapper only
```

and:

```text
delete case and contained retained transcripts
```

The destructive option must be explicit.

## Delete report

Deletes report view/materialization and report-specific derived artifacts.

It should not delete the source transcript unless the user explicitly chooses source deletion.

## Delete export

Deletes server-retained export bytes and export metadata subject to audit/event policy.

Downloaded user copies are outside the application boundary.

---

# Proposed Domain Additions for Later Implementation

These are architecture targets, not implementation tasks for 002-C.

## SourceArtifact / RecordingArtifact

Purpose:

Represent transient source artifacts such as audio uploads.

Candidate fields:

```text
id
owner_id
artifact_type
storage_ref
source_type
state
created_at
expires_at
deleted_at
purged_at
linked_transcript_id
failure_reason
retry_count
retention_rule_id
```

## RetentionRule

Purpose:

Represent artifact retention policy.

Candidate fields:

```text
id
artifact_class
default_policy
retention_trigger
ttl_seconds
inherits_from_artifact_id
cascade_policy
requires_user_intent
is_durable
deletion_mode
created_at
updated_at
```

## ArtifactLifecycleEvent

Purpose:

Provide non-content auditability for sensitive lifecycle changes.

Candidate fields:

```text
id
owner_id
artifact_id
artifact_class
event_type
previous_state
new_state
reason
created_at
metadata_without_sensitive_content
```

## ExportArtifact

Purpose:

Represent deliberate portable outputs.

Candidate fields:

```text
id
owner_id
source_report_id
source_transcript_version_id
format
state
storage_ref
created_at
downloaded_at
expires_at
deleted_at
retention_rule_id
```

---

# Required Background Processes

Later implementation planning should account for:

1. recording purge worker
2. transcription artifact purge worker
3. draft expiration worker
4. deletion cascade worker
5. derived artifact cleanup worker
6. export expiration worker
7. lifecycle event logging
8. retention policy evaluation

All jobs must be idempotent and safe to retry.

---

# Required User-Facing Signals

The UI should eventually make the following visible:

- audio will be deleted after transcription
- failed audio retry window
- draft expiration date
- save/promote action
- case assignment retention effect
- report evidence basis / transcript version
- deletion cascade preview
- export download/retention behavior

Detailed UI language belongs to 002-G.

---

# Handoff to 002-D

002-D should define how this lifecycle model is protected by:

- owner scope
- authentication boundary
- authorization checks
- infrastructure encryption
- application/field-level encryption target
- log redaction
- export encryption
- least-privilege service access
- deletion audit events without sensitive content

---

# Non-goals

002-C does not implement:

- database migrations
- TTL workers
- object storage lifecycle rules
- encryption strategy
- UI warnings
- API changes
- prompt changes

Those remain blocked until Phase 002-I authorizes an implementation phase.

---

# Acceptance Result

The lifecycle and retention architecture is ready to feed 002-D and later implementation sequencing.

Proceed next to:

```text
002-D — Privacy Boundary and Encryption Architecture Plan
```
