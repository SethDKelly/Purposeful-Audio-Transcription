# 008 — Graph Relationship Evidence and Case Correctness

## Phase Goal

Deepen the structured reasoning graph by making relationships evidence-backed and fixing case/longitudinal evidence identity.

**Status:** Complete

---

# Part 1 — Graph Relationship Evidence

## Problem

Findings and constructs may be evidence-backed, but graph relationships also represent claims.

Example:

```text
Construct A reinforces Construct B.
```

That edge needs:

- relationship type
- confidence
- rationale
- evidence where possible
- alternative explanation if inferred

## Target Relationship Schema

```json
{
  "source_construct_id": "...",
  "target_construct_id": "...",
  "relationship_type": "reinforces",
  "rationale": "...",
  "confidence": "moderate",
  "evidence_quote_ids": ["Q012", "Q019"],
  "alternative_explanations": []
}
```

## Tasks

- [x] Update module output schema to allow/require relationship evidence.
- [x] Update parser and validator.
- [x] Update persistence layer.
- [x] Update graph merge to preserve relationship evidence.
- [x] Rewire edges when constructs are merged.
- [x] Merge duplicate edges after canonicalization.
- [x] Update React graph UI to show edge rationale/evidence.
- [x] Add graph-edge evidence coverage eval.

---

# Part 2 — Case and Longitudinal Evidence Correctness

## Problem

Quote IDs are only meaningful within a transcript/version.

Across a case:

```text
Transcript A / Q001
Transcript B / Q001
```

are different evidence items.

## Required Behavior

Case-level evidence references must include:

```text
transcript_id
transcript_version_id
evidence_quote_id
quote_id
```

Longitudinal claims must identify which session/transcript supports them.

## Tasks

- [x] Audit latest-run selection logic.
- [x] Fix any oldest-vs-latest completed run issue.
- [x] Add transcript/version identity to case-level evidence references.
- [x] Update longitudinal synthesis prompts/outputs to cite sessions.
- [x] Add tests with duplicate quote IDs across transcripts.
- [x] Ensure recurring pattern claims cite multiple transcripts.
- [x] Ensure single-session claims are not framed as longitudinal.

---

# Acceptance Criteria

- Graph relationships carry confidence/rationale/evidence where possible.
- Graph merge rewires and preserves relationship evidence.
- React graph edges are inspectable.
- Case-level evidence is transcript/version-specific.
- Longitudinal synthesis does not confuse quote IDs across transcripts.
- Latest completed runs are selected correctly.
- Recurring pattern claims cite multiple sessions.
