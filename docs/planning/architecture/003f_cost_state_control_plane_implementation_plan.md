# 003-F Cost-State Control Plane Implementation Plan

## Status

Accepted as the Phase 003-F cost-state control-plane implementation plan.

This document converts the accepted Phase 002 cost-state architecture into implementation-ready work packages and gates.

It does not implement code changes, infrastructure changes, schema migrations, worker changes, queue changes, AWS automation, GitHub Actions, UI changes, auth changes, monitoring changes, or production data migrations by itself.

---

# Purpose

Prepare cost-state and personal deployment control-plane implementation work so later implementation can make low-cost personal operation safe, visible, and compatible with retained transcript analysis.

003-F turns the accepted cost-state architecture into staged implementation planning for:

- personal-mode sleep/wake state tracking
- wake request and handoff boundaries
- idle evaluation
- active-job and blocking-job coordination
- workflow worker safety
- cancellation, timeout, stale recovery, and resume semantics
- manual sleep/wake and keep-awake control surfaces
- content-free power/control-plane events
- current AWS dev operational reconciliation
- GitHub Actions replacement/restoration policy
- future enterprise availability separation
- tests and acceptance gates

---

# Governing Inputs

Primary authority:

- `docs/concepts/006_cost_availability_concepts.md`
- `docs/concepts/019_cost_state_decision.md`
- `docs/concepts/020_future_enterprise_posture_decision.md`
- `docs/planning/architecture/002f_cost_state_personal_deployment_architecture_plan.md`
- `docs/planning/inventories/002f_cost_state_transition_matrix.md`
- `docs/planning/inventories/002f_personal_deployment_control_requirements.md`
- `docs/planning/architecture/003c_data_lifecycle_retention_foundation_implementation_plan.md`
- `docs/planning/architecture/003d_privacy_boundary_encryption_baseline_implementation_plan.md`
- `docs/planning/architecture/003e_analysis_boundary_validation_implementation_plan.md`

Implementation reference inspected:

- `config/settings.py`
- `backend/services/power_service.py`
- `backend/api/routes/power.py`
- `backend/services/workflow_job_service.py`
- `backend/worker.py`
- `backend/services/workflow_engine.py`
- `backend/main.py`
- `backend/api/routes/queue.py`
- `docs/developer/aws-operations.md`

---

# Accepted Cost-State Principle

```text
Personal mode optimizes for low cost through explicit sleep/wake behavior.
Enterprise mode may later change availability policy without redefining the core product concepts.
```

Cost state may affect when the application is available.

Cost state must not change the meaning of transcripts, evidence quotes, findings, hypotheses, safety posture, reflection points, reports, cases, exports, or reasoning graph objects.

---

# Current Implementation Baseline

The prototype already has useful cost-state/control-plane foundations:

1. Settings include power-control configuration: `power_control_enabled`, `power_state_table`, `power_handoff_secret`, and `idle_sleep_after_seconds`.
2. Settings include long-job and worker controls: `kill_long_jobs_enabled`, `kill_long_jobs_seconds`, workflow worker polling, max in-flight jobs, job timeout, stale recovery, and max attempts.
3. `PowerStateStore` can use DynamoDB for power state and no-ops when power control is disabled.
4. Power state currently tracks state, last activity, idle timer start, active job count, wake request time, and message-like metadata.
5. `/api/v1/ops/power` exposes status, admin idle-status, authenticated heartbeat, Lambda handoff-token exchange, and admin idle timer start.
6. Handoff tokens are signed and time-limited.
7. `idle_status_payload` derives active job count from workflow run rows and computes whether the app should sleep based on state, active jobs, and idle duration.
8. The dedicated worker process has a health endpoint reporting in-flight count, max in-flight count, and active run IDs.
9. Workflow job service tracks in-flight futures and active run IDs, supports background execution, dedicated-worker queueing, stale recovery, max attempts, kill-mode cancellation, and queue stats.
10. Worker startup resumes incomplete runs and periodically publishes queue metrics when CloudWatch is available.
11. API startup resumes incomplete jobs only when not in dedicated worker mode.
12. Logging patterns for worker/power/queue events are mostly operational IDs, counts, statuses, and durations rather than transcript content.

The baseline is stronger than a purely conceptual cost-state plan, but it is not yet the mature control-plane model.

Current gaps and risks:

- current implementation uses `awake` / `sleeping` vocabulary while accepted concepts use `Active`, `IdlePending`, `ShuttingDown`, `FailedWake`, and `Maintenance`
- no first-class `CostStateRecord` domain/API contract reconciles accepted state names with current power-store fields
- no first-class `BlockingJobRecord` or generalized blocking-job registry exists across transcription, analysis, export, deletion, purge, encryption migration, and corpus recompute jobs
- active job counting is currently workflow-run centric and does not cover all accepted blocking job categories
- idle status has a `should_sleep` decision but not a complete shutdown coordinator contract
- wake orchestration exists in operational notes and handoff route pieces, but the repository does not yet contain a complete accepted wake/sleep implementation contract
- manual sleep in `docs/developer/aws-operations.md` still references GitHub Actions even though repository entry points state workflows were intentionally cleared
- queue endpoints are under the older `/api` surface and need route/auth reconciliation with the privacy boundary plan
- kill mode cancels all active workflow jobs after a long-job threshold, but later implementation needs clearer user-facing semantics, job-specific behavior, and validation/corpus safety rules
- failed shutdown is not represented distinctly from failed wake
- maintenance state is accepted conceptually but not first-class in current runtime surfaces
- control-plane events need explicit content-free allowlists and tests
- future enterprise availability policy is not yet represented as a deployment-mode abstraction

---

# Accepted Implementation Principle

```text
The control plane must make low-cost sleep/wake behavior explicit and safe without corrupting active work, retained evidence, validation state, deletion cascades, exports, or corpus reasoning.
```

A personal deployment may intentionally sleep.

A sleeping or waking system should not feel like an unexplained outage.

---

# Implementation Planning Decisions

## 1. Cost-state vocabulary must be normalized before broad automation changes

Later implementation should define a compatibility mapping from current power-store vocabulary to accepted product/control-plane vocabulary.

Accepted conceptual states:

```text
asleep
waking
active
idle_pending
shutting_down
failed_wake
failed_shutdown optional
maintenance
```

Current implementation terms such as `awake` and `sleeping` may remain as adapter-layer aliases temporarily, but product-facing APIs and documentation should converge on the accepted vocabulary.

## 2. CostStateRecord should become the central control-plane contract

A `CostStateRecord` or equivalent should represent current availability/cost posture separately from analysis state.

Minimum fields should cover:

```text
id
mode
state
state_reason
last_wake_requested_at
last_wake_completed_at
last_authenticated_activity_at
last_blocking_job_activity_at
idle_window_seconds
idle_timer_started_at
manual_keep_awake_until
last_shutdown_requested_at
last_shutdown_started_at
last_shutdown_completed_at
last_failed_wake_at
last_failed_shutdown_at
failure_reason_code
maintenance_message
updated_at
```

The object should not contain transcript text, prompt payloads, model completions, report bodies, export content, secrets, login codes, or session tokens.

## 3. BlockingJobRecord should generalize beyond workflow runs

Workflow runs are the current best foundation, but accepted blocking jobs include more than workflow jobs.

Later implementation should define `BlockingJobRecord` or an equivalent service contract with:

```text
job_id
job_type
owner_id optional in personal mode but required when tied to sensitive artifacts
artifact_refs
blocks_sleep
status
started_at
last_heartbeat_at
timeout_at
cancel_requested
resume_policy
safe_shutdown_behavior
content_free_failure_code
```

Accepted job types:

```text
transcription
transcript_preparation
reflection_run
synthesis_or_report_generation
export_generation
deletion_cascade
purge_worker
encryption_migration
corpus_graph_recompute
```

## 4. Idle evaluation must depend on both user activity and blocking jobs

The accepted idle rule remains:

```text
no authenticated user activity within idle window
and
no active blocking jobs
```

Later implementation should avoid using frontend presence alone as the activity signal.

The existing heartbeat route and idle timer are useful foundations, but they should be reconciled with authenticated activity, manual keep-awake, service-purpose activity, and job heartbeats.

## 5. Shutdown coordination must be explicit and idempotent

Later implementation should define a shutdown coordinator that:

- checks blocking jobs before shutdown
- delays or denies manual sleep when work cannot stop safely
- safe-cancels jobs only when their policy allows it
- starts shutdown only after safe state is confirmed
- can retry shutdown without duplicate side effects
- records content-free state transitions
- distinguishes failed wake from failed shutdown when needed

## 6. Wake orchestration must remain minimal, secure, and visible

Wake should be triggered by owner login, manual wake, or future explicit scheduled wake.

The minimal wake path should not expose retained sensitive content before authentication and handoff succeed.

Handoff tokens should remain time-limited, signed, and purpose-specific.

Wake status should be visible as `waking`, `active`, `failed_wake`, or `maintenance` rather than a generic failure.

## 7. Kill mode needs product-safe semantics

Current kill mode is useful as a cost-control protection, but later implementation should document exact behavior for each job class.

The mature model should distinguish:

```text
block_until_complete
cancel_safely
checkpoint_and_resume
allow_after_timeout
not_blocking
```

Cancelling all active workflow jobs may remain a personal-mode emergency control, but it needs user-facing language, validation-state preservation, corpus/report staleness handling, and regression tests before being treated as mature behavior.

## 8. Queue and worker status should become part of control-plane readiness

Worker health and queue stats are already useful.

Later implementation should align them with cost-state contracts so the control plane can answer:

- Are jobs queued?
- Are jobs actively running?
- Which job types block sleep?
- Are jobs stale?
- Can shutdown start safely?
- Can wake/resume recover in-flight work?

Queue status should not expose sensitive content.

## 9. GitHub Actions should remain blocked until replaced by the new control model

GitHub Actions workflows were intentionally cleared earlier.

Operational documentation that references manual sleep through GitHub Actions is now reference/stale guidance for Phase 003 purposes.

Do not restore GitHub Actions merely to regain old deployment behavior.

Any future workflow restoration must pass cost-state, privacy, job-safety, and release-readiness gates.

## 10. Enterprise availability is a deployment policy extension

Future enterprise mode may support always-on services, scheduled uptime, autoscaling workers, high-availability storage, monitoring, alerting, SLOs, organization roles, and admin/billing policies.

That should be modeled as `AvailabilityPolicy` or equivalent, not as a rewrite of core transcript/analysis/case/report concepts.

---

# Proposed Implementation Sequence

## Stage 0 — Cost-state authority lock

Create implementation-facing notes that point developers to the current cost-state authority and mark old GitHub Actions/manual-pause guidance as reference until reconciled.

## Stage 1 — Current control-surface inventory

Inventory settings, power service, power API, queue API, workflow job service, worker process, startup/resume behavior, AWS operational docs, and deleted workflow assumptions.

## Stage 2 — CostStateRecord compatibility design

Define accepted state vocabulary, adapter mapping from `awake`/`sleeping`, state transition rules, persistence choice, API shape, and content-free event fields.

## Stage 3 — BlockingJobRecord design

Define job types, heartbeat behavior, timeout behavior, cancel/resume/safe-shutdown behavior, owner/artifact binding, and how workflow runs map into the generalized blocking-job contract.

## Stage 4 — Idle evaluator design

Define authenticated activity signals, manual keep-awake, idle timer semantics, blocking job checks, idle-pending grace behavior, and transition to shutdown.

## Stage 5 — Wake/handoff design

Define minimal wake surface, handoff-token boundaries, retry behavior, failed-wake behavior, maintenance mode, and security/privacy requirements.

## Stage 6 — Shutdown coordinator design

Define manual sleep, automatic idle shutdown, shutdown preflight, job-safe delay/deny/cancel/checkpoint behavior, idempotent cloud actions, failed-shutdown state, and recovery.

## Stage 7 — Worker/queue recovery design

Define how queued, running, stale, failed, cancelled, and resumed jobs interact with sleep/wake transitions.

## Stage 8 — Operational documentation reconciliation

Update or supersede AWS operations references that depend on removed GitHub Actions, old manual pause flows, or old status vocabulary.

## Stage 9 — Test/evaluation plan

Define tests for state transitions, idle evaluation, job-safe shutdown, kill mode, stale recovery, handoff security, content-free events, queue/worker status, and no analysis-state corruption.

## Stage 10 — Future availability policy plan

Define how personal and future enterprise modes differ without redefining core product concepts.

---

# Required Gates

003-F carries forward or introduces these gates for later implementation:

- cost state contract gate
- state vocabulary reconciliation gate
- wake path security gate
- handoff token gate
- idle evaluator gate
- blocking job registry gate
- job heartbeat gate
- job-safe shutdown gate
- manual sleep/wake gate
- keep-awake bounds gate
- kill-mode semantics gate
- queue/worker recovery gate
- failed wake/shutdown gate
- maintenance mode gate
- content-free operational event gate
- privacy boundary gate
- analysis state integrity gate
- deletion cascade safety gate
- export safety gate
- corpus staleness gate
- GitHub Actions restoration gate
- deployment documentation reconciliation gate
- evaluation gate
- regression gate
- release readiness gate

---

# Handoff to 003-G

003-G should prepare UI/report implementation planning for:

- showing asleep/waking/active/idle-pending/shutting-down/failed/maintenance status
- explaining intentional sleep for cost control
- showing active jobs keeping the app awake
- exposing manual sleep/wake/keep-awake controls safely
- explaining delayed manual sleep when jobs block shutdown
- showing failed wake/retry/maintenance choices
- avoiding the impression that cost-state behavior changes report or analysis meaning

---

# Handoff to 003-H

003-H should consolidate whether Phase 003 has enough implementation-readiness material to authorize a next implementation phase.

For cost-state work, 003-H should specifically check:

- whether old GitHub Actions references are reconciled or explicitly deferred
- whether control-plane work packages are sequenced behind privacy and analysis gates
- whether job-safe shutdown has a blocking acceptance gate
- whether enterprise availability remains a future policy layer

---

# Non-goals

003-F does not implement:

- code changes
- schema migrations
- DynamoDB changes
- Lambda/CodeBuild changes
- ECS/RDS/VPC endpoint automation
- GitHub Actions restoration
- auth changes
- worker changes
- queue changes
- UI changes
- monitoring changes
- alerting changes
- production data migration

---

# Acceptance Result

The cost-state control-plane implementation plan is ready to feed 003-G and the Phase 003 exit review.

Proceed next to:

```text
003-G — UI/Report Alignment Implementation Plan
```
