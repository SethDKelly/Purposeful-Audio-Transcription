# 005 — Evidence Snapshots and Transcript Versioning

## Phase Goal

Ensure old reports remain linked to the exact transcript/evidence version used during analysis.

This phase protects the evidence traceability tenet after transcript edits.

**Design:** [../../developer/evidence_snapshot_versioning_design.md](../../developer/evidence_snapshot_versioning_design.md)

---

# Target Model

```text
Transcript
TranscriptVersion
EvidenceQuote
WorkflowRun(transcript_version_id)
FindingEvidence(evidence_quote_id)
ConstructEvidence(evidence_quote_id)
RelationshipEvidence(evidence_quote_id)
```

---

# Versioning Rules

## Rule 1

New workflow runs use the current transcript version.

## Rule 2

Editing a transcript after analysis creates a new transcript version.

## Rule 3

Old reports remain bound to the original transcript version.

## Rule 4

Quote IDs are version-scoped, not globally unique.

## Rule 5

Case-level evidence must include transcript ID and transcript version ID.

---

# Implementation Tasks

## Database

- [ ] Add `transcript_versions` table.
- [ ] Add `current_version_id` to transcripts.
- [ ] Add `transcript_version_id` to evidence quotes.
- [ ] Add `transcript_version_id` to workflow runs.
- [ ] Ensure finding/construct/relationship evidence references stable evidence quote row IDs.
- [ ] Add migration/backfill for existing transcripts.

## Services

- [ ] Update transcript creation to create version 1.
- [ ] Update transcript editing to create a new version when prior analysis exists.
- [ ] Update evidence index creation to attach to transcript version.
- [ ] Update workflow run creation to bind to transcript version.
- [ ] Update report APIs to read evidence from the workflow run version.
- [ ] Update case/longitudinal services to include transcript/version identity.

## UI

- [ ] Show report transcript version.
- [ ] Warn when transcript has changed after report generation.
- [ ] Add option to re-run analysis on latest version.
- [ ] Show evidence from the correct version.

## Tests

- [ ] Old report still resolves evidence after transcript edit.
- [ ] Reanalysis uses latest transcript version.
- [ ] Quote ID collision across versions is handled correctly.
- [ ] Case report identifies transcript/session/version for evidence.
- [ ] User cannot mutate old report evidence by editing transcript.

---

# Acceptance Criteria

- Old reports remain evidence-valid after transcript edits.
- Workflow runs record transcript version.
- Quote IDs are version-scoped.
- Case-level reports identify transcript/version for each quote.
- Reanalysis uses the latest version.
- UI communicates when a report is based on an older transcript version.
