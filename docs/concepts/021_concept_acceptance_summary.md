# 021 — Concept Acceptance Summary

## Status

Accepted as the Phase 001 concept-closure summary.

This document consolidates the accepted concept decisions from Phase 001-A through Phase 001-D and declares the concept foundation ready to govern refactor planning.

---

# Decision Summary

Phase 001 converts the concept reset from exploration into accepted design authority.

The product is now conceptually defined as:

```text
A secure conversation analysis and reflection system that uses evidence-linked transcripts, psychological and behavioral reflection lenses, confidence calibration, and longitudinal case memory to help a user examine communication patterns without diagnosing people or making clinical/legal determinations.
```

This accepted concept identity supersedes implementation-first framing.

The current codebase remains valuable as a prototype and reference implementation, but it should no longer define the product philosophy.

---

# Accepted Product Identity

## Product Concept

```text
Secure Conversation Analysis and Reflection System
```

## Historical Repository Shell

```text
Purposeful Audio Transcription
```

This remains the repository name for now, but it is not the product concept.

## Internal Engine Identity

```text
Relationship Reasoning Engine (RRE)
```

RRE remains valid as the internal analysis-engine identity.

## Input Capability

```text
Audio transcription
```

Audio transcription is an input path, not the product center.

---

# Accepted Conceptual Boundary

The product supports private, evidence-linked reflection over conversation transcripts.

It may use psychological, behavioral, therapeutic, cognitive, relational, safety-aware, and longitudinal reasoning frameworks.

It must preserve uncertainty, avoid diagnosis, avoid adjudication, protect sensitive data, and keep the user responsible for decisions.

## In Scope

- conversation records
- recordings as ephemeral inputs
- transcript preparation
- transcript versioning
- evidence quotes
- reflection runs
- reflection lenses
- psychological hypotheses
- findings
- confidence calibration
- reflection points
- reasoning graph
- reports
- cases
- exports
- retention rules
- privacy boundary
- cost state
- future enterprise policy layer

## Out of Scope

- diagnosis
- disorder assignment
- clinical treatment
- treatment planning
- legal or clinical adjudication
- intent as fact without direct evidence
- workplace surveillance
- automated HR decisions
- covert recording encouragement
- therapy or mediation replacement

---

# Accepted Data Lifecycle Decisions

## Audio

Audio is ephemeral by default.

Default behavior:

```text
Delete recording after successful transcription.
```

Failed transcription audio may be retained only for retry/debug within a short TTL.

Recommended maximum:

```text
24 hours
```

## Transcript Drafts

Transcript drafts are temporary working artifacts.

Recommended default:

```text
Expire after 7 days unless saved or assigned to a case.
```

## Saved Transcripts

Saved transcripts are durable until user deletion.

## Cases

Assigning a transcript to a case implies durable longitudinal retention.

## Analysis Outputs

Analysis output inherits the retention posture of its evidence basis.

## Exports

Exports are explicit user actions and should be download-oriented by default unless the user deliberately stores them.

---

# Accepted Encryption Decisions

Infrastructure encryption is required immediately.

Application-level encryption is the target for retained sensitive artifacts, including:

- transcripts
- transcript versions
- evidence quotes
- analysis outputs
- findings
- hypotheses
- reflection points
- reports
- cases

The concept design accepts a phased implementation path, but the target posture is explicit.

---

# Accepted Analysis Boundary Decisions

## Hypothesis-Aware Reflection

Hypothesis-aware reflection is in scope.

The system may evaluate whether transcript evidence is:

```text
observed
consistent with a hypothesis
partially consistent with a hypothesis
in tension with a hypothesis
contradicted by a hypothesis
insufficient for a hypothesis
better explained by alternatives
```

## Diagnosis and Labeling

Diagnosis and labeling are out of scope.

The product must not conclude that a person has a disorder, fixed trait, hidden motive, or clinical condition.

## User-Provided Diagnoses

User-provided diagnoses or suspicions may be accepted as context only.

They must not be validated, invalidated, or independently diagnosed by the system.

## Therapeutic / Diagnostic-Framework-Informed Reasoning

Therapeutic, diagnostic-framework-informed, behavioral, cognitive, psychodynamic, and related frameworks may inform reasoning.

They must be used as source-framework references for evidence-limited reflection, not as claims of clinical authority.

Preferred product-facing phrase:

```text
therapeutic reflection lenses
```

Avoid as default product framing:

```text
clinical lenses
diagnostic lenses
treatment lenses
pathology lenses
```

The restriction is about authority and framing, not about whether those frameworks may inform cautious reasoning.

## Safety-Aware Framing

Safety-aware framing is a conceptual override.

When safety-relevant indicators are present, safety-aware framing overrides ordinary coaching, therapeutic reflection, hypothesis exploration, and mutual-improvement language.

---

# Accepted Personal Operating Model

The near-term product is personal and owner-operated.

The same person may act as:

```text
user
administrator
data owner
cost operator
product evaluator
```

Enterprise role complexity is deferred.

Single-user does not mean insecure; authentication, ownership, encryption, retention control, redacted logs, and deletion remain required design concerns.

---

# Accepted Cost State Model

Cost State is a first-class product concept for personal mode.

The accepted states are:

```text
Asleep
Waking
Active
IdlePending
ShuttingDown
FailedWake
Maintenance
```

Personal mode optimizes for low cost through explicit sleep/wake behavior.

Enterprise mode may later change availability policy without redefining the core product concepts.

---

# Accepted Enterprise Posture

Enterprise is a possible future policy and deployment layer.

It is not the current design center.

Enterprise should add policy, identity, access, audit, retention, compliance, and availability layers over stable core concepts.

It should not redefine the core product.

---

# Deferred Questions

The following are intentionally deferred until implementation planning or later product exploration:

- final public brand name
- repository rename
- exact field-level encryption implementation
- exact retention scheduler design
- long-term audio retention support
- enterprise organizations/workspaces/RBAC
- SSO/OIDC/SAML/Okta/Google auth
- compliance framework selection
- production uptime posture
- clinician/professional workflows
- evaluation fixture expansion
- exact UI copy for every safety/diagnostic caution
- final data export format

Deferred does not mean ignored. It means these questions should not block concept acceptance.

---

# Concept Authority Declaration

The accepted concept authority order is:

```text
Concept design
→ Product philosophy
→ Domain model
→ Security/privacy model
→ Analysis philosophy
→ Implementation architecture
→ Code
```

Future implementation work should explain which accepted concept it serves.

If implementation conflicts with concept design, the conflict should be made explicit rather than silently resolved in code.

---

# Phase 001 Acceptance

Phase 001 is accepted when this document and the refactor-readiness decision are present.

After acceptance, the next major work should be implementation refactor planning, not feature expansion.
