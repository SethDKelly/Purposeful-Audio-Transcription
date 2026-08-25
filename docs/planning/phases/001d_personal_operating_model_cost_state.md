# 001-D — Personal Operating Model, User Role, and Cost State

## Status

Complete.

This phase closes the concept-level decisions for personal-mode operation, current user roles, cost state, and future enterprise posture.

---

# Purpose

Phase 001-D defines how the product should operate in the near term:

```text
personal use
single owner/admin/user
sensitive private data
aggressive cost control
future enterprise optionality
```

The goal is to preserve the current low-cost personal operating model without letting enterprise assumptions overcomplicate the concept design.

---

# Decision Documents

| Decision | Document |
|---|---|
| Personal operating model | `../../concepts/018_personal_operating_model_decision.md` |
| Cost state | `../../concepts/019_cost_state_decision.md` |
| Future enterprise posture | `../../concepts/020_future_enterprise_posture_decision.md` |

---

# Accepted Decisions

## 1. Personal Mode Is the Near-Term Design Center

The near-term product is a secure personal owner-operated conversation analysis and reflection system.

The same person may act as:

```text
user
administrator
data owner
cost operator
product evaluator
```

## 2. Single-User Does Not Mean Insecure

Even when one person is both user and administrator, the product still needs:

- authentication
- session control
- owner scoping
- redacted logs
- explicit export behavior
- meaningful deletion
- protection for retained transcripts and analysis outputs

## 3. Cost State Is a Product Concept

Sleep/wake behavior is not merely infrastructure detail.

It affects the user experience and should be modeled explicitly.

Conceptual states:

```text
Asleep
Waking
Active
IdlePending
ShuttingDown
FailedWake
Maintenance
```

## 4. Active Work Blocks Sleep

The system should not shut down while active transcription, reflection, report generation, export, deletion, purge, or encryption migration work is running.

Long-running work requires explicit timeout or cancellation policy.

## 5. Enterprise Is a Future Policy Layer

Enterprise may later add organizations, workspaces, SSO, RBAC, audit, compliance, and always-on availability.

Those should be additive policy layers over stable concepts, not near-term product complexity.

---

# Out of Scope

This phase does not implement:

- new auth code
- new cost-state UI
- wake/sleep orchestration changes
- org/workspace/RBAC features
- enterprise SSO
- billing
- deployment workflow replacement
- monitoring dashboards

Those belong in later implementation planning after concept closure.

---

# Exit Criteria

Phase 001-D is complete when:

- personal owner-operated mode is accepted
- current user/admin/data owner/cost operator roles are defined
- enterprise roles are deferred
- cost state is accepted as a first-class concept
- availability policy is separated from analysis semantics
- future enterprise transition is framed as policy expansion

---

# Next Phase

Proceed to:

```text
001-E — Concept Acceptance and Refactor Readiness
```
