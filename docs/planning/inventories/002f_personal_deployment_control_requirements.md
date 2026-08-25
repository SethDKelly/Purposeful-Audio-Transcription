# 002-F Personal Deployment Control Requirements

## Status

Accepted as the Phase 002-F personal deployment control requirements inventory.

---

# Purpose

Define the control requirements that later implementation must satisfy to make personal-mode sleep/wake behavior safe, visible, low-cost, and compatible with sensitive conversation analysis.

This document does not choose a cloud provider mechanism or implementation design.

---

# Control Surfaces

| Control Surface | Purpose | Personal-Mode Requirement |
|---|---|---|
| Wake request | Start required runtime resources | Owner login or manual wake triggers Waking |
| Wake status | Report progress/failure | User can distinguish Waking from FailedWake |
| Manual sleep | Reduce cost intentionally | Owner can request shutdown when safe |
| Keep awake | Prevent idle shutdown temporarily | Owner can keep system active for a bounded window |
| Idle evaluator | Detect safe idle state | Requires no user activity and no blocking jobs |
| Blocking job registry | Prevent unsafe shutdown | Active critical jobs delay or block sleep |
| Shutdown coordinator | Stop/scale/pause safely | Idempotent and safe to retry |
| Maintenance state | Represent intentional unavailability | Owner can see maintenance is deliberate |
| Operational events | Explain state changes without content | Logs IDs/status/durations only |
| Failure recovery | Recover from failed wake/shutdown | Owner sees actionable state and can retry or enter maintenance |

---

# Required Architecture Signals

Later implementation should expose these signals to the cost-state layer.

## User activity signals

```text
owner_authenticated
last_authenticated_activity_at
manual_keep_awake_until
manual_sleep_requested
manual_wake_requested
```

## Job activity signals

```text
active_blocking_job_count
blocking_job_types
last_blocking_job_heartbeat_at
oldest_blocking_job_started_at
blocking_job_timeout_at
cancel_requested
safe_shutdown_behavior
```

## Runtime state signals

```text
current_cost_state
wake_requested_at
wake_completed_at
shutdown_requested_at
shutdown_completed_at
failed_wake_reason
maintenance_message
```

## Security signals

```text
authenticated_owner_id
control_request_authorized
sensitive_content_not_logged
service_purpose
```

---

# Owner-Only Controls

In personal mode, these controls must be owner-only:

- wake
- sleep
- keep awake
- retry wake
- cancel blocking job
- enter maintenance
- clear maintenance
- view cost-state history

Future enterprise mode may delegate these through roles and policies, but that is deferred.

---

# Job Safety Controls

## Blocking job registration

Every job that may be corrupted by shutdown should register itself or be discoverable by the cost-state layer.

Candidate fields:

```text
job_id
job_type
owner_id
blocks_sleep
status
started_at
last_heartbeat_at
timeout_at
safe_shutdown_behavior
```

## Heartbeat / activity tracking

Long-running jobs should update activity so the idle evaluator does not mistake them for inactivity.

## Timeout policy

Every blocking job class should have an explicit timeout or manual-intervention policy.

## Cancellation policy

If a job can be canceled, cancellation must preserve data integrity and mark partial artifacts correctly.

## Resumability policy

If a job can resume, it must checkpoint enough state to continue safely after wake.

---

# Cost-State API Requirements

Later implementation may expose APIs or internal functions equivalent to:

```text
GET /cost-state
POST /cost-state/wake
POST /cost-state/sleep
POST /cost-state/keep-awake
POST /cost-state/retry-wake
POST /cost-state/maintenance
GET /cost-state/blocking-jobs
```

These names are illustrative only.

The required architecture behavior is:

- state is inspectable
- wake/sleep intent is explicit
- unsafe shutdown is blocked or delayed
- failed wake is visible
- operational events are content-free

---

# Deployment Boundary Requirements

Cost-state architecture should separate:

| Boundary | Meaning |
|---|---|
| Static/public surface | Minimal page or endpoint that can explain sleeping/waking state |
| Wake/control surface | Secure owner-authorized mechanism to start runtime resources |
| App runtime | Main authenticated app and APIs |
| Worker runtime | Analysis/transcription/report/export workers |
| Persistent storage | Durable encrypted data storage |
| Temporary storage | Ephemeral recording/transcription/export staging |
| Operational events | Non-content state/event records |

The exact mapping to AWS resources belongs to later implementation.

---

# User-Visible Requirements for 002-G

002-G should design language and flows for:

- `This app is asleep to save cost.`
- `Wake requested.`
- `The app is waking.`
- `The app is active.`
- `A reflection run is keeping the app awake.`
- `Idle shutdown will occur soon.`
- `Keep awake for a while.`
- `Sleep now.`
- `Wake failed; retry or enter maintenance.`
- `Maintenance mode is active.`

The exact text can change, but the concepts must remain visible.

---

# Non-Content Operational Event Requirements

Allowed event fields:

```text
event_id
state_from
state_to
trigger
owner_id or pseudonymous owner ref
job_id
job_type
status
reason_code
duration_ms
created_at
```

Forbidden event fields:

```text
transcript text
evidence quote text
audio content
prompt body
model output
report body
export content
secret values
session token
login code
```

---

# Acceptance Gates for Later Implementation

Later implementation should not be accepted unless it can show:

1. system can enter Asleep intentionally
2. owner can wake the system
3. wake status is visible
4. failed wake is represented
5. active jobs block unsafe sleep
6. idle shutdown uses both user and job activity
7. manual sleep is safe or clearly delayed
8. keep-awake is bounded
9. shutdown is idempotent
10. logs do not contain sensitive content
11. cost state does not alter analysis semantics
12. enterprise availability can be modeled as policy expansion later

---

# Decision

Personal deployment needs an explicit cost-state control layer.

The control layer may be lightweight, but it must be product-aware: visible to the owner, safe for jobs, content-free in logs, and separate from analysis semantics.
