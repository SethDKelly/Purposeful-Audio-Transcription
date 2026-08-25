# 015 — Hypothesis-Aware Reflection Boundary Decision

## Status

Accepted as the current hypothesis-aware reflection boundary for concept design and refactor planning.

This document defines how the product may use psychological, behavioral, relational, and therapeutic hypotheses without diagnosing people, assigning disorders, adjudicating abuse, or proving intent.

---

# Decision Summary

The product may support **hypothesis-aware reflection**.

A hypothesis is a structured reflection context used to examine transcript evidence. It is not a diagnosis, label, verdict, prediction, or substitute for professional evaluation.

## Core Rule

```text
The system may evaluate whether conversation evidence is consistent with a reflective hypothesis.
The system must not conclude that a person has a disorder, trait, motive, or fixed identity.
```

---

# Why This Decision Exists

The product is intended to help users reflect on difficult conversations where psychological, behavioral, relational, or personality-related patterns may be relevant.

A user might reasonably ask whether a transcript contains evidence consistent with:

- schizoid-like distancing
- avoidant withdrawal
- borderline-like fear of abandonment
- narcissistic injury or defensiveness
- emotional dysregulation
- shame defense
- cognitive distortions
- hostile attribution
- projection hypothesis
- trauma-related reactivity
- anxious pursuit
- invalidation
- controlling behavior

The product may help examine these possibilities, but only as evidence-limited hypotheses.

---

# Hypothesis Definition

A psychological hypothesis is:

```text
an evidence-limited reflective explanation that may help a user examine patterns in a conversation
```

A psychological hypothesis is not:

```text
a diagnosis
a clinical finding
a personality label
a legal conclusion
a proof of motive
a finding of abuse
a reason to blame or excuse harm
a substitute for professional evaluation
```

---

# Hypothesis Sources

A hypothesis may come from:

## 1. User-Provided Context

Example:

```text
The user reports that one participant has been diagnosed with schizoid personality disorder.
```

The system may use this as context, but must not validate, invalidate, or independently diagnose it.

## 2. User-Provided Question

Example:

```text
Does this exchange show evidence consistent with avoidant withdrawal?
```

The system may answer with evidence support, contradictions, uncertainty, and alternatives.

## 3. Module-Suggested Reflection Hypothesis

A lens may propose a hypothesis only when it is clearly evidence-limited and phrased cautiously.

Example:

```text
One possible interpretation is a withdrawal-protection pattern, but the transcript alone is insufficient to determine why it occurs.
```

## 4. Longitudinal Pattern Hypothesis

A hypothesis may gain or lose support across multiple transcripts, but recurrence claims require multiple transcript/version citations.

---

# Required Hypothesis Output Structure

Every hypothesis-aware output should include:

```text
hypothesis name
hypothesis source
scope
supporting evidence
contradicting evidence or missing evidence
alternative explanations
confidence / support level
reflection questions
safety considerations if relevant
limitations
```

## Support Levels

Use these categories:

```text
observed behavior
consistent with hypothesis
partially consistent with hypothesis
contradicts hypothesis
insufficient evidence
alternative explanation likely
```

Do not use:

```text
confirmed
diagnosed
proved
clinically established
pathological
personality disordered
abusive as fact
manipulative as fact
```

---

# Inference Ladder

The product should enforce this ladder:

## Level 1 — Observation

What was directly said or done in the transcript.

Example:

```text
The speaker stops responding after being asked for emotional reassurance.
```

## Level 2 — Pattern

A repeated or interactional pattern supported by transcript evidence.

Example:

```text
The exchange shows a pattern of emotional request followed by withdrawal.
```

## Level 3 — Reflective Hypothesis

A possible explanation that may fit the evidence.

Example:

```text
This may be consistent with a withdrawal-protection response, though the transcript alone cannot establish motive or diagnosis.
```

## Level 4 — Diagnosis / Verdict

Not allowed.

Example of prohibited output:

```text
The speaker has schizoid personality disorder.
```

---

# Allowed Language

Use language such as:

- may be consistent with
- could reflect
- one possible interpretation is
- the transcript shows evidence of
- the evidence is insufficient to conclude
- an alternative explanation is
- this may be a useful reflection point
- this pattern appears in this transcript
- this pattern recurs across these transcripts

---

# Prohibited Language

Do not use language such as:

- has borderline personality disorder
- is narcissistic
- is schizoid
- is abusive, unless clearly quoting or carefully framing evidence-limited safety indicators
- is manipulating intentionally
- proves trauma
- confirms diagnosis
- clinically demonstrates
- pathological personality
- toxic person
- this relationship is doomed
- the speaker’s real motive is

---

# Examples

## Accepted Framing

```text
The transcript contains evidence that may be consistent with a distancing or withdrawal-protection pattern. The clearest evidence is Q014, where the speaker disengages after being asked for reassurance. However, this does not establish schizoid personality disorder or motive. Alternative explanations include fatigue, conflict avoidance, overwhelm, or context not present in the transcript.
```

## Rejected Framing

```text
The speaker is schizoid and cannot provide intimacy.
```

## Accepted Framing

```text
The exchange may be consistent with fear-of-abandonment activation because the speaker moves quickly from perceived distance to urgent reassurance seeking. This is a hypothesis for reflection, not evidence of borderline personality disorder.
```

## Rejected Framing

```text
The speaker has BPD and is splitting.
```

## Accepted Framing

```text
The speaker’s response may reflect narcissistic injury or shame-defense dynamics, but the evidence is limited to this exchange and does not establish narcissistic personality disorder.
```

## Rejected Framing

```text
The speaker is a narcissist.
```

---

# User-Provided Diagnoses

If the user provides a diagnosis as context, the system should say:

```text
Taking the user-provided context as background, the transcript contains / does not contain / is insufficient to evaluate evidence relevant to the requested reflection hypothesis.
```

The system should not say:

```text
The transcript confirms the diagnosis.
```

---

# Hypothesis and Safety Interaction

Safety-aware framing overrides hypothesis exploration.

When transcript evidence includes threats, coercion, stalking, severe control, intimidation, self-harm, fear of harm, or forced isolation, the system should not focus primarily on personality explanations.

Instead, it should:

- identify safety-relevant evidence
- avoid mutualizing serious concerns
- avoid reconciliation pressure
- keep language evidence-limited
- encourage appropriate professional or emergency support when warranted

---

# Evaluation Requirements

Hypothesis-aware outputs should be evaluated for:

- evidence linkage
- confidence calibration
- alternative explanations
- forbidden diagnostic claims
- intent-as-fact claims
- safety mutualization
- longitudinal overreach
- user-provided diagnosis handling

## Critical Failures

Fail evaluation if output:

- diagnoses a participant
- uses personality disorder labels as settled identity
- validates a user-provided diagnosis from transcript evidence
- states intent as fact without direct evidence
- treats a single exchange as a longitudinal pattern
- explains safety-relevant behavior mainly through personality hypotheses

---

# Decision

Hypothesis-aware reflection is in scope.

Diagnosis, labeling, adjudication, and intent-proving are out of scope.

The product should help users reflect on evidence, not convert transcript analysis into psychological verdicts.
