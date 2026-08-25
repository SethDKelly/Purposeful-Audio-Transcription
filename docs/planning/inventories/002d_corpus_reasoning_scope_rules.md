# 002-D Corpus Reasoning Scope Rules

## Status

Accepted as the Phase 002-D corpus reasoning privacy and evidence-scope rules.

---

# Purpose

Ensure subsequent uploaded transcripts can enrich the reasoning graph while preserving privacy, evidence lineage, user intent, and deletion semantics.

A single conversation can provide limited evidence. Multiple conversations can reveal stronger patterns, contradictions, trends, and changes over time.

This document defines how that deeper evidence may be used safely.

---

# Core Rule

```text
Multi-transcript reasoning is allowed and important, but only inside an explicit retained evidence scope.
```

The system must not silently use every retained transcript in the account as a hidden corpus.

---

# Accepted Corpus Scopes

## 1. Single Transcript Scope

Uses one transcript version.

Appropriate for:

- first analysis
- narrow review
- one-conversation report
- evidence-limited findings

## 2. Selected Transcript Set

Uses explicitly selected transcript versions.

Appropriate for:

- comparing several known conversations
- testing whether a pattern repeats
- user-controlled ad hoc longitudinal review

## 3. Case Evidence Corpus

Uses all retained transcript versions intentionally assigned to a case.

Appropriate for:

- longitudinal analysis
- reasoning graph enrichment
- recurring pattern detection
- change-over-time review
- case-level synthesis

## 4. Future Explicit Corpus / Workspace Scope

Deferred for later enterprise or advanced personal modes.

This may support:

- workspaces
- projects
- organizations
- sharing grants
- role-based access

Not part of near-term implementation unless explicitly planned.

---

# Not Allowed by Default

The system should not default to:

- hidden account-wide transcript analysis
- cross-case reasoning without confirmation
- use of expired drafts in durable corpus reasoning
- use of deleted transcript versions
- use of raw audio as corpus evidence after transcription
- treating prior model conclusions as new evidence
- treating duplicate quotes as independent support

---

# Evidence Lineage Requirement

Every corpus-level claim must preserve lineage:

```text
corpus scope
→ transcript id
→ transcript version id
→ evidence quote id
→ finding/hypothesis/graph object
→ corpus-level conclusion
```

A user should be able to inspect which conversations support a corpus-level pattern.

---

# Corpus Graph Enrichment Types

The reasoning graph may use multi-transcript evidence to represent:

| Enrichment Type | Meaning |
|---|---|
| Recurrence | Similar pattern appears across multiple transcript versions |
| Contradiction | Later or different evidence weakens a prior interpretation |
| Strengthening | Additional independent evidence increases support |
| Weakening | New evidence reduces confidence or narrows scope |
| Context split | Pattern appears in one context but not another |
| Temporal change | Pattern changes across sessions/conversations |
| Insufficient corpus evidence | Corpus is too small, inconsistent, or incomplete |

---

# Confidence Rules

Corpus-level confidence may increase only when:

- supporting evidence comes from multiple transcript versions
- evidence is independently grounded in transcript quotes
- evidence is not merely repeated from an earlier report
- alternatives and contradictions are considered
- the corpus scope is clear

Corpus-level confidence should decrease or remain cautious when:

- all evidence comes from one transcript
- context differs substantially across conversations
- speaker identity is uncertain
- evidence is sparse or ambiguous
- safety or diagnostic implications are possible
- evidence contradicts the hypothesized pattern

---

# Case Evidence Corpus

A `Case Evidence Corpus` is the near-term preferred corpus boundary.

It contains retained artifacts intentionally associated with a case:

- transcript versions
- evidence quotes
- findings
- hypotheses
- reflection points
- reports
- reasoning graph nodes/edges
- longitudinal summaries

Case membership is therefore both:

```text
retention-significant
privacy-significant
```

---

# User-Facing Requirements

Later UI planning should make corpus use visible.

The user should be able to see:

- which case/corpus is being used
- how many transcripts are included
- which transcript versions are included
- whether a report is single-transcript or corpus-level
- which evidence quotes support each corpus claim
- whether deleted or stale evidence affected a graph object

Detailed UI language belongs to 002-G.

---

# Deletion and Staleness Rules

Deleting or expiring a transcript/version should affect corpus-level artifacts derived from it.

Possible later implementation responses:

- delete dependent graph objects
- recompute affected corpus summaries
- mark affected graph objects stale
- lower confidence
- remove evidence edges
- require user review before reusing the corpus report

Architecture must preserve this possibility.

---

# Privacy Rules

Corpus reasoning must obey:

- owner scope
- explicit case/corpus scope
- retention rules
- encryption posture
- log redaction
- deletion cascade rules
- export boundaries

Corpus summaries and corpus graph objects are sensitive retained content and should be treated as application-level encryption targets.

---

# 002-E Handoff

002-E should define how corpus reasoning affects:

- hypothesis support levels
- confidence calibration
- safety-aware override behavior
- report language
- non-diagnostic framing
- graph edge evidence rules
- contradiction handling

---

# Decision

The project should preserve and strengthen multi-transcript reasoning.

The architecture should support deeper evidence through explicit case/corpus scope, not hidden account-wide inference.
