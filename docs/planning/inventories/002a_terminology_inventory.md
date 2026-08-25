# 002-A Terminology Inventory

## Status

Accepted as the Phase 002-A terminology inventory.

---

# Accepted product terms

| Term | Meaning |
|---|---|
| Secure Conversation Analysis and Reflection System | Current concept-level product identity |
| Relationship Reasoning Engine / RRE | Internal analysis-engine identity |
| Purposeful Audio Transcription | Historical repository name / legacy shell |
| Audio transcription | Input capability, not product identity |
| Conversation record | Source conversation represented by transcript and optional recording |
| Recording | Ephemeral audio input used to produce a transcript |
| Transcript | Textual conversation record used for reflection/analysis |
| Transcript Version | Stable evidence basis for analysis and reports |
| Evidence Quote | Concise transcript span supporting a finding |
| Reflection Run | Analysis execution over a transcript version |
| Reflection Lens | Bounded reasoning perspective applied to evidence |
| Therapeutic Reflection Lens | Product-facing term for CBT/DBT/psychodynamic/etc. reflection frameworks |
| Diagnostic-framework-informed concept | Internal/source-framework reasoning reference, not clinical authority |
| Psychological Hypothesis | Evidence-limited reflective explanation, not a diagnosis |
| Finding | Evidence-backed insight with confidence and limitations |
| Confidence | Calibration of support level and inference risk |
| Reflection Point | Non-prescriptive self-review prompt |
| Reasoning Graph | Structured relationship model among evidence, findings, hypotheses, and concepts |
| Case | Opt-in longitudinal grouping of related transcripts |
| Retention Rule | Policy controlling what is kept, for how long, and why |
| Privacy Boundary | Access, ownership, encryption, logging, and export boundary |
| Cost State | Personal-mode availability/cost posture |
| Export | Deliberate portable user artifact |
| Personal Mode | Single owner/operator deployment mode |
| Future Enterprise Policy Layer | Future expansion for orgs, RBAC, SSO, audit, compliance, and uptime |

---

# Preferred phrasing

Use:

- evidence-linked reflection
- evidence-limited hypothesis
- therapeutic reflection lens
- diagnostic-framework-informed reasoning reference
- consistent with / partially consistent with / contradicted by / insufficient evidence
- personal owner/operator
- future enterprise policy layer
- transcript-centered reflection record

---

# Avoid as product-facing defaults

Avoid using these as product-facing defaults:

- clinical lens
- diagnostic lens
- treatment lens
- pathology lens
- disorder detection
- personality disorder analysis
- mental health assessment
- AI therapist
- diagnosis engine
- workplace surveillance
- HR adjudication

These terms may appear in historical docs or internal caution notes, but they should not frame the product.

---

# Legacy terms to map

| Legacy / implementation term | Map to |
|---|---|
| Analysis module | Reflection Lens, unless referring to implementation module |
| Workflow | Reflection Run or workflow engine, depending context |
| Report | Reflection Report / user-facing analysis view |
| Audio app / transcription app | Input capability or historical repository shell |
| User/admin split | Personal owner/operator for near-term mode |
| Clinical analysis | Therapeutic reflection or diagnostic-framework-informed reasoning reference |
| Safety mode | Safety-aware framing / safety override behavior |
| Graph merge / ontology | Reasoning Graph implementation reference |

---

# Forbidden output claims

The product must not claim:

- this person has BPD/NPD/SPD/etc.
- this confirms a diagnosis
- this proves abuse or legal misconduct
- this proves hidden intent
- this person needs treatment
- HR should take action against this employee

Allowed alternative:

```text
The transcript contains evidence that may be consistent with this reflective hypothesis, but the evidence is limited and does not establish diagnosis, intent, or clinical/legal determination.
```

---

# 002-B handoff

Use this terminology inventory to map concepts to current implementation artifacts without preserving legacy names as product authority.
