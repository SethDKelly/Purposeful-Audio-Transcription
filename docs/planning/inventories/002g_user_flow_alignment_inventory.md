# 002-G User Flow Alignment Inventory

## Status

Accepted as the Phase 002-G user flow alignment inventory.

---

# Purpose

Map core future user flows to the accepted concept model so later implementation can build screens without losing concept authority.

This inventory does not specify visual design, routing, component hierarchy, or implementation tasks.

---

# Flow Inventory

## 1. Home / Dashboard

### Purpose

Orient the personal owner to current system, data, and work state.

### Must show or link to

- current Cost State
- recent transcripts
- recent cases
- draft expirations
- active or recent reflection runs
- reports needing review
- active blocking jobs when relevant
- privacy/retention status where useful

### Concept risks

- turning the dashboard into an audio-job queue only
- hiding that drafts can expire
- hiding that case assignment affects retention
- hiding cost-state status

---

## 2. Intake: paste/import/upload/audio

### Purpose

Create a transcript or transcript draft.

### Must show or link to

- source type
- audio deletion default if audio is used
- draft status
- draft expiration behavior
- save/promote options
- transcript review readiness

### Required boundary language

```text
Audio is used to create a transcript and is deleted after successful transcription by default.
```

### Concept risks

- implying uploaded audio is durable by default
- implying transcription equals saved transcript
- treating source artifact as product center

---

## 3. Transcript Review

### Purpose

Prepare a transcript before evidence-linked reflection.

### Must show or link to

- transcript title/session metadata
- speaker/turn review where applicable
- current version status
- analysis readiness
- excluded turns if supported
- save/promote state

### Required boundary language

```text
Analysis binds to a transcript version so evidence can be inspected later.
```

### Concept risks

- allowing analysis without stable evidence basis where later reports depend on it
- hiding version changes
- making transcript editing silently mutate past evidence

---

## 4. Save / Retain Transcript

### Purpose

Promote a draft to durable retained evidence.

### Must show or link to

- saved transcript retention meaning
- owner scope
- deletion path
- case assignment option
- draft expiration bypass

### Required boundary language

```text
Saved transcripts are retained until you delete them.
```

### Concept risks

- saving silently without retention notice
- using vague labels such as `done` or `finish`
- not distinguishing draft from retained transcript

---

## 5. Case Assignment

### Purpose

Add a transcript to a longitudinal evidence boundary.

### Must show or link to

- case name
- included transcript versions
- corpus reasoning implications
- durable retention implication
- remove-from-case vs delete-transcript distinction

### Required boundary language

```text
Adding a transcript to a case makes it part of the retained case evidence corpus for longitudinal reflection.
```

### Concept risks

- treating case as a simple folder
- hiding corpus reasoning effects
- hiding privacy/retention implications

---

## 6. Analysis Setup

### Purpose

Declare evidence scope and reflection lenses.

### Must show or link to

- analysis scope type
- included transcript versions
- selected case/corpus if applicable
- requested reflection lenses
- user-provided context/hypotheses
- safety and non-diagnostic boundary note

### Required scope options

```text
single transcript version
selected transcript set
case evidence corpus
```

### Concept risks

- `analyze all` without scope
- hidden account-wide corpus use
- lens labels that imply diagnosis or treatment
- user context treated as system-validated truth

---

## 7. Reflection Run Progress

### Purpose

Show analysis execution state without exposing prompt internals or sensitive logs.

### Must show or link to

- declared scope
- selected lenses
- run status
- blocking-job status when relevant
- cancellation policy if supported
- active job keeping app awake if relevant

### Concept risks

- showing prompt bodies or raw model output in ordinary UI
- hiding that active jobs block sleep
- calling run status `diagnosing`, `assessing`, or `treating`

---

## 8. Report Review

### Purpose

Inspect the evidence-linked reflection output.

### Must show or link to

- report scope
- transcript version basis
- lens list
- findings
- evidence quotes
- hypotheses and support levels
- alternatives / contradictions
- confidence and limitations
- safety posture if relevant
- reflection points
- export action

### Required boundary language

```text
This report supports reflection from selected evidence. It does not diagnose, prove intent, make legal conclusions, or replace professional judgment.
```

### Concept risks

- report reads like clinical verdict
- evidence hidden behind prose
- reflection points read like orders or treatment plans
- safety posture hidden or muted

---

## 9. Evidence / Reasoning Graph

### Purpose

Inspect how evidence, findings, hypotheses, reflection points, and corpus patterns relate.

### Must show or link to

- evidence quote nodes
- finding nodes
- hypothesis nodes
- support/contradiction/alternative edges
- corpus recurrence/weakening/strengthening edges
- confidence and limitations
- source transcript versions
- stale/deleted evidence status where applicable

### Concept risks

- graph edges imply causality without evidence
- corpus findings lose transcript lineage
- prior model outputs counted as evidence
- deleted evidence continues to support active conclusions silently

---

## 10. Case / Corpus Review

### Purpose

Review longitudinal evidence and changes over multiple retained transcripts.

### Must show or link to

- case transcripts
- included transcript versions
- corpus evidence count
- recurrence patterns
- contradictions
- temporal changes
- stale evidence or deleted evidence impact
- case-level reports

### Required boundary language

```text
Case-level conclusions are based on the retained transcripts assigned to this case, not all account history.
```

### Concept risks

- overgeneralizing from corpus to identity
- hiding contradictions
- using all retained transcripts without consent
- treating case as mere organization rather than evidence boundary

---

## 11. Delete / Remove / Expire

### Purpose

Let the user control retention and deletion safely.

### Must show or link to

- delete target
- cascade preview
- dependent reports/evidence/graph objects
- remove-from-case option
- destructive case deletion option
- export/download boundary

### Required boundary language

```text
Deleting this transcript may remove or invalidate evidence, reports, and corpus-level graph conclusions that depend on it.
```

### Concept risks

- delete action only hides UI row
- cascade consequences hidden
- remove-from-case confused with source deletion
- downloaded exports implied to be controlled after download

---

## 12. Export

### Purpose

Create a deliberate portable artifact.

### Must show or link to

- report/export scope
- included transcript version basis
- included evidence appendix if supported
- non-diagnostic/safety limitations
- server retention behavior
- deletion path if server-retained

### Required boundary language

```text
Exports are deliberate portable artifacts. Downloaded copies are outside the app boundary.
```

### Concept risks

- silent long-term server export retention
- exports drop limitations or evidence basis
- export appears to be a clinical or legal report

---

## 13. System Status / Cost State

### Purpose

Help the owner understand availability and cost behavior.

### Must show or link to

- current cost state
- wake progress
- idle pending state
- active jobs keeping system awake
- manual wake/sleep/keep-awake controls when implemented
- failed wake explanation
- maintenance state

### Required boundary language

```text
The app may sleep when idle to reduce personal operating cost.
```

### Concept risks

- sleep looks like crash/outage
- wake failure is silent
- user does not understand why app remains awake
- cost state is mixed with analysis state

---

# Cross-Flow Requirements

Every flow that touches sensitive retained data should preserve:

- owner scope
- evidence scope
- retention state
- deletion path
- content-free operational logs
- non-diagnostic boundary
- safety-aware framing where relevant

---

# Flow Acceptance Criteria for Later Implementation

A future UI implementation should not pass review if it:

1. Presents the product primarily as an audio transcription app.
2. Hides transcript version/evidence basis for reports.
3. Uses clinical, diagnostic, or treatment labels as product authority.
4. Presents hypotheses as diagnosis or identity labels.
5. Uses recommendations/interventions as default user-facing guidance.
6. Hides case/corpus scope for multi-transcript reasoning.
7. Treats safety posture as ordinary relationship coaching.
8. Hides deletion cascade effects.
9. Silently retains exports server-side.
10. Makes personal-mode sleep/wake look like product failure.

---

# Decision

Later UI work should be reviewed as concept implementation, not merely presentation work.

The UI is an authority surface: it can preserve or break the product boundary.
