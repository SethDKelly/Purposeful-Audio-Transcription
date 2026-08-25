# 001 — Product Premise

## Working Product Definition

The application is a secure conversation analysis and reflection system.

It analyzes transcripts, which may be derived from recordings, using evidence-based psychological, behavioral, therapeutic, cognitive, and relational lenses to support personal reflection, longitudinal understanding, and communication improvement.

## Plain-Language Description

The user records, uploads, or pastes a conversation. The application converts it into a transcript, preserves evidence, analyzes it through multiple reflective lenses, and produces structured findings that link back to exact transcript quotes.

The user can review patterns over time, especially when transcripts are grouped into cases.

## What the Product Is For

The product helps a user ask:

- What happened in this conversation?
- What did each person actually say?
- What evidence supports a finding?
- What communication patterns may be present?
- What cognitive or behavioral patterns may be influencing the interaction?
- What therapeutic reflection points may be useful?
- What changed across conversations?
- What should I reflect on before acting or speaking again?

## What the Product Is Not For

The product is not for:

- diagnosing a person
- proving a personality disorder
- determining abuse as a settled fact
- deciding who is right
- proving malicious intent
- replacing therapy
- replacing mediation
- producing clinical advice
- producing legal conclusions
- surveilling people
- retaining sensitive recordings unnecessarily

## Premise Example

A user may know or suspect that one person has schizoid personality disorder and another exhibits traits associated with borderline or narcissistic personality organization.

The product should not diagnose either person.

But it may help the user examine transcript evidence for communication patterns that could be consistent with user-provided hypotheses, such as:

- withdrawal
- emotional distancing
- fear of engulfment
- fear of abandonment
- invalidation
- escalation
- defensive self-protection
- splitting-like language
- contempt-like language
- control attempts
- repair avoidance
- unmet needs
- cognitive distortions
- emotional dysregulation signals

The output should be framed as:

```text
The transcript contains evidence that may be consistent with this reflective hypothesis.
```

Not:

```text
This person has this disorder.
```

## Permitted Hypothesis Use

The application may support hypothesis-aware reflection.

A hypothesis can be:

- user-provided
- module-suggested as possible
- derived from repeated patterns
- framed as evidence-limited
- used to ask better reflective questions

A hypothesis must not become a diagnosis, label, verdict, prediction, character judgment, justification for harm, or substitute for professional evaluation.

## Initial Use Contexts

The application should support transcripts from:

- personal relationship conversations
- personal therapy sessions, if legally and ethically recorded and appropriate
- business meetings
- difficult conversations
- reflective journaling conversations
- coaching or mediation-adjacent conversations
- longitudinal personal cases

The product should remain general enough for these contexts without specializing too early.

## Primary Product Tension

```text
Longitudinal reflection needs retained transcripts.
Privacy argues for deletion and minimization.
```

## Proposed Resolution

Audio is ephemeral by default.

Transcripts are durable only when the user chooses to retain them, ideally through explicit save or case promotion.

Retained transcripts and analysis outputs should be encrypted and owner-scoped.

Cases provide longitudinal continuity without requiring raw recordings to persist.

## Product North Star

The product should feel like a private evidence-backed reflection workspace for conversations — not a transcription app, diagnostic AI therapist, workplace surveillance tool, or generic chatbot.
