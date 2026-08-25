# 002-C — Data Lifecycle and Retention Architecture Plan

## Status

Complete.

This subgroup translates the accepted data lifecycle and retention decisions into architecture planning requirements.

---

# Purpose

002-C resolves the lifecycle and retention gaps identified in 002-B before privacy/encryption architecture planning begins.

It answers:

- How should recordings move through the system?
- How should transcript drafts become durable or expire?
- What makes a transcript durable?
- How do transcript versions, evidence, reports, and cases affect retention?
- What should deletion cascade to?
- How should exports be treated?
- What needs to be handed to 002-D for privacy and encryption architecture?

---

# Outputs

| Output | Document |
|---|---|
| Data lifecycle and retention architecture plan | `../architecture/002c_data_lifecycle_retention_architecture_plan.md` |
| Artifact retention matrix | `../inventories/002c_artifact_retention_matrix.md` |

---

# Accepted Decisions

## 1. Recording lifecycle needs explicit architecture

Audio is an ephemeral input artifact.

Architecture should model recording/audio as a transient source artifact boundary, not only as `SourceType.AUDIO`.

## 2. Retention Rule needs first-class semantics

Every artifact class should have an explicit retention policy, even if the first implementation uses configuration and background jobs instead of a dedicated table.

## 3. Transcript remains the durable center

The durable product value is the transcript-centered reflection record.

`Transcript` can remain the practical aggregate root unless later planning requires a separate `ConversationRecord` object.

## 4. Drafts are temporary

Transcript drafts expire unless saved, kept after analysis, or assigned to a case.

Recommended default remains:

```text
7 days
```

## 5. Case assignment implies retention

Assigning a transcript to a case is a privacy-significant action because it promotes transcript/version/evidence history to durable longitudinal retention.

## 6. Derived artifacts inherit evidence-basis retention

Findings, hypotheses, reflection points, graph objects, synthesis outputs, and reports should not outlive their transcript version/case evidence basis unless exported intentionally.

## 7. Exports are explicit

Exports are deliberate portable artifacts.

Default architecture should be download-oriented and avoid long-term server retention unless explicitly configured.

---

# Resolved 002-B Gaps

| 002-B Gap | 002-C Resolution |
|---|---|
| Recording lifecycle is not first-class enough | Add SourceArtifact / RecordingArtifact lifecycle boundary as architecture target |
| Retention Rule is not a first-class domain concept | Add RetentionRule semantics and artifact retention matrix |
| Export artifact needs explicit semantics | Add ExportArtifact semantics and download-first retention default |
| Conversation Record aggregate needs clarification | Keep Transcript as practical aggregate root for now; defer separate ConversationRecord unless needed |

---

# Handoff to 002-D

002-D should now define the privacy and encryption posture for every lifecycle artifact:

- recording/audio upload
- transcription artifacts
- transcript draft
- saved transcript
- transcript version
- evidence quote
- reflection run
- finding
- hypothesis
- reflection point
- reasoning graph object
- report
- case
- export
- logs/telemetry

---

# Non-goals

002-C does not implement:

- schema migrations
- retention workers
- object storage lifecycle rules
- encryption
- UI warnings
- API changes
- deployment changes

Implementation remains blocked until Phase 002-I exit review authorizes the next phase.

---

# Exit Criteria

002-C is complete when:

- recording lifecycle architecture target is defined
- retention rule semantics are defined
- artifact retention matrix exists
- deletion cascade semantics are documented
- export retention behavior is documented
- 002-D handoff is explicit

All criteria are satisfied.

---

# Next Phase

Proceed to:

```text
002-D — Privacy Boundary and Encryption Architecture Plan
```
