# 012 — Conceptual Boundary Decision

## Status

Accepted as the current conceptual boundary for concept design and refactor planning.

This document defines what the product includes, excludes, and must treat cautiously.

---

# Boundary Summary

The application is a secure conversation analysis and reflection system.

It analyzes transcripts, which may be derived from recordings, using evidence-based psychological, behavioral, therapeutic, cognitive, relational, and longitudinal reflection lenses.

It supports reflection and self-understanding.

It does not diagnose, adjudicate, surveil, or replace professional judgment.

---

# In-Bounds Concepts

## 1. Conversation Record

A conversation record may begin as:

- pasted transcript
- uploaded transcript
- audio recording
- recorded business meeting
- personal therapy session transcript, when legally and ethically appropriate
- relationship conversation
- reflective journaling dialogue

## 2. Transcript

The transcript is the core durable analysis input.

The system may help prepare, segment, correct, version, and analyze transcripts.

## 3. Evidence Quote

Evidence quotes connect findings to exact transcript text.

Evidence should be concise, speaker-attributed, transcript-version-scoped, and expandable for context.

## 4. Reflection Run

A reflection run analyzes a transcript version through one or more lenses and produces structured findings, confidence, limitations, and synthesis.

## 5. Reflection Lens

The system may include lenses inspired by:

- communication analysis
- behavioral analysis
- CBT-style thought reflection
- DBT-style interpersonal effectiveness and emotion-regulation reflection
- psychodynamic or psychoanalytic hypothesis-aware reflection
- attachment-informed interaction analysis
- trauma-informed communication review
- conflict mapping
- mediation-style interests and impasses
- NVC observations, feelings, needs, and requests
- systems thinking
- narrative identity and meaning-making
- bias and reliability audit
- safety-aware review

## 6. Psychological Hypothesis

A psychological hypothesis is allowed as a reflection context.

The system may evaluate whether transcript evidence is:

```text
consistent with
partially consistent with
in tension with
contradicted by
insufficient for
better explained by alternatives
```

A hypothesis must remain evidence-limited and non-diagnostic.

## 7. Reflection Point

A reflection point helps the user consider possible changes in communication, interpretation, emotional regulation, assumptions, repair, validation, or boundary-setting.

Reflection points are not instructions, treatment plans, or determinations.

## 8. Case

A case groups related transcripts for longitudinal reflection.

Cases should be opt-in because they imply a durable memory posture.

## 9. Cost State

Cost State is in-bounds as a personal-mode operating concept.

The system may sleep, wake, become active, idle, and shut down to minimize cost.

## 10. Future Enterprise Policy Layer

Enterprise is in-bounds as a future policy/deployment layer.

It should not drive near-term complexity.

---

# Out-of-Bounds Concepts

The product must not be designed to do the following.

## 1. Diagnosis

The system must not diagnose mental health conditions, personality disorders, trauma disorders, attachment styles as fixed traits, or clinical conditions.

Forbidden style:

```text
This person has BPD.
This confirms narcissistic personality disorder.
This speaker is schizoid.
```

Allowed style:

```text
This exchange may be consistent with a user-provided hypothesis about emotional withdrawal, but the transcript is insufficient for diagnosis.
```

## 2. Legal or Clinical Adjudication

The system must not determine abuse, coercive control, harassment, discrimination, liability, workplace misconduct, or clinical risk as settled fact.

It may flag evidence that warrants careful review.

## 3. Intent as Fact

The system must not claim hidden intent unless the transcript directly states it.

Forbidden style:

```text
They were trying to manipulate you.
```

Allowed style:

```text
This wording may have a controlling effect, though intent is not established by the transcript.
```

## 4. Workplace Surveillance

The system must not be framed as a tool for covertly evaluating employees, identifying toxic people, or automating HR decisions.

Business meeting analysis is in-bounds only when framed around communication reflection, meeting improvement, conflict understanding, and evidence-based review.

## 5. Replacement for Therapy or Mediation

The product must not claim to replace therapy, mediation, coaching, or professional supervision.

It may support preparation, reflection, review, and evidence organization.

## 6. Covert Recording System

The product must not encourage illegal, unethical, or hidden recording.

Recording legality and consent remain user responsibilities and should be surfaced as a product caution where relevant.

---

# Caution-Zone Concepts

These concepts are allowed only with tight boundaries.

## Psychoanalytic / Psychodynamic Reflection

Allowed:

- defenses as hypotheses
- projection as a possible interpretive pattern
- shame defense as a possible hypothesis
- withdrawal as protective strategy
- attachment-relevant interaction patterns

Not allowed:

- definitive unconscious motive claims
- personality structure diagnosis
- psychoanalytic certainty

## Personality Disorder Context

Allowed:

- user-provided diagnosis as context
- user-provided suspicion as hypothesis
- evidence-consistency review
- alternatives and limitations

Not allowed:

- assigning a disorder
- validating a diagnosis
- suggesting a new diagnosis as fact
- using disorder labels as explanations without evidence

## CBT / DBT Reflection

Allowed:

- thought pattern reflection
- emotion regulation reflection
- interpersonal effectiveness reflection
- assumption checking
- behavior-impact review

Not allowed:

- treatment plan
- clinical instruction
- claim that a person needs a modality
- mental health advice beyond reflection

## Safety Analysis

Allowed:

- flagging threats, intimidation, stalking, coercion-like indicators, self-harm statements, severe control, or fear of harm
- safety-aware framing
- recommending appropriate professional or emergency support when warranted

Not allowed:

- adjudicating abuse as settled fact
- pressuring reconciliation
- mutualizing serious safety concerns
- minimizing safety indicators as ordinary conflict

---

# Context Boundaries

## Personal Relationship Conversations

In scope.

Primary use should be self-reflection, evidence review, communication improvement, pattern recognition, and longitudinal awareness.

## Therapy Session Transcripts

Conditionally in scope.

The system may help organize personal reflection from legally and ethically obtained transcripts, but it must not replace the therapist, reinterpret therapy as diagnosis, or undermine professional care.

## Business Meetings

In scope when framed as conversation reflection, meeting improvement, conflict understanding, and behavioral pattern review.

Out of scope when framed as surveillance, HR adjudication, or automated personnel evaluation.

## Coaching / Mediation-Adjacent Conversations

In scope when framed as preparation and reflection.

Out of scope when framed as professional replacement or legal/clinical determination.

---

# User Boundary

Near-term, the primary user is a single personal owner/operator.

This person may act as:

- user
- administrator
- data owner
- cost operator
- product evaluator

Do not introduce enterprise role complexity into the core product yet.

---

# Data Boundary

## Durable Core

The durable product center is:

```text
Transcript
Transcript Version
Evidence Quote
Finding
Reflection Point
Report
Case
Reasoning Graph
```

## Ephemeral Input

Recordings are ephemeral by default.

They should not become durable unless the user explicitly chooses retention.

---

# Boundary Tests

A feature is inside the product boundary if it helps the user answer:

- What does the transcript actually show?
- What evidence supports this reflection?
- How confident is this interpretation?
- What alternative explanations exist?
- What pattern might be recurring?
- What can I reflect on in my own communication?
- What should I be cautious about?

A feature is outside the product boundary if it tries to answer:

- Who is disordered?
- Who is guilty?
- Who is abusive as a final determination?
- What should HR do to this employee?
- What treatment does this person need?
- What is the hidden intent for certain?
- How can I use this recording against someone?

---

# Accepted Boundary Statement

Use this statement as the product boundary:

```text
The product supports private, evidence-linked reflection over conversation transcripts. It may use psychological, behavioral, therapeutic, cognitive, and relational lenses to generate hypotheses and reflection points, but it must preserve uncertainty, avoid diagnosis, avoid adjudication, protect sensitive data, and keep the user responsible for decisions.
```
