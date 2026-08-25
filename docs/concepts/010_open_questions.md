# 010 — Open Questions

## Purpose

Capture questions that should be answered before implementation refactoring begins.

Do not treat these as blockers to all progress. They are design decisions that should be resolved or explicitly deferred.

---

# Product Identity

## Q1 — What should the product be called?

Current name:

```text
Purposeful Audio Transcription
```

Potential issue:

The name frames transcription as the product, but transcription is only an input path.

## Q2 — Is “Relationship Reasoning Engine” too narrow or too technical?

The application may analyze business meetings, therapy sessions, and personal conversations. “Relationship” may fit broadly, but “Conversation Reflection” may be more general.

---

# Audio and Retention

## Q3 — Should recordings be deleted immediately after transcription?

Options:

1. delete immediately after success
2. retain for short retry TTL
3. retain only when explicitly saved
4. allow configurable retention

Recommended starting point:

```text
short TTL, explicit save required for longer retention
```

## Q4 — Should transcripts be retained by default?

Options:

1. retained by default
2. retained only if explicitly saved
3. retained only if assigned to a case
4. retained for short TTL unless promoted

Recommended starting point:

```text
short default retention unless saved/promoted
```

## Q5 — Should cases imply long-term retention?

Recommended:

```text
yes, assigning to a case means the user is choosing longitudinal retention
```

---

# Encryption

## Q6 — Is AWS/RDS encryption enough for the personal phase?

Possible answer:

```text
acceptable for early development, but application-level encryption should be designed
```

## Q7 — Should transcript text and analysis outputs use field-level encryption?

Likely yes for a mature version.

---

# Analysis Scope

## Q8 — Should the app frame psychoanalytic/CBT/DBT outputs as “therapeutic reflections” or “clinical lenses”?

Recommended:

```text
therapeutic reflection lenses
```

Avoid implying clinical treatment.

## Q9 — Should user-provided diagnoses be accepted as context?

Likely yes, but only as user-provided context.

Example:

```text
The user reports that one participant has SPD. The system may examine transcript evidence in light of that context but must not validate or diagnose it.
```

## Q10 — Should the app ever suggest possible diagnoses?

Recommended:

```text
no diagnosis suggestions; only evidence-limited hypotheses and reflection points
```

---

# Safety

## Q11 — Should safety-aware mode suppress some psychological hypothesis modules?

Likely yes when high-risk indicators are present.

## Q12 — Should the app encourage professional support?

Yes, when safety or clinical uncertainty is meaningful, but it should not present itself as therapy.

---

# User and Access Model

## Q13 — Is the initial app strictly single-user?

Current assumption:

```text
yes
```

## Q14 — Should multi-user features be modeled now?

Model as future concepts, but do not implement unless necessary.

---

# Cost State

## Q15 — Should sleep/wake be visible in the product UI?

Recommended:

```text
yes
```

The user should understand that wake latency is intentional cost control.

## Q16 — Should the cost-control mechanism survive enterprise transition?

Yes, as a deployment policy option, even if enterprise defaults change.

---

# Enterprise Future

## Q17 — Should enterprise be a separate product or a deployment mode?

Recommended:

```text
deployment/policy mode over the same core concepts
```

## Q18 — What enterprise features should remain deferred?

- SSO
- orgs/workspaces
- sharing
- team audit
- billing
- compliance automation
- always-on HA
- enterprise support

---

# Refactor Sequencing

## Q19 — Should current feature development pause during concept redesign?

Recommended:

```text
pause non-critical feature expansion; continue only bug/security fixes
```

## Q20 — What happens after concept docs are accepted?

Create an implementation refactor roadmap that maps current code to the accepted concepts.
