# 003-F Job-Safe Shutdown Gate Checklist

## Status

Accepted as the Phase 003-F cost-state, worker, wake/sleep, and job-safe shutdown gate checklist.

---

# Purpose

Define the minimum questions later implementation must answer before cost-state, wake, sleep, idle, worker, queue, shutdown, GitHub Actions, deployment, or control-plane changes are accepted.

This checklist is not code.

---

# Gate Principle

```text
A system is not safe to sleep merely because it is idle at the browser; it is safe to sleep only when authenticated activity, blocking jobs, retention/deletion work, validation state, export work, corpus state, and shutdown idempotency have been checked.
```

---

# Universal Cost-State Checklist

Every cost-state/control-plane implementation must answer:

1. What cost state is the system currently in?
2. Is the state expressed in accepted vocabulary or a documented compatibility alias?
3. Who is authorized to view or change this state?
4. Was wake, sleep, keep-awake, maintenance, or shutdown requested explicitly?
5. Is the request owner-authorized in personal mode?
6. Has authenticated user activity occurred within the idle window?
7. Are any blocking jobs active?
8. Are queued jobs waiting to run?
9. Are any jobs stale, failed, cancelling, retrying, or resuming?
10. Can each active job stop safely, block shutdown, checkpoint, resume, or fail cleanly?
11. Is shutdown idempotent and retry-safe?
12. Are failure states visible as failed wake, failed shutdown, or maintenance rather than silent outage?
13. Are all control-plane events content-free?
14. Does cost-state behavior preserve analysis, retention, deletion, export, and corpus integrity?
15. Are tests defined for normal, failure, and recovery paths?

---

# Operation-Specific Checks

## Cost state contract

Required checks:

- accepted states are defined
- current runtime aliases are documented
- state transitions are validated
- state records contain no sensitive content
- state changes write content-free events
- local/dev no-op behavior is clearly distinct from deployed power-control behavior

Blocking failure examples:

- UI/API exposes `awake` while documentation expects `active` with no mapping
- state record stores transcript title/body/prompt/report text
- power-control disabled state is mistaken for deployed sleep/wake readiness

---

## Wake path and handoff

Required checks:

- wake is owner-initiated or explicitly scheduled by policy
- wake status is visible
- retained sensitive content is not exposed before auth/handoff
- handoff tokens are signed, short-lived, and purpose-specific
- failed wake records reason code and retry path
- maintenance can be used for intentional intervention

Blocking failure examples:

- wake endpoint allows unauthenticated sensitive access
- handoff token has no expiration or weak signing
- wake failure appears only as generic downtime

---

## Idle evaluation

Required checks:

- idle window is configured
- authenticated server-side activity updates state
- frontend presence alone does not determine activity
- manual keep-awake has a bounded expiration
- active blocking jobs prevent or delay idle shutdown
- queued jobs are considered according to policy
- idle-pending transition is represented or deliberately collapsed into shutdown with documented reasoning

Blocking failure examples:

- app shuts down during active reflection run because browser is quiet
- app never sleeps because heartbeat is unauthenticated/noisy
- keep-awake has no maximum or audit trail

---

## Blocking job registry

Required checks:

- every job class declares whether it blocks sleep
- job type is identified
- owner/artifact binding is present when job touches sensitive artifacts
- heartbeat or last-activity signal exists for long jobs
- timeout behavior is explicit
- cancellation behavior is explicit
- resume behavior is explicit
- safe shutdown behavior is explicit

Blocking failure examples:

- deletion cascade can be interrupted mid-cascade with no resume/stale state
- export generation is killed after writing partial retained artifact
- corpus recompute continues using stale evidence after wake/retry

---

## Workflow queue and worker recovery

Required checks:

- queued jobs are visible to control-plane preflight
- in-flight jobs are visible
- stale recovery has clear retry/fail behavior
- worker restart cannot duplicate execution unsafely
- API and dedicated worker modes do not both claim the same job
- worker health is content-free
- queue routes are reconciled with privacy/auth policy

Blocking failure examples:

- wake resumes the same workflow twice
- queue stats expose sensitive transcript/report content
- stale job remains permanently running and blocks sleep forever

---

## Manual sleep

Required checks:

- manual sleep is owner-only in personal mode
- manual sleep runs shutdown preflight
- unsafe blocking jobs delay or deny sleep with user-visible reason
- safe-cancel jobs are cancelled according to job policy
- shutdown state is recorded
- failed shutdown is recoverable

Blocking failure examples:

- manual sleep kills a running deletion cascade without checkpoint
- manual sleep ignores active export generation
- failed shutdown leaves state as active or asleep incorrectly

---

## Automatic idle shutdown

Required checks:

- idle evaluator confirms no authenticated activity
- blocking job registry confirms no active blocking jobs
- shutdown coordinator confirms safe shutdown
- shutdown is idempotent
- resources can be stopped/scaled/deleted in correct order
- failed steps record recoverable reason codes
- post-shutdown state is explicit

Blocking failure examples:

- idle shutdown stops worker while queue still has active blocking jobs
- VPC endpoint/RDS/ECS step failure is not recorded
- repeated shutdown attempts cause duplicate destructive side effects

---

## Kill mode

Required checks:

- kill threshold is explicit
- affected job classes are explicit
- kill mode cancellation is safe for artifacts involved
- validation/report/corpus state is marked failed, cancelled, stale, or retryable as needed
- idle timer behavior after kill mode is explicit
- user-facing status explains what happened

Blocking failure examples:

- kill mode cancels analysis but leaves report as completed
- kill mode cancels all jobs with no audit/event record
- killed corpus job leaves stale high-confidence corpus claim active

---

## Analysis, retention, deletion, export, and corpus integrity

Required checks:

- sleep/wake does not modify analysis scope
- transcript-version basis survives cancellation/retry/resume
- validation state is not lost
- retained report status reflects incomplete/failed/cancelled jobs
- deletion cascades are not interrupted unsafely
- export artifacts are not partially retained without state
- corpus graph objects are stale-marked, recomputed, or failed when source evidence changes

Blocking failure examples:

- resumed analysis uses a different transcript version from the original run
- cancelled export remains downloadable as if complete
- deleted evidence continues to support corpus graph after wake

---

## Operational events and logs

Required checks:

- event allowlist is defined
- reason codes are content-free
- event fields contain IDs/status/counts/durations only
- transcript, quote, prompt, completion, report, export, login code, session token, and secrets are forbidden
- logs from wake/sleep/worker/queue/kill/stale recovery are tested

Blocking failure examples:

- wake failure logs a prompt or transcript body
- queue error logs report JSON
- handoff event logs raw token

---

## Deployment documentation and GitHub Actions

Required checks:

- current operational docs do not present removed workflows as active authority
- GitHub Actions restoration has an explicit plan and gate
- manual sleep/wake instructions reflect accepted control plane
- old pause/resume paths are marked historical, reference, or superseded
- release readiness checks include job-safe shutdown and privacy gates

Blocking failure examples:

- docs tell operators to run a removed workflow as the preferred manual sleep path
- GitHub Actions are restored without privacy/job-safety gates
- deployment notes contradict accepted Cost State vocabulary

---

# Required Test Families

Later implementation should add tests for:

```text
cost_state_alias_mapping
cost_state_transition_valid
power_status_content_free
wake_requires_owner_or_policy
handoff_token_signed_and_expires
heartbeat_requires_auth
idle_not_ready_when_user_active
idle_not_ready_when_blocking_job_active
idle_ready_after_window_no_jobs
keep_awake_blocks_idle_until_expiry
manual_sleep_owner_only
manual_sleep_denied_when_job_blocks
shutdown_preflight_lists_blocking_jobs
shutdown_idempotent_retry_safe
failed_wake_visible
failed_shutdown_visible
maintenance_mode_visible
blocking_job_heartbeat_refreshes_activity
workflow_worker_in_flight_blocks_sleep
stale_workflow_recovery_requeues_or_fails
kill_mode_marks_jobs_cancelled_or_failed
kill_mode_preserves_validation_and_report_state
queue_stats_content_free
control_plane_events_content_free
no_analysis_scope_change_after_resume
no_transcript_version_change_after_resume
no_deleted_evidence_active_after_wake
removed_github_actions_not_documented_as_current
```

---

# Validation Ordering

Recommended gate order:

```text
1. Cost-state vocabulary and contract
2. Owner/auth/privacy check for control action
3. Wake/handoff or manual sleep request validation
4. Authenticated activity and idle-window check
5. Blocking job registry check
6. Job heartbeat/stale/recovery check
7. Shutdown preflight
8. Analysis/deletion/export/corpus integrity check
9. Content-free operational event/log check
10. User-visible status/reporting check
11. Deployment documentation reconciliation
12. Regression and release readiness checks
```

Reason:

The system must know what state it is in and whether the caller is authorized before it evaluates shutdown safety. Job and integrity checks must pass before any runtime resource is stopped.

---

# Decision

This checklist carries forward to later implementation phases as part of the cost-state contract gate, wake path security gate, idle evaluator gate, blocking job registry gate, job-safe shutdown gate, privacy boundary gate, analysis state integrity gate, deletion/export/corpus safety gates, evaluation gate, regression gate, and release readiness gate.
