# 016 — Therapeutic Lens Language Decision

## Status

Accepted as the current language decision for therapeutic, psychological, behavioral, CBT, DBT, psychodynamic, and related analysis lenses.

This document defines how the product should name and frame therapeutic lenses without implying clinical treatment, diagnosis, or professional authority.

---

# Decision Summary

Use the phrase:

```text
therapeutic reflection lenses
```

Do not use the default phrase:

```text
clinical lenses
```

The product may use therapeutic concepts as reflection frameworks, but it is not a therapy provider, clinical tool, diagnostic instrument, or treatment-planning system.

---

# Rationale

The application may analyze transcripts using concepts inspired by CBT, DBT, behavioral analysis, psychodynamic thinking, attachment-informed communication, trauma-informed communication, mediation, NVC, and systems thinking.

These frameworks are valuable for reflection, but the current product is for personal evidence-backed conversation analysis.

The language must preserve this distinction.

---

# Preferred Lens Family Name

Use:

```text
therapeutic reflection lenses
```

This phrase communicates that the app borrows reflective concepts from therapeutic traditions while staying outside clinical treatment.

## Allowed Alternatives

- psychological reflection lenses
- behavioral reflection lenses
- cognitive reflection lenses
- relational reflection lenses
- safety-aware reflection lenses
- hypothesis-aware reflection lenses

## Avoid as Default

- clinical lenses
- diagnostic lenses
- treatment lenses
- pathology lenses
- disorder detection
- personality disorder analysis
- mental health assessment

---

# Lens-Specific Language

## CBT-Style Reflection

Allowed framing:

```text
CBT-style thought pattern reflection
```

The product may examine:

- automatic thoughts
- assumptions
- interpretations
- cognitive distortions
- evidence for and against interpretations
- alternative interpretations
- behavior-impact links

Avoid:

- CBT treatment plan
- cognitive restructuring prescription
- clinical CBT intervention

## DBT-Style Reflection

Allowed framing:

```text
DBT-style emotion regulation and interpersonal effectiveness reflection
```

The product may examine:

- escalation signals
- validation opportunities
- emotion regulation cues
- distress tolerance reflection points
- interpersonal effectiveness opportunities
- repair and boundary language

Avoid:

- DBT treatment plan
- skills coaching as therapy
- clinical DBT intervention

## Behavioral Analysis Reflection

Allowed framing:

```text
behavioral pattern reflection
```

The product may examine:

- antecedents
- observable behaviors
- consequences
- reinforcement-like loops
- avoidance patterns
- approach/withdrawal patterns

Avoid:

- behavior diagnosis
- clinical functional analysis unless future professional mode explicitly supports it

## Psychodynamic / Psychoanalytic Reflection

Allowed framing:

```text
psychodynamic hypothesis-aware reflection
```

The product may examine possible evidence for:

- defenses
- shame responses
- distancing
- projection-like interpretations
- emotional protection strategies
- identity threat
- attachment-related meaning

Avoid:

- psychoanalytic diagnosis
- claims about unconscious motive as fact
- fixed personality conclusions

## Attachment-Informed Reflection

Allowed framing:

```text
attachment-informed interaction reflection
```

The product may examine:

- bids for closeness
- pursuit/withdrawal cycles
- reassurance seeking
- distancing
- fear of abandonment hypotheses
- fear of engulfment hypotheses

Avoid:

- assigning attachment style as identity
- saying a speaker is avoidant/anxious/disorganized as a fixed label

## Trauma-Informed Communication Reflection

Allowed framing:

```text
trauma-informed communication reflection
```

The product may examine:

- safety/threat language
- dysregulation cues
- shutdown/escalation cues
- shame activation hypotheses
- control and predictability needs

Avoid:

- concluding trauma history
- treating trauma as confirmed
- providing trauma therapy

---

# Standard Lens Disclaimer

Every therapeutic reflection lens should conceptually follow this disclaimer:

```text
This lens uses therapeutic concepts for evidence-based reflection. It does not diagnose, treat, or determine clinical conditions. Findings should be interpreted as reflection prompts, not professional conclusions.
```

This disclaimer does not need to appear verbatim in every UI surface, but the design should preserve the meaning.

---

# Reflection Output Style

Therapeutic reflection outputs should use:

- evidence-linked observations
- cautious hypotheses
- confidence levels
- alternative explanations
- reflection questions
- self-awareness prompts
- safety-aware caveats when relevant

They should avoid:

- instructions framed as treatment
- clinical conclusions
- pathology-centered labels
- personality judgments
- prescriptions
- certainty about motive
- certainty about diagnosis

---

# User-Facing Examples

## Preferred

```text
CBT-style reflection: This statement may involve mind-reading because it assumes the other person’s intent without direct evidence. A useful reflection question is: what evidence supports that interpretation, and what other explanation might fit?
```

## Avoid

```text
CBT diagnosis: The speaker has a distorted thinking pattern that needs restructuring.
```

## Preferred

```text
DBT-style reflection: The exchange shows a possible validation gap. The speaker answers the facts of the complaint before acknowledging the emotion.
```

## Avoid

```text
The speaker needs DBT skills training.
```

## Preferred

```text
Psychodynamic reflection: One possible hypothesis is that the speaker’s withdrawal protects against feeling criticized. The transcript supports this only weakly; fatigue or overwhelm may also explain the response.
```

## Avoid

```text
The speaker withdraws because of unconscious schizoid defenses.
```

---

# Therapy Session Context

The product may analyze personal therapy session transcripts only when legally and ethically appropriate.

In that context, the product should still frame output as reflection, not supervision, diagnosis, or clinical documentation.

Future professional versions may add clinician-specific workflows, but those are out of scope for the current personal-mode concept design.

---

# Decision

Therapeutic concepts are allowed as reflection lenses.

The product should frame them as evidence-based reflection aids, not clinical authority.

The preferred phrase is:

```text
therapeutic reflection lenses
```
