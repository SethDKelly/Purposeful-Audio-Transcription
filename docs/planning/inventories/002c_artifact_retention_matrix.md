# 002-C Artifact Retention Matrix

## Status

Accepted as the Phase 002-C artifact retention matrix.

---

# Purpose

Provide a compact artifact-by-artifact retention reference for Phase 002 architecture planning.

This matrix is governed by:

- `docs/concepts/013_data_lifecycle_decision.md`
- `docs/concepts/014_retention_and_encryption_decision.md`
- `docs/planning/architecture/002c_data_lifecycle_retention_architecture_plan.md`

---

# Matrix

| Artifact | Durable by Default? | Default Retention | Promotion Trigger | Deletion Trigger | Derived Artifacts |
|---|---:|---|---|---|---|
| Recording/audio upload | No | Delete after successful transcription | Explicit future audio-save feature only; deferred | Successful transcription, failed retry TTL expiry, user delete | Transcription job artifacts |
| Failed transcription audio | No | Max 24h retry/debug TTL | None by default | Retry success, TTL expiry, user delete | Error metadata without content may remain |
| Transcription provider artifact | No | Until transcript reconciliation | None by default | Reconciliation complete, TTL expiry | Transcript draft |
| Transcript draft | No | Recommended 7 days | Explicit save, keep-after-analysis, case assignment | Draft TTL expiry, user delete | Draft versions, draft evidence, draft reports |
| Saved transcript | Yes | Until user deletion | Explicit save / keep action | User delete | Versions, evidence, reflection runs, reports |
| Case transcript | Yes | Until user deletion or case/transcript deletion | Case assignment | User delete transcript or destructive case deletion | Longitudinal findings, summaries, graph links |
| Transcript version | Conditionally | While dependent evidence/report/case exists | Analysis/report/case dependency | Source transcript deletion or no remaining dependency | Evidence quotes, version-bound findings |
| Evidence quote | Conditionally | With transcript version/report dependency | Finding/report/graph citation | Source version/report deletion | Findings, graph edge evidence |
| Reflection run | Conditionally | Inherits source transcript/report/case policy | Analysis execution | Source deletion, draft expiry, user delete report | Module/lens runs, findings, reports |
| Finding | Conditionally | Inherits evidence basis | Reflection run completion | Source evidence/report deletion | Constructs, reflection points |
| Psychological hypothesis | Conditionally | Inherits evidence basis | Hypothesis-aware reflection output | Source evidence/report deletion | Support/contradiction/alternative records |
| Reflection point | Conditionally | Inherits report/source policy | Finding/report generation | Report/source deletion | None; may link back to finding/evidence |
| Reasoning graph node/edge | Conditionally | Inherits evidence basis | Analysis/synthesis graph creation | Source evidence/report/case deletion | Longitudinal graph summaries |
| Report | Conditionally | With retained transcript/case | Report generation | User delete report or source transcript deletion | Export |
| Case | Yes | Until user deletion | Explicit case creation | User delete case wrapper or destructive case delete | Longitudinal outputs |
| Export | No by default | Download-only by default | Explicit export action | Download completion, expiry, user delete | Portable file outside app boundary after download |
| Logs/telemetry | Operational only | Operational retention window | System operation | Log retention expiry | None; must not include sensitive bodies |

---

# Promotion Rules

## Draft to durable transcript

A draft becomes durable only when the user does one of the following:

- explicit save
- explicit keep-after-analysis
- assignment to a case

## Transcript to case-retained transcript

A transcript becomes case-retained when assigned to a case.

Case assignment implies durable longitudinal retention and should be treated as privacy-significant.

## Report to export

A report becomes an export only through explicit user action.

Export generation must preserve source transcript version identity.

---

# Cascade Rules

## Draft deletion cascade

Deleting or expiring a draft deletes:

- draft transcript text
- draft transcript versions
- draft evidence quotes
- draft reflection runs
- draft findings/hypotheses/reflection points
- draft reports

## Saved transcript deletion cascade

Deleting a saved transcript deletes or renders inaccessible:

- transcript versions
- evidence quotes
- reflection runs
- findings
- hypotheses
- reflection points
- reasoning graph nodes/edges
- reports
- case links

## Case deletion options

The user must choose between:

```text
delete case wrapper only
```

and:

```text
delete case and contained retained transcripts
```

## Export deletion

Server-retained export deletion removes export bytes and export metadata according to policy.

Downloaded copies are outside the application boundary.

---

# 002-D Handoff

Every artifact in this matrix needs a privacy/encryption posture in 002-D.

At minimum, 002-D should classify each artifact by:

- owner scope
- sensitivity
- encryption target
- logging restriction
- deletion/audit event requirements
