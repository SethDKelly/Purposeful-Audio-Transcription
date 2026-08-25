# 013 — Data Lifecycle Decision

## Status

Accepted as the current data lifecycle decision for concept design and refactor planning.

This document defines how conversation data should move through the product from recording or transcript intake through reflection, retention, export, and deletion.

---

# Decision Summary

The product should treat data lifecycle as a first-class concept.

The application may analyze transcripts derived from recordings, but recordings are not the durable center of the product.

The durable product value is the transcript-centered reflection record: transcript versions, evidence quotes, findings, hypotheses, confidence, reasoning graph, reflection points, reports, and longitudinal case memory.

## Default Lifecycle Principle

```text
Capture only what is needed.
Keep raw audio only briefly.
Retain transcripts only by user intent.
Bind analysis to transcript versions.
Encrypt retained sensitive content.
Delete cascades must be explicit and meaningful.
```

---

# Artifact Classes

## 1. Recording

### Role

A recording is an input artifact.

It exists to produce a transcript.

### Lifecycle

```text
created/uploaded
→ staged
→ transcribing
→ transcribed
→ deleted
```

### Default Decision

Audio is ephemeral by default.

After successful transcription, audio should be deleted automatically.

If transcription fails, audio may be retained only for a short retry window.

### Retry Window

Recommended initial maximum:

```text
24 hours
```

A shorter configured default is preferable once retry behavior is reliable.

### Explicit Long-Term Audio Retention

Explicit long-term audio retention is out of scope for the default product concept.

If it is added later, it must require deliberate user action and clear warning.

---

## 2. Transcription Job Artifact

### Role

A transcription job artifact is an intermediate processing artifact.

Examples include provider job IDs, temporary output files, speaker-label source data, and normalized turn-generation inputs.

### Lifecycle

```text
created
→ processed
→ reconciled into transcript
→ purged
```

### Default Decision

Transcription artifacts should be temporary and purged after the transcript is created and verified.

Provider/job metadata may be retained only when needed for audit, debugging, or cost visibility, and should not include transcript bodies unless explicitly required.

---

## 3. Transcript Draft

### Role

A transcript draft is a prepared or partially prepared transcript that has not yet been intentionally retained.

### Lifecycle

```text
created
→ prepared
→ ready to analyze
→ saved/promoted
or
→ expired/deleted
```

### Default Decision

Transcript drafts should not automatically become permanent memory.

Recommended initial retention:

```text
7 days unless saved or assigned to a case
```

This is a product default, not a hard implementation requirement. The exact duration may be configurable.

---

## 4. Saved Transcript

### Role

A saved transcript is a durable user-retained artifact.

### Lifecycle

```text
draft
→ saved
→ versioned
→ analyzed
→ optionally assigned to case
→ retained until deleted
```

### Default Decision

A transcript becomes durable only through user intent:

- explicit save
- assignment to a case
- explicit keep-after-analysis action

Saved transcripts should be encrypted and owner-scoped.

---

## 5. Transcript Version

### Role

A transcript version preserves evidence integrity.

### Lifecycle

```text
created from transcript state
→ bound to evidence and analysis
→ superseded by later version
→ retained while dependent reports/cases exist
```

### Default Decision

Every analysis must bind to a transcript version.

Old versions should remain available while reports, evidence, or case history depend on them.

Editing a transcript after analysis creates a new version rather than mutating the prior evidence basis.

---

## 6. Evidence Quote

### Role

An evidence quote connects a finding to exact transcript text.

### Lifecycle

```text
created from transcript version
→ cited by finding/report/graph edge
→ retained with dependent analysis
→ deleted when transcript version/dependent artifacts are deleted
```

### Default Decision

Evidence quotes are not free-floating artifacts.

They are scoped to transcript versions and retained only while the related transcript version or report exists.

---

## 7. Reflection Run

### Role

A reflection run processes one transcript version through one or more lenses.

### Lifecycle

```text
queued
→ running
→ completed/failed/canceled
→ retained or expired according to source transcript policy
```

### Default Decision

If a reflection run is performed on an unsaved draft, the analysis result should either expire with the draft or prompt the user to save/promote the transcript.

If a reflection run is performed on a saved transcript or case transcript, results may be retained until deleted.

---

## 8. Finding / Hypothesis / Reflection Point

### Role

These are analysis artifacts derived from transcript evidence.

### Lifecycle

```text
generated
→ evidence-linked
→ reviewed
→ retained with report/case
→ deleted with source transcript/version/report
```

### Default Decision

Findings, hypotheses, and reflection points should inherit the retention policy of the transcript/report/case that produced them.

They should not survive deletion of their evidence basis unless exported intentionally.

---

## 9. Report

### Role

A report is a user-facing view over structured analysis.

### Lifecycle

```text
generated
→ reviewed
→ exported or retained
→ deleted by user or cascade
```

### Default Decision

Reports are retained only if their source transcript is retained.

Reports must declare the transcript version they were generated from.

---

## 10. Case

### Role

A case groups transcripts for longitudinal reflection.

### Lifecycle

```text
created
→ transcripts assigned
→ longitudinal analysis generated
→ retained until deleted
```

### Default Decision

Assigning a transcript to a case implies durable retention of that transcript and its needed versions, evidence, and analysis outputs.

Case membership is therefore a privacy-significant user action.

---

## 11. Export

### Role

An export is a deliberate portable artifact created by the user.

### Lifecycle

```text
requested
→ generated
→ downloaded or retained according to explicit setting
→ deleted/expired
```

### Default Decision

Exports should be explicit and not silently retained long-term by the application.

If retained server-side, exports must have their own retention policy.

---

# Deletion Semantics

## Delete Recording

Deletes staged audio and related temporary processing artifacts.

Does not necessarily delete the transcript if the transcript has been saved.

## Delete Transcript Draft

Deletes draft transcript, draft evidence, draft analysis outputs, and temporary reports.

## Delete Saved Transcript

Deletes transcript versions, evidence, findings, reflection runs, reports, and case links unless the user chooses a narrower unlink operation where supported.

## Remove Transcript from Case

Removes longitudinal association.

It should not automatically delete the transcript unless the user explicitly chooses deletion.

## Delete Case

The user must choose between:

```text
delete case wrapper only
```

or

```text
delete case and contained retained transcripts
```

The destructive option must be explicit.

---

# Data Lifecycle Invariants

- Audio is not durable by default.
- Transcript drafts expire unless saved or promoted.
- Saved transcripts are durable until deleted.
- Case assignment implies durable retention.
- Analysis binds to transcript versions.
- Reports must identify their evidence basis.
- Derived analysis artifacts inherit source retention.
- Deletion must cascade meaningfully.
- Exports are explicit user actions.
- Sensitive retained artifacts should be encrypted.

---

# Deferred Implementation Details

This decision does not yet define:

- exact database schema
- exact TTL implementation
- exact background purge mechanism
- exact encryption library or KMS strategy
- exact UI copy
- exact export storage mechanism

Those belong in later implementation design.
