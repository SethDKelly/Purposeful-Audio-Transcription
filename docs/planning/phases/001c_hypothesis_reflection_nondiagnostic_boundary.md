# 001-C — Hypothesis-Aware Reflection and Non-Diagnostic Boundary

## Status

Complete.

This phase closes the concept-level decisions for psychological hypotheses, therapeutic reflection lens language, and safety-aware override behavior.

---

# Purpose

The product is intended to analyze sensitive conversations using evidence-based psychological, behavioral, therapeutic, cognitive, and relational reflection lenses.

This creates a central boundary problem:

```text
The product should support useful psychological reflection.
The product must not diagnose, label, adjudicate, or claim clinical certainty.
```

Phase 001-C resolves that boundary.

---

# Decision Documents

| Decision | Document |
|---|---|
| Hypothesis-aware reflection boundary | `../../concepts/015_hypothesis_reflection_boundary.md` |
| Therapeutic lens language | `../../concepts/016_therapeutic_lens_language_decision.md` |
| Safety boundary and override behavior | `../../concepts/017_safety_boundary_decision.md` |

---

# Accepted Decisions

## 1. Hypothesis-Aware Reflection Is In Scope

The product may evaluate whether transcript evidence is consistent with a psychological, behavioral, relational, or therapeutic reflection hypothesis.

Allowed support categories:

```text
observed behavior
consistent with hypothesis
partially consistent with hypothesis
contradicts hypothesis
insufficient evidence
alternative explanation likely
```

The product must not frame hypotheses as diagnoses, labels, verdicts, predictions, or proof of motive.

## 2. User-Provided Diagnoses Are Context, Not Proof

If the user provides diagnostic context, the product may use it as background for reflection.

It must not validate, invalidate, or independently diagnose from transcript evidence.

## 3. Therapeutic Concepts Are Reflection Lenses

Use the phrase:

```text
therapeutic reflection lenses
```

Avoid default framing such as:

```text
clinical lenses
diagnostic lenses
treatment lenses
pathology lenses
```

## 4. CBT/DBT/Psychodynamic Concepts Are Allowed With Boundaries

The product may use CBT-style, DBT-style, behavioral, psychodynamic, attachment-informed, trauma-informed, and related concepts as reflection frameworks.

It must not provide treatment plans, clinical conclusions, diagnosis, or professional authority.

## 5. Safety-Aware Framing Overrides Ordinary Reflection

When transcripts include safety-relevant indicators, safety-aware framing takes priority over ordinary coaching, therapeutic reflection, hypothesis exploration, and mutual improvement language.

---

# Out of Scope

This phase does not implement:

- model prompts
- validators
- safety classifiers
- UI banners
- new database objects
- new evaluation fixtures
- crisis support workflows

Those belong in later implementation planning after concept closure.

---

# Exit Criteria

Phase 001-C is complete when:

- hypothesis-aware reflection is formally allowed but bounded
- user-provided diagnoses are handled only as context
- allowed and prohibited hypothesis language is documented
- therapeutic lens language is reflection-oriented
- safety-aware framing has concept-level override authority
- ordinary mutual-improvement framing is prohibited in serious safety contexts

---

# Next Phase

Proceed to:

```text
001-D — Personal Operating Model, User Role, and Cost State
```
