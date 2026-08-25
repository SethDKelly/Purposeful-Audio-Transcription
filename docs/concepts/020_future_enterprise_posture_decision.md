# 020 — Future Enterprise Posture Decision

## Status

Accepted as the current future-enterprise posture decision for concept design and refactor planning.

This document defines how enterprise potential should be preserved without overcomplicating the personal-mode product.

---

# Decision Summary

Enterprise use is a possible future deployment and policy layer.

It is not the current design center.

The near-term product should remain a secure personal owner-operated conversation analysis and reflection system.

## Core Rule

```text
Enterprise should extend stable concepts through policy, identity, access, audit, and availability layers.
It should not redefine the core concepts.
```

---

# Current Design Center

Near-term design center:

```text
single owner/admin/user
personal use
sensitive private transcripts
hypothesis-aware reflection
non-diagnostic discipline
case-based longitudinal memory
aggressive sleep/wake cost control
explicit retention and deletion
```

---

# Future Enterprise Additions

Enterprise may later add:

- organizations
- workspaces
- role-based access
- SSO / OIDC / SAML / Okta / Google
- administrator roles
- reviewer roles
- audit logs
- retention policies
- sharing grants
- billing
- always-on or autoscaled availability
- compliance documentation
- incident response processes
- security review artifacts

These are future additions, not current requirements.

---

# Stable Concepts That Should Survive Enterprise Transition

The following should remain stable:

- Recording
- Transcript
- Transcript Version
- Evidence Quote
- Reflection Run
- Lens
- Psychological Hypothesis
- Finding
- Confidence
- Reflection Point
- Reasoning Graph
- Case
- Retention Rule
- Privacy Boundary
- Cost State / Availability Policy
- Export

Enterprise should add ownership and policy structure around these concepts.

---

# Policy Expansion Model

| Personal Mode | Enterprise / Future Mode |
|---|---|
| Owner | Organization / workspace owner |
| Personal transcript | Workspace transcript |
| Personal case | Workspace case |
| Owner-only access | Role-based access |
| Personal retention choice | Policy-governed retention |
| Personal cost state | Availability policy |
| Personal export | Governed export |
| Local/personal audit | Compliance audit |
| Email/login access | SSO / enterprise identity |

---

# What Enterprise Must Not Introduce Prematurely

Do not introduce near-term complexity for:

- organization administration
- team management
- HR workflows
- personnel decisions
- clinician-client hierarchy
- billing administration
- compliance workflows
- multi-user collaboration
- external sharing
- always-on high availability

Unless a future phase explicitly accepts those concepts, they remain deferred.

---

# Enterprise Risk Boundaries

## Surveillance Risk

Enterprise use must not become covert meeting surveillance or employee scoring.

## HR Misuse Risk

The product must not automate personnel decisions, disciplinary action, promotion decisions, or misconduct determinations.

## Clinical Overreach Risk

Even in future professional versions, the product must preserve evidence traceability, confidence calibration, and non-diagnostic discipline unless a legally and professionally appropriate mode is explicitly designed.

## Complexity Risk

Enterprise concepts should not make personal mode harder to understand or operate.

---

# Decision

Treat enterprise as a future policy/deployment expansion over stable personal-mode concepts.

Do not allow enterprise assumptions to drive the immediate concept model, UI, retention rules, or operating model.
