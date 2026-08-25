# 009 — Refactor Mapping

## Purpose

Map the current implementation to the concept design without making this document an implementation plan.

This document identifies which current parts of the application appear conceptually valid, which need renaming, and which may be accidental complexity.

---

# Current Product Naming

## Current Repository Name

```text
Purposeful Audio Transcription
```

## Conceptual Issue

The name emphasizes audio transcription, but transcription is only an input path.

The deeper product is conversation reflection and structured evidence-based analysis.

## Recommendation

Consider renaming or repositioning the product around:

- private conversation reflection
- evidence-based conversation analysis
- relationship reasoning
- reflective transcript analysis
- conversation evidence studio

Do not rename immediately without deciding product identity.

---

# Current Implementation Mapping

| Current Implementation Area | Concept It Serves |
|---|---|
| Audio upload/transcribe | Recording, Audio Staging, Transcript |
| Transcript preparation workspace | Transcript, Transcript Version |
| Evidence quote IDs | Evidence Quote |
| Analysis modules | Lens |
| Module outputs | Finding, Confidence, Reflection Point |
| Synthesis | Reasoning Graph, Report |
| Ontology | Reasoning Graph |
| Cases | Case, Longitudinal Analysis |
| Safety mode | Safety-Aware Framing |
| Email OTP/session auth | Privacy Boundary, User Session |
| AWS sleep/wake | Cost State |
| Exports | Export |
| Worker queue | Reflection Run |
| Telemetry/log redaction | Privacy Boundary, Cost/Operations |

---

# Concepts That Appear Strong

The following current concepts appear directionally correct:

- Transcript
- Evidence Quote
- Finding
- Confidence
- Lens
- Case
- Reasoning Graph
- Safety-Aware Report
- Cost State
- Export

These should likely be preserved.

---

# Concepts That Need Clarification

## Recording

Clarify whether audio is ephemeral by default.

## Transcript Retention

Clarify whether transcripts are retained by default or only when saved/promoted.

## Psychological Hypothesis

Current modules may imply hypotheses, but the product needs a formal concept for hypothesis-aware reflection without diagnosis.

## Reflection Point

The product needs a clearer distinction between findings and user-facing reflection prompts.

## Cost State

The sleep/wake system should be documented as a product operating concept, not just AWS ops.

## Privacy Boundary

Security docs exist, but privacy should become a first-class concept.

---

# Refactor Direction

After concept design is accepted, refactor should proceed by asking:

1. Which concept does this code support?
2. Is the concept named in the docs?
3. Does the implementation preserve the concept’s invariants?
4. Does the UI expose the concept clearly?
5. Does the data model support the concept safely?
6. Does the implementation leak internal machinery to the user?
7. Does the concept compose correctly with security, retention, and cost state?

---

# Likely Refactor Themes

## 1. Rename Product Layers

Clarify:

```text
input layer: recording/transcription
core layer: transcript/evidence/reflection
analysis layer: lenses/hypotheses/findings
memory layer: cases/longitudinal patterns
operations layer: cost state/security
```

## 2. Separate Recording from Transcript

Do not allow recording retention to piggyback on transcript retention.

## 3. Add Hypothesis-Aware Reflection

Formalize hypothesis handling:

```text
hypothesis
→ evidence support
→ evidence contradiction
→ alternatives
→ confidence
→ reflection questions
```

## 4. Make Retention Explicit

Every artifact should have a retention rule.

## 5. Make Cost State Visible

User should understand asleep, waking, active, idle, and shutdown.

## 6. Reduce User Exposure to Internal Modules

Users should choose analysis intent/depth, not necessarily module graphs.

## 7. Strengthen Case Promotion

Longitudinal tracking should be opt-in and conceptually tied to retained transcripts.

---

# Refactor Non-Goals

Do not immediately:

- rewrite everything
- remove working infrastructure
- specialize for enterprise
- add clinician-only workflows
- add broad collaboration
- rename the repository without product identity decision
- remove AWS sleep/wake behavior
- abandon current evidence/graph work
