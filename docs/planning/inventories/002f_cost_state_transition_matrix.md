# 002-F Cost State Transition Matrix

## Status

Accepted as the Phase 002-F cost-state transition matrix.

---

# Purpose

Provide a compact reference for personal-mode sleep/wake state transitions.

This matrix is governed by:

- `docs/concepts/006_cost_availability_concepts.md`
- `docs/concepts/019_cost_state_decision.md`
- `docs/planning/architecture/002f_cost_state_personal_deployment_architecture_plan.md`

---

# State Transition Matrix

| From State | Trigger | Guard / Condition | To State | Notes |
|---|---|---|---|---|
| Asleep | Owner login | Wake path available | Waking | Default personal-mode wake trigger |
| Asleep | Manual wake | Owner authorized | Waking | Owner-only control |
| Asleep | Maintenance requested | Owner/operator decision | Maintenance | Optional personal control |
| Waking | Required services ready | Health checks pass | Active | App becomes usable |
| Waking | Wake failure | Health checks fail / timeout | FailedWake | User receives actionable feedback |
| Waking | Maintenance requested | Owner/operator decision | Maintenance | Used for intentional intervention |
| Active | User activity | Authenticated activity present | Active | Refreshes idle window |
| Active | Blocking job active | Job heartbeat/status active | Active | Blocks sleep while safe/required |
| Active | No activity + no blocking job | Idle threshold reached | IdlePending | Recommended threshold: 2 hours unless changed |
| Active | Manual sleep | No unsafe blocking jobs | ShuttingDown | Owner-requested cost reduction |
| Active | Manual sleep | Blocking job cannot stop safely | Active | Sleep denied or delayed with explanation |
| Active | Maintenance requested | Owner/operator decision | Maintenance | Should handle active jobs according to policy |
| IdlePending | User activity resumes | Authenticated activity present | Active | Cancels pending idle shutdown |
| IdlePending | Blocking job starts | Job registered/heartbeat | Active | Job now keeps system awake |
| IdlePending | Idle grace completes | No user activity and no blocking job | ShuttingDown | Shutdown begins |
| IdlePending | Manual keep-awake | Owner authorized | Active | Keep-awake extends availability |
| ShuttingDown | Shutdown completed | Runtime resources reduced safely | Asleep | Final low-cost state |
| ShuttingDown | Shutdown failure | Cannot stop safely / resource error | FailedWake | Operational failure state; name may later split into FailedShutdown |
| ShuttingDown | Blocking job discovered | Unsafe to stop | Active | Abort shutdown if safe to do so |
| FailedWake | Retry wake | Owner authorized | Waking | Retrying is explicit |
| FailedWake | Manual sleep / reset | Owner authorized | Asleep | Clear failed wake if resources are safely minimized |
| FailedWake | Maintenance requested | Owner/operator decision | Maintenance | Used for manual investigation |
| Maintenance | Maintenance complete | Owner/operator decision | Asleep | Default return if not actively waking |
| Maintenance | Owner wake | Maintenance cleared | Waking | Explicit reactivation |

---

# Transition Rules

## Wake rules

- Wake must be explicit.
- Wake must not expose sensitive content before authentication succeeds.
- Wake progress should be visible.
- Failed wake must be represented explicitly.

## Active rules

- Active user activity keeps the system awake.
- Active blocking jobs keep the system awake.
- Activity should be tracked by server-side state, not only browser presence.

## Idle rules

- Idle requires both no authenticated user activity and no blocking jobs.
- Recommended personal-mode idle window remains 2 hours.
- Keep-awake may extend the window.

## Shutdown rules

- Shutdown must be idempotent.
- Shutdown must not corrupt jobs.
- Shutdown should be delayed, denied, or safe-canceled when blocking jobs are present.
- Shutdown events must not log sensitive content.

## Failure rules

- Failed wake should be actionable.
- Failed shutdown may later become a separate state if implementation needs it.
- Maintenance may be used for manual intervention.

---

# Blocking Job Categories

These jobs should normally block sleep unless their safe-shutdown behavior says otherwise:

| Job Type | Default Sleep Behavior |
|---|---|
| transcription | block until complete, timeout, or safe cancel |
| transcript_preparation | block or checkpoint |
| reflection_run | block, checkpoint, or mark failed safely |
| report_generation | block or mark failed safely |
| export_generation | block or safe cancel |
| deletion_cascade | block until safe checkpoint |
| purge_worker | allow retry if idempotent |
| encryption_migration | block unless migration is resumable |
| corpus_graph_recompute | checkpoint/resume if later introduced |

---

# Open Implementation Choices

The matrix does not decide:

- exact cloud mechanism for wake
- exact cloud mechanism for shutdown
- whether FailedShutdown becomes separate from FailedWake
- exact idle grace period after IdlePending
- exact heartbeat frequency
- exact long-job timeout durations
- exact keep-awake maximum

Those belong to later implementation planning after Phase 002-I.
