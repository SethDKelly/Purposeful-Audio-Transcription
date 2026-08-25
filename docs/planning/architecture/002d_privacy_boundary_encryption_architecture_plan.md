# 002-D Privacy Boundary and Encryption Architecture Plan

## Status

Accepted as the Phase 002-D architecture plan.

This document translates the accepted privacy, ownership, encryption, and redaction decisions into architecture requirements for later implementation phases.

It does not authorize code, schema, infrastructure, or deployment changes by itself.

---

# Purpose

Define how sensitive conversation artifacts should be protected across intake, retention, analysis, corpus-level reasoning, export, deletion, logs, and future enterprise expansion.

This plan builds on:

- `docs/concepts/005_security_privacy_retention_concepts.md`
- `docs/concepts/014_retention_and_encryption_decision.md`
- `docs/planning/architecture/002c_data_lifecycle_retention_architecture_plan.md`
- `docs/planning/inventories/002c_artifact_retention_matrix.md`

---

# Accepted Privacy Principle

```text
Sensitive conversation data is private by default, owner-scoped, minimized by default, encrypted when retained, never exposed through logs, and never used outside the user's explicit retained/case/corpus scope.
```

---

# Architecture Decision Summary

## 1. Owner scope is mandatory on retained sensitive artifacts

Every retained sensitive artifact should be owner-scoped in the personal-mode architecture.

Near-term owner scope may be a single personal owner/operator, but the data model should not rely on global implicit ownership.

Sensitive retained artifacts should carry or inherit owner scope from their parent artifact.

## 2. Privacy Boundary becomes an architecture layer

`Privacy Boundary` should be represented as a cross-cutting architecture concern, not a single table or service.

It includes:

- identity/session boundary
- owner/artifact boundary
- service authorization boundary
- encryption boundary
- logging/telemetry boundary
- export boundary
- deletion/audit boundary
- corpus reasoning boundary

## 3. Corpus reasoning is allowed only through explicit scope

The product should support deeper reasoning across multiple transcripts because a single conversation often provides limited evidence.

However, multi-transcript reasoning must be scoped.

Allowed scopes:

```text
single transcript version
selected transcript set
case evidence corpus
explicit future corpus/workspace scope
```

Default rule:

```text
Do not silently use all retained transcripts across the account.
```

The user should intentionally select or confirm the retained case/corpus scope that the reasoning graph may use.

## 4. Case Evidence Corpus is a privacy-sensitive reasoning boundary

A `Case Evidence Corpus` is the retained set of transcript versions, evidence quotes, findings, hypotheses, reports, graph objects, and longitudinal summaries associated with a case.

It exists to enrich evidence over time.

It should allow the reasoning graph to distinguish:

- single-conversation evidence
- recurring evidence across multiple conversations
- contradictory evidence across conversations
- evidence that strengthens a pattern over time
- evidence that weakens or contextualizes a pattern over time
- temporal changes in communication patterns

Every corpus-level claim must preserve evidence lineage back to source transcript versions and quote IDs.

## 5. Application-level encryption is the target for retained sensitive content

Infrastructure encryption is required baseline protection.

Application-level or field-level encryption is the target maturity posture for retained transcripts, transcript versions, evidence quotes, findings, hypotheses, reflection points, reports, cases, corpus summaries, and retained exports.

## 6. Logs and telemetry must remain content-free

Logs may include operational metadata, IDs, counts, durations, status, and error categories.

Logs must not include transcript bodies, evidence quote text, audio content, prompt payloads, model responses, export content, secrets, session tokens, or login codes.

## 7. Deletion must affect corpus reasoning

If a transcript, transcript version, evidence quote, or report is deleted, corpus-level reasoning graph objects derived from that evidence must be deleted, invalidated, or marked stale according to deletion policy.

Corpus-level conclusions must not survive as unsupported claims after their evidence basis is removed.

---

# Privacy Boundary Layers

## 1. Identity and session boundary

Near-term mode:

```text
personal owner/operator
```

Requirements:

- authenticated access before sensitive content is available
- no frontend secrets
- short-lived session/token posture where practical
- secure wake/login path for personal cost-state mode
- future compatibility with stronger identity providers

## 2. Owner and artifact boundary

Every retained artifact should be associated with an owner directly or through a parent artifact.

Examples:

```text
owner -> transcript -> transcript version -> evidence quote -> finding/report/graph
owner -> case -> case evidence corpus -> longitudinal graph
owner -> export artifact
```

Derived artifacts inherit owner scope from their evidence basis.

## 3. Service authorization boundary

Only authorized services should access decrypted sensitive content, and only for the active purpose.

Examples:

- transcription service may access staged audio only during transcription
- analysis worker may access transcript version text only during the reflection run
- export service may access report content only during export generation
- purge worker may access identifiers and storage refs needed for deletion, not content bodies

## 4. Encryption boundary

Retained sensitive content should be encrypted at rest.

Baseline:

- encrypted database storage
- encrypted object storage
- encrypted secrets
- TLS in transit where available
- least-privilege IAM

Target:

- application-level or field-level encryption for sensitive retained fields
- KMS-backed envelope encryption direction
- decrypt only inside authenticated/session-bound or worker-bound execution paths

## 5. Logging and telemetry boundary

Telemetry should explain operations without leaking content.

Allowed:

- artifact IDs
- owner IDs or hashed/pseudonymous IDs where appropriate
- status
- counts
- durations
- event names
- error categories
- lifecycle states

Forbidden:

- audio bytes or transcripts
- transcript bodies
- evidence quote text
- prompt bodies
- raw model completions
- report bodies
- export content
- login codes
- session tokens
- secrets

## 6. Export boundary

Exports are explicit user actions.

Default architecture:

```text
generate -> download -> do not retain long-term server-side
```

If retained server-side, export artifacts require:

- owner scope
- retention rule
- encryption
- deletion path
- lifecycle event
- source transcript version binding

## 7. Corpus reasoning boundary

Corpus reasoning may use multiple transcripts only when the transcript set is explicit.

Allowed corpus scopes:

- one case
- explicitly selected transcript versions
- future explicit workspace/corpus scope

Not allowed by default:

- account-wide hidden corpus analysis
- cross-case inference without user confirmation
- use of expired drafts in durable corpus reasoning
- use of deleted or stale transcript versions as active evidence

---

# Encryption Target Model

## Baseline implementation posture

Early implementation may rely on infrastructure encryption while the field-level model is designed.

Baseline controls remain mandatory:

- RDS encryption
- S3 encryption
- Secrets Manager encryption
- TLS where available
- least-privilege IAM
- private subnets/security groups where practical
- redacted logs
- no sensitive content in telemetry

## Target personal-use maturity

Use application-level or field-level encryption for retained sensitive content.

Candidate target model:

```text
KMS-managed master key
→ data encryption key
→ encrypted sensitive fields
→ decrypt only inside authorized request/worker context
```

Personal mode may use one owner-scoped key domain initially.

Future enterprise mode may introduce organization/workspace/key hierarchy.

## Field encryption candidates

Target encrypted fields include:

- transcript raw text
- normalized turn text
- transcript version text/snapshot
- evidence quote text and surrounding context
- finding summaries where sensitive
- psychological hypotheses
- reflection points
- synthesis/report body
- case notes
- longitudinal/corpus summaries
- graph node/edge labels and rationales where sensitive
- export content when retained server-side

## Metadata caution

Metadata may remain queryable where necessary, but metadata can still be sensitive.

Examples needing review:

- case title
- transcript title
- speaker display names
- session labels
- dates
- tags
- safety flags
- diagnosis-related user-supplied context

---

# Corpus Evidence and Reasoning Graph Requirements

## Evidence lineage

Every corpus-level graph claim must be traceable to:

```text
case/corpus scope
→ transcript id
→ transcript version id
→ evidence quote id
→ finding/hypothesis/report/graph node or edge
```

## Pattern strength

Corpus-level reasoning may increase pattern confidence only when multiple independent transcript versions provide supporting evidence.

Repeated claims copied from earlier reports should not be treated as new evidence.

## Contradiction and change

Corpus reasoning must preserve evidence that contradicts or qualifies earlier patterns.

Longitudinal graph enrichment should support:

- pattern recurrence
- pattern weakening
- pattern change over time
- context-specific differences
- insufficient evidence across corpus

## Deletion impact

Deleting a transcript or transcript version should trigger review of corpus graph objects that depend on it.

Possible outcomes:

- delete dependent corpus object
- recompute corpus object
- mark corpus object stale
- lower confidence
- remove evidence edge

Implementation details belong to later phases, but the architecture must preserve this possibility.

---

# Artifact Privacy and Encryption Classification

Detailed artifact classification lives in:

```text
docs/planning/inventories/002d_artifact_privacy_encryption_matrix.md
```

High-level classification:

| Artifact Family | Sensitivity | Owner Scope | Encryption Target |
|---|---|---|---|
| Recording/audio | Very high | Direct owner scope | Temporary encrypted object storage; delete quickly |
| Transcript/version/turn/evidence | Very high | Owner via transcript | Application-level encryption target |
| Findings/hypotheses/reflection points | High to very high | Inherit evidence owner | Application-level encryption target |
| Reports/cases/corpus summaries | Very high | Owner/case scope | Application-level encryption target |
| Exports | Very high | Direct owner scope | Encrypt if retained server-side |
| Logs/telemetry | Low only if content-free | Operational scope | No sensitive bodies allowed |

---

# Required Architecture Controls

Later implementation planning should include:

1. owner scope on retained artifacts
2. authorization checks for every sensitive content read
3. lifecycle-aware deletion permissions
4. content-free logs and telemetry
5. encryption-at-rest baseline verification
6. application-level encryption design for retained content
7. scoped corpus selection for multi-transcript reasoning
8. evidence lineage for corpus graph enrichment
9. deletion/staleness propagation for corpus graph objects
10. export generation and retention controls
11. non-content lifecycle audit events
12. future key hierarchy compatibility

---

# Non-goals

002-D does not implement:

- encryption code
- schema migrations
- key management infrastructure
- authentication changes
- RBAC
- corpus graph recomputation
- export encryption
- log pipeline changes
- deployment changes

Implementation remains blocked until Phase 002-I exit review authorizes the next phase.

---

# Handoff to 002-E

002-E should use this plan to define privacy-aware architecture for:

- bounded psychological hypotheses
- safety-aware override state
- prompt and model-output validation
- evidence-limited reasoning
- corpus-aware confidence calibration
- multi-transcript graph enrichment without overclaiming
- non-diagnostic output rules

---

# Acceptance Result

The privacy boundary and encryption architecture is ready to feed 002-E and later implementation sequencing.

Proceed next to:

```text
002-E — Analysis Boundary, Hypothesis, and Safety Architecture Plan
```
