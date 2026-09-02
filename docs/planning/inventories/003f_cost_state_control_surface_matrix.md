# 003-F Cost-State Control Surface Matrix

## Status

Accepted as the Phase 003-F cost-state control surface implementation matrix.

---

# Purpose

Map accepted cost-state/control-plane concepts to current implementation surfaces, remaining risks, target implementation posture, and gates.

This matrix is implementation planning only.

---

# Matrix Legend

| Status | Meaning |
|---|---|
| `existing_foundation` | Useful implementation exists and should be preserved |
| `existing_but_incomplete` | Useful implementation exists but lacks accepted cost-state/control-plane semantics |
| `new_or_equivalent` | Needs a new object, field set, API, worker contract, automation, or service boundary |
| `policy_only_initially` | May begin as documented/configured policy before schema/code |
| `reference_or_stale` | Useful historical/reference material, but not current authority |
| `defer` | Valid but not needed for current implementation foundation |

---

# Surface Matrix

| Surface / Concept | Current Implementation Surface | Status | Required Implementation Target | Primary Gates |
|---|---|---|---|---|
| Cost State concept | `docs/concepts/019_cost_state_decision.md`, 002-F architecture | existing_foundation | keep Cost State first-class and separate from analysis semantics | cost_state_contract_gate |
| Cost state settings | `power_control_enabled`, `power_state_table`, `idle_sleep_after_seconds`, `power_handoff_secret` | existing_foundation | reconcile settings with accepted state vocabulary and deployment-mode policy | state_vocabulary_reconciliation_gate, wake_path_security_gate |
| Worker/job settings | `workflow_worker_enabled`, poll/max-in-flight/timeouts/stale seconds/max attempts | existing_foundation | map workflow jobs into blocking-job registry and control-plane readiness | blocking_job_registry_gate, queue_worker_recovery_gate |
| Long-job kill controls | `kill_long_jobs_enabled`, `kill_long_jobs_seconds` | existing_but_incomplete | job-class-specific kill/cancel/checkpoint semantics and user-facing warning posture | kill_mode_semantics_gate, job_safe_shutdown_gate |
| Power state storage | `PowerStateStore`, DynamoDB table when enabled, no-op when disabled | existing_foundation | `CostStateRecord` or equivalent with accepted states and transition metadata | cost_state_contract_gate, content_free_operational_event_gate |
| Current power vocabulary | `asleep`, `waking`, `awake`, `sleeping` | existing_but_incomplete | map to accepted `asleep`, `waking`, `active`, `idle_pending`, `shutting_down`, `failed_wake`, `maintenance` | state_vocabulary_reconciliation_gate |
| Activity heartbeat | `/api/v1/ops/power/heartbeat`, `touch_activity` | existing_foundation | authenticated activity signal plus keep-awake and owner-only control semantics | idle_evaluator_gate, manual_sleep_wake_gate |
| Idle timer | `start_idle_timer`, `idle_timer_started_at` | existing_foundation | explicit idle-pending state/grace model and transition into shutdown coordinator | idle_evaluator_gate |
| Idle decision | `idle_status_payload.should_sleep` | existing_foundation | shutdown preflight input, not complete shutdown authority by itself | idle_evaluator_gate, job_safe_shutdown_gate |
| Active job count | workflow-row count of created/queued/running/pending | existing_but_incomplete | generalized blocking-job registry across accepted job types | blocking_job_registry_gate |
| Power API | `/api/v1/ops/power/status`, `/idle-status`, `/heartbeat`, `/handoff`, `/start-idle-timer` | existing_foundation | owner/admin authorization review, product-safe state contract, content-free responses | wake_path_security_gate, privacy_boundary_gate |
| Public status | `GET /api/v1/ops/power/status` | existing_but_incomplete | content-free public/minimal status policy or authenticated-only decision | privacy_boundary_gate, wake_path_security_gate |
| Handoff token | `mint_handoff_token`, `parse_handoff_token`, `/handoff` | existing_foundation | short-lived purpose-specific wake/session exchange contract and tests | handoff_token_gate |
| Manual wake | described through login/wake path in operations docs | existing_but_incomplete | accepted owner-only wake control and retry-wake contract | manual_sleep_wake_gate, wake_path_security_gate |
| Manual sleep | operations doc references GitHub Actions manual pause | reference_or_stale | replace with accepted owner-only manual sleep path after GitHub Actions restoration gate | GitHub_Actions_restoration_gate, manual_sleep_wake_gate |
| Keep awake | conceptual requirement only | new_or_equivalent | bounded owner-only keep-awake control and expiry | keep_awake_bounds_gate |
| Failed wake | conceptual only | new_or_equivalent | explicit state, reason code, retry path, maintenance handoff | failed_wake_shutdown_gate |
| Failed shutdown | currently folded into failure/legacy vocabulary | new_or_equivalent | decide whether separate state is needed; if not, document alias behavior | failed_wake_shutdown_gate |
| Maintenance mode | conceptual only | new_or_equivalent | owner/operator-visible intentional unavailability state | maintenance_mode_gate |
| Workflow queue | `WorkflowJobService`, queue stats, background/dedicated worker modes | existing_foundation | queue state feeds control plane and blocks/permits shutdown according to job policy | queue_worker_recovery_gate, blocking_job_registry_gate |
| Dedicated worker | `backend/worker.py`, health server, resume incomplete, poll loop | existing_foundation | worker readiness and shutdown semantics integrated into control-plane preflight | queue_worker_recovery_gate, job_safe_shutdown_gate |
| Worker health | `/health`, `/live`, active run IDs, in-flight counts | existing_foundation | content-free control-plane health signal; avoid exposing sensitive job details | content_free_operational_event_gate, privacy_boundary_gate |
| Stale recovery | `recover_stale`, `workflow_job_stale_seconds` | existing_foundation | sleep/wake recovery contract with safe retry/fail behavior | queue_worker_recovery_gate, regression_gate |
| Resume incomplete | API startup and worker startup resume logic | existing_foundation | explicit wake/resume/reconcile state after sleep, crash, or deployment | queue_worker_recovery_gate, failed_wake_shutdown_gate |
| Cancellation | `request_cancel`, kill mode cancellation | existing_but_incomplete | job-specific cancellation policy and artifact/validation staleness behavior | job_safe_shutdown_gate, analysis_state_integrity_gate |
| Workflow timeout | `workflow_job_timeout_seconds`, engine timeout checks | existing_foundation | align timeouts with blocking-job safe-shutdown behaviors | job_heartbeat_gate, job_safe_shutdown_gate |
| Startup side effects | init DB, purge expired transcripts, resume incomplete jobs | existing_foundation | classify startup work as wake/reconcile operations; ensure they do not mask failed wake | failed_wake_shutdown_gate, deletion_cascade_safety_gate |
| Queue routes | `/api/queue/*` | existing_but_incomplete | route/auth reconciliation with privacy boundary and `/api/v1` direction | privacy_boundary_gate, deployment_documentation_reconciliation_gate |
| AWS operations doc | `docs/developer/aws-operations.md` | reference_or_stale | reconcile current power-control description with removed workflows and accepted controls | deployment_documentation_reconciliation_gate |
| GitHub Actions workflows | intentionally cleared | policy_only_initially | remain blocked until replacement/restoration plan passes gates | GitHub_Actions_restoration_gate |
| CloudWatch metrics | worker queue metrics, `RRE/Dev` | existing_foundation | control-plane observability for queue/worker/power without content | content_free_operational_event_gate |
| Analysis state boundary | analysis scope, validation, corpus, reports | existing_but_incomplete | cost-state transitions must not corrupt or redefine analysis artifacts | analysis_state_integrity_gate, corpus_staleness_gate |
| Export/deletion blocking | planned job categories, partial purge/delete behavior | existing_but_incomplete | export/deletion jobs register blocking or safe-cancel behavior | export_safety_gate, deletion_cascade_safety_gate |
| Future enterprise availability | conceptual policy layer | defer | later `AvailabilityPolicy` or equivalent over same core concepts | future_enterprise_policy_gate |

---

# Current Strengths to Preserve

- explicit power settings
- DynamoDB-backed power state option
- no-op local/dev behavior when disabled
- authenticated heartbeat route
- signed time-limited handoff tokens
- idle status using active jobs plus idle duration
- workflow queue stats
- worker health endpoint
- in-flight job tracking
- stale recovery
- long-job kill-mode protection
- worker resume on startup
- API resume of incomplete jobs when not in dedicated worker mode
- content-light worker and queue logs

---

# Priority Gaps

## P0 gaps

- accepted state vocabulary not reconciled with current `awake` / `sleeping` terms
- no `CostStateRecord` contract exposed as authoritative product/control-plane state
- no generalized `BlockingJobRecord` across all blocking job types
- idle evaluator does not yet govern a full shutdown coordinator
- job-safe shutdown is not gateable across transcription, analysis, export, deletion, purge, encryption migration, and corpus recompute
- GitHub Actions references in operations docs conflict with current cleared-workflow posture

## P1 gaps

- failed wake and failed shutdown behavior not explicit enough
- maintenance mode not first-class
- keep-awake control not implemented as a bounded owner-only control
- public vs authenticated power-status policy needs privacy review
- queue routes remain legacy `/api` surfaces
- kill-mode semantics are too coarse for mature product behavior

## P2 gaps

- future enterprise availability policy
- advanced observability/SLOs
- scheduled wake windows
- role-delegated enterprise power controls

---

# Target Object / Contract Set

Later implementation should consider this minimum target set:

```text
CostStateRecord
AvailabilityPolicy
BlockingJobRecord
IdleEvaluationResult
WakeRequest
ShutdownPreflightResult
ShutdownRequest
KeepAwakeRequest
ControlPlaneEvent
WorkerRecoveryResult
```

Equivalent means a clearly documented field/config/service contract may be acceptable before a dedicated database table, as long as gates pass.

---

# Decision

This matrix is ready to feed the 003-F work packages, 003-G UI/report planning, and 003-H exit review.
