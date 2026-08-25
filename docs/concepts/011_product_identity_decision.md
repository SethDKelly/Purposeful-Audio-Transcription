# 011 — Product Identity Decision

## Status

Accepted as the current working product identity for concept design.

This is not necessarily the final brand name. It is the naming and identity decision that should guide documentation, refactor planning, user-facing language, and future implementation work until deliberately superseded.

---

# Decision Summary

The product should no longer be conceptually defined as an audio transcription application.

Audio transcription is an input path.

The product is a secure conversation analysis and reflection system.

## Canonical Product Description

Use this as the canonical product description in concept and planning docs:

```text
A secure conversation analysis and reflection system that uses evidence-linked transcripts, psychological and behavioral reflection lenses, confidence calibration, and longitudinal case memory to help a user examine communication patterns without diagnosing people or making clinical/legal determinations.
```

## Working Product Identity

Use this working identity in concept docs:

```text
Secure Conversation Analysis and Reflection System
```

This is intentionally descriptive rather than brand-like.

The product may later receive a shorter public-facing name, but the concept design should not depend on branding yet.

---

# Name Roles

## Purposeful Audio Transcription

### Decision

Treat `Purposeful Audio Transcription` as the historical repository name and legacy project shell, not the product concept.

### Rationale

The phrase overemphasizes transcription. The concept reset establishes that the durable product value is not audio transcription; it is private, evidence-based conversation reflection over transcripts that may come from recordings.

### Allowed Use

- repository slug until renamed
- historical references
- migration notes

### Avoid Use

- product identity
- user-facing value proposition
- core concept docs except as history

---

## Relationship Reasoning Engine / RRE

### Decision

Retain `Relationship Reasoning Engine (RRE)` as the internal analysis-engine identity.

### Rationale

RRE accurately describes the structured reasoning component: evidence, findings, lenses, constructs, graph relationships, confidence, synthesis, and longitudinal comparisons.

However, it is too technical and too narrow to be the entire product identity.

### Allowed Use

- internal engine layer
- architecture diagrams
- developer docs
- analysis workflow references
- code/package names where already established

### Avoid Use

- final user-facing product name unless later accepted deliberately
- description of the entire product boundary

---

## Audio Transcription

### Decision

Classify audio transcription as an input capability.

### Rationale

A user may provide audio, but the product's durable artifacts are transcripts, evidence, reflections, findings, reports, and cases.

### Correct Framing

```text
Recordings may be transcribed into transcripts for reflection.
```

### Incorrect Framing

```text
The product is an audio transcription app.
```

---

## Conversation Analysis

### Decision

Use `conversation analysis` as a broad product capability, not as a narrow academic-method claim.

### Rationale

The product analyzes conversations in a practical sense across communication, behavioral, psychological, therapeutic, and longitudinal lenses. It is not claiming to implement only the formal academic discipline of Conversation Analysis.

### Correct Framing

```text
The application analyzes conversation transcripts through evidence-linked reflection lenses.
```

---

## Therapeutic Reflection

### Decision

Use `therapeutic reflection` or `therapeutic reflection lenses` instead of `clinical analysis` where possible.

### Rationale

The product may use CBT-style, DBT-style, psychodynamic, behavioral, attachment-informed, and trauma-informed lenses, but it is not providing therapy, diagnosis, or treatment.

### Correct Framing

```text
CBT-style reflection lens
DBT-style interpersonal effectiveness reflection
psychodynamic hypothesis-aware reflection
trauma-informed communication reflection
```

### Avoid Framing

```text
clinical diagnosis
therapeutic treatment plan
personality disorder detection
```

---

# Product Identity Hierarchy

Use this hierarchy going forward:

```text
Product category:
  Secure conversation analysis and reflection system

Working product identity:
  Secure Conversation Analysis and Reflection System

Internal engine identity:
  Relationship Reasoning Engine (RRE)

Input capability:
  Audio transcription

Durable artifact layer:
  Transcript, Evidence Quote, Reflection Run, Finding, Case, Report

Future deployment mode:
  Enterprise policy layer
```

---

# Product North Star

The product should feel like:

```text
A private evidence-backed reflection workspace for conversations.
```

It should not feel like:

```text
an audio transcription utility
an AI therapist
a diagnostic tool
a workplace surveillance tool
a generic chatbot
a legal/clinical adjudication system
```

---

# User-Facing Positioning Drafts

## Short Positioning

```text
Private evidence-backed reflection for important conversations.
```

## Medium Positioning

```text
A secure conversation reflection system that turns transcripts into evidence-linked insights, reflection points, and longitudinal patterns without diagnosing people or replacing professional judgment.
```

## Technical Positioning

```text
A transcript-centered reasoning system that combines evidence indexing, confidence-calibrated findings, psychological and behavioral reflection lenses, and longitudinal graph-based synthesis.
```

---

# Design Implications

## Documentation

Future docs should avoid leading with audio transcription. They should lead with transcript-based conversation reflection.

## UI

The UI should not organize the product primarily around recordings. It should organize around conversations, transcripts, reflections, evidence, cases, and reports.

## Architecture

Audio ingestion should be a replaceable input pipeline. The core analysis system should operate on prepared transcript versions.

## Security

Security should be described around sensitive conversation data, not just uploaded audio files.

## Cost Model

Personal low-cost sleep/wake remains a deployment/operating concept, not the product identity.

---

# Deferred Branding Question

A final brand name remains deferred.

Possible future naming directions:

- Conversation Reflection Engine
- Conversation Evidence Studio
- Reflective Conversation Analysis
- Relationship Reasoning Engine
- Private Conversation Reflection
- Purposeful Reflection

Do not perform a repository rename until a final product/brand decision is made.

---

# Acceptance Criteria

This decision is accepted when:

- product docs stop treating audio transcription as the core product
- RRE is retained as internal engine identity
- transcript-based reflection becomes the central product identity
- future refactor phases use this terminology consistently
- naming remains descriptive until branding is deliberately revisited
