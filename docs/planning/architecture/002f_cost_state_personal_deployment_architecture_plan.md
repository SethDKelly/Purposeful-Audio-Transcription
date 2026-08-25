# 002-F Cost State and Personal Deployment Architecture Plan

## Status

Accepted as the Phase 002-F architecture plan.

This document translates the accepted cost-state, personal operating model, and future enterprise posture decisions into architecture requirements for later implementation phases.

It does not authorize code, infrastructure, deployment, pipeline, scheduler, or workflow changes by itself.

---

# Purpose

Define how personal-mode sleep/wake behavior should work as a product architecture concern.

The goal is to minimize operating cost while preserving:

- safe access to sensitive retained data
- clear user-visible availability state
- safe handling of active jobs
- predictable wake and shutdown behavior
- future enterprise availability policy without redefining product concepts

This plan builds on:

- `docs/concepts/006_cost_availability_concepts.md`
- `docs/concepts/018_personal_operating_model_decision.md`
- `docs/concepts/019_cost_state_decision.md`
- `docs/concepts/020_future_enterprise_posture_decision.md`

---

# Accepted Cost-State Principle

```text
Personal mode optimizes for low cost through explicit sleep/wake behavior.
Enterprise mode may later change availability policy without redefining the core product concepts.
```

---

# Architecture Decision Summary

## 1. Cost State is a control-plane concept

`Cost State` should be represented by a deployment/control-plane architecture layer.

It should not be embedded in analysis semantics, transcript semantics, prompt logic, or report interpretation.

Cost State may affect when the system is available, but it must not change what an analysis object means.

## 2. Personal mode is allowed to be intentionally asleep

In personal mode, the application is not expected to be always-on.

The system may sleep aggressively when unused.

The user experience should treat wake latency as intentional cost control, not as an error.

## 3. Login or manual wake initiates availability

Accepted wake triggers:

```text
owner login
manual wake control
future scheduled wake, if explicitly added
```

The wake path must be minimal, secure, and clear enough for the owner to understand system status.

## 4. Idle shutdown depends on user activity and job activity

The system should not shut down merely because no browser request is active.

Shutdown requires both:

```text
no authenticated user activity
no active blocking job
```

for the configured idle window.

Recommended personal-mode default remains:

```text
2 hours
```

## 5. Active jobs block sleep unless timeout/cancel policy applies

Sleep/wake behavior must not corrupt active work.

Blocking job categories include:

- transcription
- transcript preparation
- reflection run
- synthesis/report generation
- export generation
- deletion/purge cascade
- encryption/decryption migration
- corpus graph recomputation, if later introduced

Long-running jobs require explicit timeout, cancellation, resumability, or safe-fail policy.

## 6. Cost State requires user-visible status

The owner should be able to understand when the system is:

```text
Asleep
Waking
Active
IdlePending
ShuttingDown
FailedWake
Maintenance
```

At minimum, later UI/API design should expose enough state for the user to know whether the app is waking, active, idle-pending, or failed to wake.

## 7. Enterprise availability is a policy expansion

Future enterprise mode may use scheduled uptime, always-on services, autoscaling workers, high-availability storage, monitoring, and alerting.

Those are availability policy changes.

They must not redefine:

- Transcript
- Evidence Quote
- Reflection Run
- Hypothesis
- Confidence
- Reflection Point
- Case
- Reasoning Graph
- Privacy Boundary
- Retention Rule

---

# Cost State Model

Use this conceptual state vocabulary.

```text
Asleep
Waking
Active
IdlePending
ShuttingDown
FailedWake
Maintenance
```

## Asleep

The system is minimized for cost.

Allowed retained resources may include:

- persistent storage
- secrets
- minimal wake/auth path
- power/control-plane state
- low-cost routing component if required by implementation

Expensive runtime resources should be stopped, scaled to zero, paused, or removed according to deployment policy.

## Waking

The owner has requested access and required resources are starting.

User-facing requirement:

```text
Show that wake is in progress and intentional.
```

## Active

The system is usable.

Authenticated user activity or blocking background jobs keep the system active.

## IdlePending

The system has no recent authenticated user activity and no active blocking jobs, but the idle window has not yet completed or shutdown has not yet begun.

User-facing requirement:

```text
Show or infer that the system may shut down soon unless activity resumes or keep-awake is requested.
```

## ShuttingDown

The control plane is reducing cost by stopping, scaling down, pausing, or deleting runtime resources according to policy.

Shutdown must be idempotent and safe to retry.

## FailedWake

The system attempted to wake but did not reach a usable state.

User-facing requirement:

```text
Provide actionable feedback rather than silent failure.
```

## Maintenance

The system is intentionally unavailable for maintenance, redesign, migration, or manual intervention.

---

# Control-Plane Architecture Requirements

Later implementation should define a control-plane component or service boundary responsible for:

1. recording current cost state
2. accepting wake requests
3. accepting manual sleep requests
4. evaluating idle policy
5. checking active blocking jobs
6. preventing unsafe shutdown
7. initiating shutdown
8. reporting failed wake
9. surfacing maintenance state
10. writing non-sensitive operational lifecycle events

The control plane may be implemented as scripts, APIs, scheduled jobs, cloud automation, or a dedicated service later.

002-F only defines the architecture responsibilities.

---

# Candidate CostStateRecord

Purpose:

Represent the current power/availability posture without mixing cost state into analysis data.

Candidate fields:

```text
id
mode
state
state_reason
last_wake_requested_at
last_wake_completed_at
last_user_activity_at
last_blocking_job_activity_at
idle_window_seconds
manual_keep_awake_until
last_shutdown_started_at
last_shutdown_completed_at
last_failed_wake_at
failed_wake_reason
maintenance_message
updated_at
```

## Mode values

```text
personal
future_enterprise
maintenance
```

## State values

```text
asleep
waking
active
idle_pending
shutting_down
failed_wake
maintenance
```

---

# Candidate BlockingJobRecord

Purpose:

Allow cost-state logic to identify jobs that should delay or prevent shutdown.

Candidate fields:

```text
id
owner_id
job_type
job_id
blocks_sleep
status
started_at
last_heartbeat_at
timeout_at
cancel_requested
resume_policy
safe_shutdown_behavior
```

## Blocking job types

```text
transcription
transcript_preparation
reflection_run
report_generation
export_generation
deletion_cascade
purge_worker
encryption_migration
corpus_graph_recompute
```

## Safe shutdown behavior values

```text
block_until_complete
cancel_safely
checkpoint_and_resume
allow_after_timeout
not_blocking
```

---

# Idle Evaluation Rule

Conceptual rule:

```text
if mode == personal
and state == active
and no authenticated user activity within idle window
and no blocking jobs are active
then enter IdlePending or ShuttingDown according to policy
```

Idle evaluation must consider both:

- user activity
- job activity

It must not rely only on frontend presence.

---

# Manual Controls

Personal mode should support these controls later:

| Control | Purpose |
|---|---|
| Manual wake | Owner starts the system intentionally |
| Manual sleep | Owner shuts down expensive resources intentionally |
| Keep awake | Owner temporarily prevents idle shutdown |
| Cancel blocking job | Owner cancels long-running work where safe |
| Retry wake | Owner retries after FailedWake |
| Enter maintenance | Owner marks system intentionally unavailable |

These controls should be owner-only in personal mode.

---

# User-Facing Status Requirements

Later UI/API planning should make these visible or inferable:

- app is asleep to save cost
- wake requested
- wake in progress
- active and usable
- active jobs are keeping system awake
- idle shutdown may occur
- manual keep-awake is active
- shutdown is in progress
- wake failed
- maintenance mode is active

Detailed UI copy belongs to 002-G.

---

# Security and Privacy Requirements

Cost-state architecture must preserve the privacy decisions from 002-D.

Cost-state records may include operational metadata, but must not include:

- transcript bodies
- evidence quote text
- prompt payloads
- model completions
- report bodies
- audio content
- export content
- secrets
- session tokens
- login codes

Wake/sleep logs should use IDs, status, durations, state changes, and error categories only.

---

# Job Safety Requirements

Shutdown must not corrupt active work.

Later implementation should ensure:

- active jobs heartbeat or otherwise report activity
- stale jobs can be identified
- timeout/cancel policies are explicit
- shutdown can be retried safely
- partial work is either checkpointed, canceled safely, or marked failed
- destructive operations such as deletion cascades are not interrupted unsafely
- wake after failed shutdown can reconcile state

---

# Deployment Policy Separation

Cost State is stable.

Deployment policy can vary.

| Concept | Personal Mode | Future Enterprise Mode |
|---|---|---|
| Availability posture | Aggressive sleep/wake | Always-on, scheduled, or autoscaled |
| Wake trigger | Login/manual | Scheduled, autoscale, operator, SSO activity |
| Idle shutdown | Default behavior | Optional or disabled |
| Long jobs | Block sleep or use timeout/cancel | Worker autoscaling/queues |
| Monitoring | Owner-visible lightweight status | Alerting/observability/SLOs |
| Cost operator | Personal owner | Organization/admin/billing owner |

---

# Handoff to 002-G

002-G should define user-facing language and flows for:

- asleep state
- wake progress
- failed wake
- idle warning
- manual sleep/wake
- keep-awake control
- active job preventing shutdown
- maintenance mode
- cost-state wording that does not look like product failure

---

# Handoff to 002-H

002-H should convert this architecture into a refactor backlog and acceptance gates, including:

- cost-state record or equivalent
- blocking job status model
- idle evaluator
- wake/sleep control surface
- shutdown safety gates
- non-content operational events
- tests for job-safe shutdown behavior
- removal or replacement plan for old GitHub Actions workflow assumptions

---

# Non-goals

002-F does not implement:

- cloud scripts
- AWS lifecycle rules
- GitHub Actions
- database migrations
- worker queue changes
- UI changes
- auth changes
- monitoring stack
- autoscaling policy

Implementation remains blocked until Phase 002-I exit review authorizes the next phase.

---

# Acceptance Result

The cost-state and personal deployment architecture is ready to feed 002-G and 002-H.

Proceed next to:

```text
002-G — UI/UX Concept Alignment Plan
```
