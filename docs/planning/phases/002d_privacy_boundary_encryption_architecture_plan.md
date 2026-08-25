# 002-D — Privacy Boundary and Encryption Architecture Plan

## Status

Complete.

This subgroup translates the accepted privacy, ownership, encryption, corpus-scope, and logging decisions into architecture planning requirements.

---

# Purpose

002-D defines how sensitive conversation artifacts should be protected before analysis-boundary planning begins.

It answers:

- What is the privacy boundary?
- How should owner scope work in personal mode?
- Which artifacts require encryption posture?
- What must never appear in logs?
- How should exports be bounded?
- How can multi-transcript reasoning enrich the reasoning graph safely?
- How should deletion affect corpus-level graph objects?
- What must be handed to 002-E for hypothesis, safety, and analysis architecture?

---

# Outputs

| Output | Document |
|---|---|
| Privacy boundary and encryption architecture plan | `../architecture/002d_privacy_boundary_encryption_architecture_plan.md` |
| Artifact privacy and encryption matrix | `../inventories/002d_artifact_privacy_encryption_matrix.md` |
| Corpus reasoning scope rules | `../inventories/002d_corpus_reasoning_scope_rules.md` |

---

# Accepted Decisions

## 1. Privacy Boundary is cross-cutting architecture

Privacy is not a single table or feature.

It spans:

- identity/session boundary
- owner/artifact boundary
- service authorization boundary
- encryption boundary
- logging/telemetry boundary
- export boundary
- deletion/audit boundary
- corpus reasoning boundary

## 2. Owner scope is mandatory for retained sensitive artifacts

Every retained sensitive artifact should carry or inherit owner scope.

Near-term personal mode may have one owner/admin/user, but the architecture should not rely on globally unowned sensitive content.

## 3. Application-level encryption is the target maturity posture

Infrastructure encryption remains the required baseline.

Application-level or field-level encryption is the target for retained transcripts, transcript versions, evidence, findings, hypotheses, reflection points, reports, cases, corpus summaries, and retained exports.

## 4. Logs and telemetry must be content-free

Logs may include IDs, counts, durations, status, lifecycle events, and error categories.

Logs must not include audio, transcript bodies, evidence quote text, prompt bodies, raw model completions, report bodies, export content, login codes, session tokens, or secrets.

## 5. Corpus reasoning is allowed only through explicit scope

Multi-transcript reasoning is important and should be preserved.

Subsequent transcripts can enrich the reasoning graph, but only when they are part of an explicit retained evidence scope.

Allowed near-term scopes:

```text
single transcript version
selected transcript set
case evidence corpus
```

Default rule:

```text
Do not silently use all retained transcripts across the account.
```

## 6. Case Evidence Corpus is the preferred near-term corpus boundary

A case may act as the retained multi-transcript evidence corpus.

Case-level reasoning can strengthen, weaken, contradict, or contextualize patterns across conversations when every claim preserves source evidence lineage.

## 7. Deletion must affect corpus reasoning

Corpus-level graph claims must not survive unsupported after their evidence basis is deleted.

Later implementation must support deletion, invalidation, recomputation, stale marking, or confidence reduction for affected corpus graph objects.

---

# Resolved / Advanced 002-C Handoff Items

| 002-C Handoff | 002-D Resolution |
|---|---|
| Owner scope | Owner scope is required on retained sensitive artifacts directly or by inheritance |
| Authentication boundary | Sensitive content requires authenticated access; detailed auth implementation remains later work |
| Authorization checks | Every sensitive content read should be service-purpose scoped |
| Infrastructure encryption | Required baseline |
| Application-level encryption | Target maturity posture for retained sensitive content |
| Log redaction | Content-free logs only |
| Export encryption | Required if exports are retained server-side |
| Deletion audit events | Allowed only as non-content lifecycle events |
| Multi-transcript corpus use | Allowed through explicit selected set or case evidence corpus |

---

# Handoff to 002-E

002-E should use 002-D to define architecture for:

- bounded psychological hypotheses
- confidence calibration across single-transcript and corpus-level evidence
- safety-aware override behavior
- diagnostic-framework-informed reasoning without diagnostic authority
- prompt/input scope controls
- output validation and report language
- corpus-aware reasoning graph enrichment
- contradiction and alternative explanation handling

---

# Non-goals

002-D does not implement:

- encryption code
- key management
- schema migrations
- authentication changes
- RBAC
- corpus graph recomputation
- export encryption
- log pipeline changes
- deployment changes

Implementation remains blocked until Phase 002-I exit review authorizes the next phase.

---

# Exit Criteria

002-D is complete when:

- privacy boundary layers are defined
- owner scope is accepted as mandatory for retained artifacts
- encryption maturity posture is defined
- artifact privacy/encryption matrix exists
- logs/telemetry restrictions are documented
- corpus reasoning scope rules are documented
- 002-E handoff is explicit

All criteria are satisfied.

---

# Next Phase

Proceed to:

```text
002-E — Analysis Boundary, Hypothesis, and Safety Architecture Plan
```
