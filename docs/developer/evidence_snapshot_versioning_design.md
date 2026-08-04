# Evidence Snapshot and Transcript Versioning Design

## Purpose

This document defines how to preserve evidence integrity after transcript edits.

Evidence traceability requires that old reports continue to point to the exact transcript quotes used during analysis.

---

# Problem

If evidence quote IDs are regenerated after transcript edits, old reports may become misleading.

Example:

```text
Original report cites Q012.
User edits transcript.
Evidence index is rebuilt.
Q012 now refers to different text.
Old report becomes invalid.
```

---

# Proposed Model

```text
Transcript
  id
  owner_user_id
  current_version_id

TranscriptVersion
  id
  transcript_id
  version_number
  created_at
  created_by_user_id
  source_type
  change_summary
  is_current

EvidenceQuote
  id
  transcript_version_id
  quote_id
  turn_id
  speaker
  text
  start_char
  end_char
  evidence_type

WorkflowRun
  id
  transcript_id
  transcript_version_id
  workflow_id
  status

FindingEvidence
  finding_id
  evidence_quote_id

ConstructEvidence
  construct_id
  evidence_quote_id

RelationshipEvidence
  relationship_id
  evidence_quote_id
```

---

# Versioning Rules

## Rule 1 — New Analysis Uses Current Version

```text
workflow_run.transcript_version_id = transcript.current_version_id
```

## Rule 2 — Edits After Analysis Create New Version

If a transcript has associated completed workflow runs, edits create a new `TranscriptVersion`.

## Rule 3 — Old Reports Stay Bound

Existing reports remain bound to their original `transcript_version_id`.

## Rule 4 — Quote IDs Are Version-Scoped

`Q001` is unique only within a transcript version.

Globally unique evidence references should use `evidence_quote.id`.

---

# UI Requirements

The UI should show:

- transcript version used by a report
- whether transcript has changed since report was generated
- option to re-run analysis on latest version
- evidence quote text from the correct version

Example message:

```text
This report was generated from Transcript Version 2.
The transcript has since been edited. Re-run analysis to use the latest version.
```

---

# Acceptance Criteria

- Old reports remain valid after transcript edits.
- Quote IDs are version-scoped.
- Workflow runs always record transcript version.
- Reanalysis uses latest version.
- UI warns when report is not based on latest transcript version.
- Case reports identify transcript/session/version for each evidence item.
