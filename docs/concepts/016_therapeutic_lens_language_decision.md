# 016 — Therapeutic Lens Language Decision

## Status

Accepted as the current language decision for therapeutic, psychological, behavioral, CBT, DBT, psychodynamic, diagnostic-framework-informed, and related analysis lenses.

This document defines how the product should name and frame these lenses without implying clinical treatment, diagnosis, or professional authority.

---

# Decision Summary

Use the phrase:

```text
therapeutic reflection lenses
```

Do not use the default product-facing phrase:

```text
clinical lenses
```

The product may use therapeutic, diagnostic-framework-informed, behavioral, cognitive, psychodynamic, and related concepts as reasoning references, but it is not a therapy provider, clinician, diagnostic instrument, treatment-planning system, or professional authority.

---

# Clarification — Authority vs Reasoning Utility

Avoiding phrases such as `clinical lenses`, `diagnostic lenses`, `treatment lenses`, and `pathology lenses` does **not** mean the underlying traditions are useless or prohibited.

The reason to avoid those terms is authority management.

The application lacks clinical authority. It should not present itself as diagnosing, treating, or pathologizing anyone.

However, these frameworks may still help the reasoning engine by supplying:

- concepts to check against transcript evidence
- possible explanatory hypotheses
- patterns to compare over time
- alternative explanations
- reflection prompts
- safety cautions
- confidence limits

The distinction is:

```text
Allowed: use source frameworks to reason cautiously from evidence.
Forbidden: present the output as clinical authority, diagnosis, pathology detection, treatment, or settled truth.
```

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
- diagnostic-framework-informed reflection references
- clinical-framework-informed reasoning references, internal/developer context only

## Avoid as Product-Facing Defaults

- clinical lenses
- diagnostic lenses
- treatment lenses
- pathology lenses
- disorder detection
- personality disorder analysis
- mental health assessment

These terms may appear in internal design discussions only when explicitly marked as source-framework or rationale references rather than product authority.

---

# Lens-Specific Language

## CBT-Style Reflection

Allowed framing:

```text
CBT-style thought pattern reflection
```

The product may examine automatic thoughts, assumptions, interpretations, cognitive distortions, evidence for and against interpretations, alternative interpretations, and behavior-impact links.

Avoid treatment plans, cognitive restructuring prescriptions, or clinical CBT interventions.

## DBT-Style Reflection

Allowed framing:

```text
DBT-style emotion regulation and interpersonal effectiveness reflection
```

The product may examine escalation signals, validation opportunities, emotion regulation cues, distress tolerance reflection points, interpersonal effectiveness opportunities, repair language, and boundary language.

Avoid DBT treatment plans, skills coaching as therapy, or clinical DBT interventions.

## Behavioral Analysis Reflection

Allowed framing:

```text
behavioral pattern reflection
```

The product may examine antecedents, observable behaviors, consequences, reinforcement-like loops, avoidance patterns, and approach/withdrawal patterns.

Avoid behavior diagnosis or clinical functional analysis unless a future professional mode explicitly supports it.

## Psychodynamic / Psychoanalytic Reflection

Allowed framing:

```text
psychodynamic hypothesis-aware reflection
```

The product may examine possible evidence for defenses, shame responses, distancing, projection-like interpretations, emotional protection strategies, identity threat, and attachment-related meaning.

Avoid psychoanalytic diagnosis, claims about unconscious motive as fact, or fixed personality conclusions.

## Diagnostic-Framework-Informed Reflection

Allowed framing:

```text
diagnostic-framework-informed reflection reference
```

This may be used internally or in advanced user-facing contexts when a user has provided diagnostic context or a reflective hypothesis.

The system may ask whether transcript evidence is consistent with, inconsistent with, or insufficient for that hypothesis.

Avoid saying the system has diagnosed, confirmed, ruled out, detected, or clinically assessed a condition.

## Attachment-Informed Reflection

Allowed framing:

```text
attachment-informed interaction reflection
```

The product may examine bids for closeness, pursuit/withdrawal cycles, reassurance seeking, distancing, fear-of-abandonment hypotheses, and fear-of-engulfment hypotheses.

Avoid assigning attachment style as identity.

## Trauma-Informed Communication Reflection

Allowed framing:

```text
trauma-informed communication reflection
```

The product may examine safety/threat language, dysregulation cues, shutdown/escalation cues, shame activation hypotheses, and control/predictability needs.

Avoid concluding trauma history, treating trauma as confirmed, or providing trauma therapy.

---

# Standard Lens Disclaimer

Every therapeutic reflection lens should conceptually follow this disclaimer:

```text
This lens uses therapeutic or psychological concepts for evidence-based reflection. It does not diagnose, treat, or determine clinical conditions. Findings should be interpreted as reflection prompts and evidence-limited hypotheses, not professional conclusions.
```

This disclaimer does not need to appear verbatim in every UI surface, but the design should preserve the meaning.

---

# Decision

Therapeutic, psychological, behavioral, diagnostic-framework-informed, and related concepts are allowed as reasoning references and reflection lenses.

The product should frame them as evidence-based reflection aids, not clinical authority.

The preferred product-facing phrase is:

```text
therapeutic reflection lenses
```
