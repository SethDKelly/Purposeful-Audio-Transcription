# 002-G UI/UX Concept Alignment Plan

## Status

Accepted as the Phase 002-G UI/UX concept alignment plan.

This document translates the accepted concept and architecture decisions into user-facing language, flow, report, warning, and navigation requirements for later implementation phases.

It does not authorize UI implementation, component changes, copy changes, frontend rewrites, or product branding changes by itself.

---

# Purpose

Ensure the product experience reflects the accepted concept design.

The UI should make the product feel like:

```text
a secure, evidence-linked conversation reflection system
```

not:

```text
a transcription utility
an AI therapist
a diagnosis engine
a workplace surveillance tool
a generic chatbot
a legal or clinical adjudication system
```

This plan builds on:

- `docs/concepts/011_product_identity_decision.md`
- `docs/concepts/012_concept_boundary_decision.md`
- `docs/concepts/013_data_lifecycle_decision.md`
- `docs/concepts/014_retention_and_encryption_decision.md`
- `docs/concepts/015_hypothesis_reflection_boundary.md`
- `docs/concepts/016_therapeutic_lens_language_decision.md`
- `docs/concepts/017_safety_boundary_decision.md`
- `docs/planning/architecture/002c_data_lifecycle_retention_architecture_plan.md`
- `docs/planning/architecture/002d_privacy_boundary_encryption_architecture_plan.md`
- `docs/planning/architecture/002e_analysis_boundary_hypothesis_safety_architecture_plan.md`
- `docs/planning/architecture/002f_cost_state_personal_deployment_architecture_plan.md`

---

# Accepted UX Principle

```text
Every user-facing surface should make scope, evidence, uncertainty, retention, safety posture, and cost state understandable without turning the product into diagnosis, therapy, surveillance, or raw transcription tooling.
```

---

# Architecture Decision Summary

## 1. Product framing should be reflection-first, transcript-enabled

The UI may include audio upload and transcription flows, but transcription should appear as an input path.

The durable product center should be presented as:

- transcripts
- transcript versions
- evidence quotes
- reflection runs
- findings
- hypotheses
- reflection points
- reports
- cases
- case evidence corpus
- reasoning graph

Avoid making the main UI feel like an audio processing dashboard.

## 2. Every analysis surface should show evidence scope

Before and after analysis, the user should understand whether the output is based on:

```text
single transcript version
selected transcript set
case evidence corpus
```

The UI should not hide corpus use.

The user should be able to inspect which transcript versions and evidence quotes support a report or graph claim.

## 3. Case Evidence Corpus needs explicit UI presence

Cases are not merely folders.

A case should be presented as a privacy-significant longitudinal evidence boundary.

The UI should help the user understand that assigning a transcript to a case enables retained multi-transcript reasoning and graph enrichment.

## 4. Report language must preserve analysis boundaries

Reports should communicate observations, findings, hypotheses, support levels, alternatives, limitations, safety posture, reflection points, and evidence basis.

Reports should not communicate diagnosis, treatment plans, legal conclusions, hidden intent as fact, or personality labels as settled identity.

## 5. Reflection Point should replace Recommendation / Intervention language

User-facing guidance should use `Reflection Point` or similar non-prescriptive language.

Avoid default labels such as:

```text
Recommendation
Intervention
Treatment plan
Clinical guidance
```

unless a future phase explicitly scopes a professional mode.

## 6. Safety posture must be visible when relevant

Safety-aware framing should not be hidden inside report prose.

Elevated or high-risk safety posture should affect:

- report header or banner
- section ordering
- suppressed ordinary mutual-improvement prompts
- reflection point availability
- support-category language
- export/report limitations

The UI must avoid pressuring confrontation, repair, or reconciliation in high-risk contexts.

## 7. Retention and deletion must be visible

The user should understand:

- audio is deleted after transcription by default
- failed audio has a short retry/debug window
- transcript drafts expire unless saved or assigned to a case
- saved transcripts are durable until deleted
- case assignment implies durable longitudinal retention
- deleting a transcript affects reports, evidence, graph objects, and case history
- exports are explicit and download-oriented by default

## 8. Cost State should feel intentional, not broken

Personal-mode sleep/wake should be reflected in user-facing language.

The UI should explain that sleep is a cost-saving mode.

Wake latency should not look like product failure.

Failed wake should be actionable.

## 9. Security posture should be calm but visible

The UI should communicate privacy and owner control without overwhelming the user.

It should make clear that retained sensitive content is private, owner-scoped, and subject to retention/deletion controls.

Do not expose implementation details such as KMS, RDS, S3, internal service names, or secret-management mechanics in ordinary user flows.

---

# Primary User-Facing Concepts

Use these concepts consistently:

| Concept | User-Facing Meaning |
|---|---|
| Transcript | Text record of a conversation |
| Transcript Version | Stable evidence basis used for a report or run |
| Evidence Quote | Specific transcript excerpt supporting a claim |
| Reflection Run | Analysis execution over a declared evidence scope |
| Reflection Lens | Bounded reasoning perspective applied to evidence |
| Therapeutic Reflection Lens | Reflection lens informed by therapeutic traditions without clinical authority |
| Psychological Hypothesis | Evidence-limited reflective explanation, not a diagnosis |
| Finding | Evidence-backed insight with confidence and limits |
| Reflection Point | Non-prescriptive prompt for self-review |
| Case | Longitudinal grouping of related transcripts |
| Case Evidence Corpus | Retained case evidence used for multi-transcript reasoning |
| Safety Posture | Evidence-linked caution state affecting report framing |
| Export | Deliberate portable artifact |
| Cost State | Availability/cost posture such as asleep, waking, active, idle pending |

---

# Core User Flows

## 1. Intake flow

Purpose:

Create a transcript from paste, file, import, or audio.

UX requirements:

- make audio retention default visible
- make transcript draft status visible
- separate upload/transcription from durable retention
- show draft expiration when applicable
- prompt save or case assignment when durable memory is desired

## 2. Transcript review flow

Purpose:

Prepare a transcript for evidence-linked reflection.

UX requirements:

- show transcript readiness
- support speaker/turn review where applicable
- show version creation before analysis when relevant
- clarify that analysis binds to a transcript version

## 3. Save / retain / case assignment flow

Purpose:

Convert a temporary draft into durable retained evidence.

UX requirements:

- distinguish save from analyze
- explain that saved transcripts are retained until deleted
- explain that case assignment enables longitudinal reasoning
- warn that case membership is retention-significant and privacy-significant

## 4. Analysis setup flow

Purpose:

Declare evidence scope and selected lenses before reflection.

UX requirements:

- choose single transcript, selected transcript set, or case evidence corpus
- show included transcript versions
- show requested reflection lenses
- allow user-provided context/hypotheses without implying diagnosis
- preview whether output will be single-transcript or corpus-level

## 5. Report review flow

Purpose:

Inspect evidence-backed output.

UX requirements:

- report scope header
- transcript version basis
- lens list
- safety posture when relevant
- findings with evidence quotes
- hypotheses with support levels and alternatives
- confidence and limitations
- reflection points
- evidence appendix or expandable evidence

## 6. Case / corpus flow

Purpose:

Use multiple retained transcripts to enrich reasoning over time.

UX requirements:

- show which transcripts belong to a case
- show included transcript versions
- show corpus evidence count
- distinguish recurrence from single-conversation evidence
- show contradictions and weakening evidence, not only strengthening evidence
- show stale/deleted evidence effects when applicable

## 7. Deletion flow

Purpose:

Help the user delete data with clear cascade awareness.

UX requirements:

- preview what will be deleted or invalidated
- distinguish deleting a report from deleting its source transcript
- distinguish removing a transcript from a case from deleting the transcript
- show that deleted evidence can affect corpus-level graph claims
- avoid accidental destructive action

## 8. Export flow

Purpose:

Create a deliberate portable artifact.

UX requirements:

- show export scope
- include transcript version/report basis
- preserve boundary language and limitations
- make server retention behavior explicit
- clarify downloaded copies are outside app boundary

## 9. Cost-state flow

Purpose:

Help the personal owner understand availability.

UX requirements:

- show asleep/waking/active/idle-pending/shutting-down/failed-wake/maintenance status
- explain cost-saving sleep
- show active jobs keeping the app awake
- support manual wake/sleep/keep-awake when implemented
- make failed wake actionable

---

# Report UX Requirements

Every report should answer these user-facing questions:

1. What evidence scope was used?
2. Which transcript versions support this report?
3. Which lenses were applied?
4. Which claims are directly observed?
5. Which claims are hypotheses?
6. What evidence supports each finding?
7. What evidence contradicts or limits each hypothesis?
8. What alternatives should be considered?
9. What confidence or support level is assigned?
10. Is there a safety posture affecting the report?
11. Which reflection points are offered, if any?
12. What can the product not conclude?

---

# Safety UX Requirements

Safety posture should be represented carefully.

Suggested user-facing posture labels:

| Architecture Value | User-Facing Label |
|---|---|
| `none_detected` | No specific safety concern identified in this evidence |
| `elevated_caution` | Elevated caution |
| `high_risk` | High-risk safety indicators |
| `immediate_or_crisis_indicators` | Immediate or crisis indicators |

Rules:

- Safety labels must not imply legal or clinical conclusions.
- Safety explanations must cite evidence.
- Elevated/high-risk posture should suppress unsafe reflection points.
- Support language should remain category-level and careful.
- The product should not present itself as crisis support.

---

# Hypothesis UX Requirements

Hypotheses should be presented with structure, not as labels.

A hypothesis section should show:

```text
hypothesis name
source
scope
support level
evidence for
evidence against or missing evidence
alternative explanations
confidence
limitations
non-diagnostic boundary
```

Use support labels such as:

- observed behavior
- consistent with hypothesis
- partially consistent with hypothesis
- contradicts hypothesis
- insufficient evidence
- alternative explanation likely

Avoid:

- confirmed
- diagnosed
- proved
- clinically established
- pathological
- this person is...

---

# Corpus UX Requirements

Corpus-level UI should make depth visible without overstating certainty.

Show:

- corpus scope
- number of transcript versions included
- time span if known
- included/excluded transcript versions
- recurrence count
- contradiction count or summary
- context splits
- temporal changes
- stale/deleted evidence status when relevant

Avoid:

- hidden account-wide analysis
- `always` / `never` language
- treating report conclusions as new evidence
- counting duplicate quotes as independent evidence

---

# Cost-State UX Requirements

Recommended user-facing descriptions:

| Cost State | User-Facing Copy Direction |
|---|---|
| Asleep | The app is asleep to reduce personal operating cost. |
| Waking | The app is waking required services. This may take a moment. |
| Active | The app is active and ready. |
| IdlePending | The app may sleep soon because there is no recent activity or blocking work. |
| ShuttingDown | The app is shutting down expensive resources safely. |
| FailedWake | The app could not wake successfully. Show retry/support details. |
| Maintenance | The app is intentionally unavailable for maintenance. |

Avoid language that implies data loss or analysis failure merely because the app is asleep.

---

# Navigation Model Recommendation

Later UI planning should consider navigation around these top-level areas:

```text
Home / Dashboard
Transcripts
Cases
Reports
Evidence / Graph
Exports
Settings / Retention
System Status
```

Near-term personal mode does not need enterprise navigation such as organizations, workspaces, team management, HR review, billing admin, clinician-client hierarchy, or compliance review.

---

# Handoff to 002-H

002-H should convert this UI/UX alignment into backlog items and acceptance gates, including:

- terminology replacement plan
- report header/scope design
- evidence quote display requirements
- hypothesis section requirements
- safety banner requirements
- retention/delete flow requirements
- case corpus UI requirements
- export boundary requirements
- cost-state status UI requirements
- legacy UI copy audit

---

# Non-goals

002-G does not implement:

- React components
- page layouts
- visual design system
- copy changes
- routing changes
- report rendering changes
- graph UI
- export UI
- deployment status UI
- authentication UI

Implementation remains blocked until Phase 002-I exit review authorizes the next phase.

---

# Acceptance Result

The UI/UX concept alignment plan is ready to feed 002-H refactor backlog and acceptance gates.

Proceed next to:

```text
002-H — Refactor Backlog, Sequencing, and Acceptance Gates
```
