# 018 — Personal Operating Model Decision

## Status

Accepted as the current personal operating model decision for concept design and refactor planning.

This document defines who the near-term application is for, which user roles exist now, and which roles should remain deferred.

---

# Decision Summary

The near-term product should be designed as a personal, owner-operated application.

The same person may act as:

```text
user
administrator
data owner
cost operator
product evaluator
```

The application should not introduce enterprise role complexity into the core product during the concept-reset phase.

---

# Current User Model

## Primary User

The primary user is the personal owner/operator.

This person:

- logs into the system
- wakes the system when needed
- uploads or pastes transcripts
- may upload recordings for transcription
- reviews transcript preparation
- chooses whether to save or delete transcripts
- assigns transcripts to cases when longitudinal retention is desired
- runs reflection analysis
- reviews reports and evidence
- exports reports intentionally
- pays or controls cloud cost
- administers the deployment

## Administrator

In the near-term model, administrator is not a separate actor.

Administration is a role the owner performs.

The administrator can:

- configure environment settings
- manage deployment state
- control wake/sleep posture
- review logs and operational health
- manage access to the personal app
- delete or purge data

## Data Owner

The owner is responsible for retention decisions.

The product should make those decisions visible rather than silent.

## Cost Operator

The owner is responsible for cost posture.

Cost visibility and sleep/wake behavior are part of the current personal-mode product experience.

---

# Deferred User Models

The following are future concepts, not current operating assumptions:

- organization admin
- workspace owner
- clinician
- client
- supervisor
- reviewer
- auditor
- enterprise user
- HR user
- compliance officer
- billing admin
- multi-user sharing recipient

These may be modeled later as policy and access layers.

They should not drive the near-term concept design.

---

# Role Boundary

## Current Role Boundary

```text
single owner/admin/user
```

## Future Role Boundary

```text
user
organization
workspace
role
sharing grant
audit policy
retention policy
```

Future roles should be additive.

They should not require redefining transcript, evidence, reflection run, hypothesis, case, or cost state.

---

# Product Implications

## UI

The UI may assume a personal operator by default.

It should not require workspace selection, organization switching, team invites, role management, or enterprise admin screens.

## Security

Authentication is still required.

Single-user does not mean insecure.

The product should still enforce:

- login
- session control
- owner scoping
- deletion controls
- redacted logs
- explicit exports

## Data

Every retained sensitive artifact should be understood as owned by the personal operator.

## Cost

The owner should be able to understand when the system is asleep, waking, active, idle pending, or shutting down.

---

# Invariants

- Personal mode is the current design center.
- The owner may also be the administrator.
- Single-user does not remove the need for security.
- Enterprise role complexity is deferred.
- Future multi-user models must be additive, not concept-breaking.
- Data ownership and cost ownership should be visible to the user.

---

# Decision

Design the near-term application as a secure personal owner-operated system.

The product may later evolve into a multi-user or enterprise system, but near-term concept and refactor planning should not optimize for enterprise administration, collaboration, or RBAC beyond preserving a future path.
