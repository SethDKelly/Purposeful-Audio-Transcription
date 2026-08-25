# 002-G UI/UX Language Matrix

## Status

Accepted as the Phase 002-G UI/UX language matrix.

---

# Purpose

Provide user-facing terminology guidance so future UI, reports, help text, and exports preserve the accepted product concept boundaries.

This matrix is governed by:

- `docs/concepts/011_product_identity_decision.md`
- `docs/concepts/012_concept_boundary_decision.md`
- `docs/planning/architecture/002g_ui_ux_concept_alignment_plan.md`

---

# Product Framing

| Use | Avoid | Rationale |
|---|---|---|
| Secure conversation analysis and reflection system | Audio transcription app | Transcription is input, not product identity |
| Evidence-linked reflection | AI advice | Emphasizes evidence and user responsibility |
| Private conversation reflection | Surveillance / monitoring | Avoids workplace/observer framing |
| Reflection report | Clinical report / diagnosis report | Avoids clinical/legal authority |
| Relationship Reasoning Engine / RRE as internal engine | RRE as only product identity | Keeps engine distinct from product shell |

---

# Analysis Terms

| Use | Avoid | Rationale |
|---|---|---|
| Reflection Lens | Analysis module, clinical lens | Lens is product-facing; module is implementation |
| Therapeutic Reflection Lens | Treatment lens, pathology lens | Uses therapeutic concepts without authority claims |
| Diagnostic-framework-informed reasoning reference | Diagnostic assessment | Framework can inform reasoning; product cannot diagnose |
| Finding | Verdict / judgment | Finding is evidence-backed and limited |
| Confidence | Certainty | Confidence is calibrated evidence support, not proof |
| Reflection Point | Recommendation, intervention, prescription | Keeps guidance non-prescriptive |
| Alternative explanation | Excuse / dismissal | Keeps uncertainty visible |
| Limitation | Fine print | Limits are core to trustworthy reflection |

---

# Hypothesis Terms

| Use | Avoid | Rationale |
|---|---|---|
| Psychological Hypothesis | Diagnosis | Hypothesis is reflective and evidence-limited |
| Consistent with hypothesis | Confirms | Support is not proof |
| Partially consistent with hypothesis | Shows they are... | Avoids identity labeling |
| Contradicts hypothesis | Rules out | Product does not clinically rule in/out |
| Insufficient evidence | Unknown but likely | Preserves uncertainty |
| Alternative explanation likely | They are lying / manipulating | Avoids hidden intent claims |
| User-provided context | Confirmed diagnosis | User context must not become system validation |

---

# Evidence Terms

| Use | Avoid | Rationale |
|---|---|---|
| Evidence Quote | Proof | Evidence supports; it does not always prove |
| Transcript Version | Latest text only | Analysis binds to a stable evidence basis |
| Evidence scope | Data used behind the scenes | Scope must be visible |
| Source transcript | Background data | Keeps lineage inspectable |
| Evidence basis | Model context | User should know what supports the report |
| Expand context | Reveal model thoughts | Shows surrounding transcript, not hidden reasoning |

---

# Corpus / Case Terms

| Use | Avoid | Rationale |
|---|---|---|
| Case | Folder, project only | Case implies longitudinal evidence and retention |
| Case Evidence Corpus | All your data | Corpus must be explicit and scoped |
| Selected transcript set | Account history | Avoids hidden account-wide inference |
| Recurs across selected transcripts | Always happens | Avoids overgeneralization |
| Temporal change | Personality change | Keeps change grounded in evidence |
| Contradictory evidence | Inconsistent user | Contradiction is analytical, not moral |
| Stale evidence | Bad data | Staleness is lifecycle/version issue |

---

# Safety Terms

| Use | Avoid | Rationale |
|---|---|---|
| Safety posture | Abuse verdict | Safety posture is evidence-linked caution, not legal conclusion |
| Elevated caution | Mild abuse | Avoids adjudication |
| High-risk safety indicators | Dangerous person | Avoids labeling person as identity |
| Immediate or crisis indicators | Crisis handled by app | Product is not crisis support |
| Support category | Specific legal/clinical directive | Keeps support guidance careful |
| Ordinary reflection may be limited | Both sides need to communicate | Avoids unsafe mutualization |

---

# Retention / Privacy Terms

| Use | Avoid | Rationale |
|---|---|---|
| Audio will be deleted after transcription by default | Audio is saved | Audio is ephemeral by default |
| Draft expires unless saved | Draft is stored forever | Prevents silent durable memory |
| Save transcript | Upload complete | Upload/intake is not durable retention |
| Assign to case | Add to folder | Case assignment implies durable corpus use |
| Delete transcript and dependent analysis | Delete file | Deletion cascades to evidence/reports/graph objects |
| Export for download | Backup retained by app | Server retention must be explicit |
| Private and owner-scoped | Secure because single-user | Single-user still needs security |

---

# Cost-State Terms

| Use | Avoid | Rationale |
|---|---|---|
| App is asleep to reduce cost | App is down | Sleep is intentional |
| Waking required services | Loading forever | Wake has product meaning |
| Active jobs are keeping the app awake | App will not shut down | Explain why sleep is delayed |
| Idle shutdown | Crash / timeout | Idle shutdown is intentional cost control |
| Failed wake | Broken app | Failure state should be actionable |
| Keep awake | Disable sleep forever | Keep-awake should sound temporary |

---

# Report Phrases

## Preferred report phrasing

Use phrasing such as:

```text
This report is based on the selected transcript version.
```

```text
This finding is supported by the following evidence quotes.
```

```text
This hypothesis is partially consistent with the selected evidence, but alternatives remain plausible.
```

```text
This pattern recurs across the selected case corpus.
```

```text
This report cannot establish diagnosis, legal fault, hidden intent, or clinical conclusions.
```

## Avoid report phrasing

Avoid phrasing such as:

```text
The model determined the real cause.
```

```text
This proves the diagnosis.
```

```text
The other person is narcissistic.
```

```text
You should confront them.
```

```text
Both people are equally responsible.
```

```text
This always happens.
```

---

# Button / Action Labels

| Preferred Label | Avoid | Notes |
|---|---|---|
| Save transcript | Keep forever | Saving implies durable retention but should not sound irreversible |
| Analyze selected version | Analyze everything | Scope must be clear |
| Use case evidence corpus | Use all history | Corpus must be explicit |
| Add to case | Add to folder | Consider helper text about retention/corpus implications |
| Export report | Download data | Export should identify report/scope |
| Delete transcript | Remove from view | Deletion has cascade meaning |
| Remove from case | Delete from case | Distinguish unlink from source deletion |
| Keep awake | Disable shutdown | Temporary availability control |
| Put app to sleep | Shut down app | Sleep is intentional, cost-saving |

---

# Decision

Future UI and report work should treat language as part of the product boundary.

Terminology drift can create safety, privacy, and authority drift, so later implementation should include a UI/report copy audit against this matrix.
