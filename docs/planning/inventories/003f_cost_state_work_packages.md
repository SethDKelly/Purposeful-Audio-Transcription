# 003-F Cost-State Control Plane Work Packages

## Status

Accepted as the Phase 003-F cost-state control-plane implementation-planning work package inventory.

These packages are not implementation authorization.

---

# Purpose

Break cost-state/control-plane work into later implementation-ready packages.

Each package must be gated before code, schema, route, worker, cloud automation, GitHub Actions, deployment, monitoring, UI, or production data migration changes are accepted.

---

# Work Package Legend

| Field | Meaning |
|---|---|
| ID | Stable Phase 003-F work package identifier |
| Priority | P0, P1, or P2 |
| Target | Main implementation area later affected |
| Gate | Acceptance gate that must pass before implementation is accepted |

---

# P0 Work Packages

## CCP-WP-001 — Cost-state authority and vocabulary reconciliation

Priority: P0

Target:

```text
docs/concepts/019_cost_state_decision.md
docs/planning/architecture/002f_cost_state_personal_deployment_architecture_plan.md
backend/services/power_service.py
backend/api/routes/power.py
config/settings.py
```

Purpose:

Reconcile current runtime terms with accepted Cost State vocabulary before expanding power automation.

Required planning outcomes:

- accepted state enum
- current alias map: `awake` / `sleeping` to accepted states
- product-facing vs internal state names
- transition table updates
- content-free event vocabulary
- backward compatibility posture

Gate:

```text
cost_state_contract_gate
state_vocabulary_reconciliation_gate
regression_gate
```

---

## CCP-WP-002 — CostStateRecord contract

Priority: P0

Target:

```text
backend/services/power_service.py
backend/api/routes/power.py
future domain/schema/persistence layer
```

Purpose:

Define the central control-plane state record or equivalent API/service contract.

Required planning outcomes:

- fields for state, mode, wake, activity, idle, shutdown, failure, maintenance, and update timestamps
- no sensitive content fields
- storage decision: DynamoDB, DB, config-backed no-op, or hybrid
- API response shape
- transition validation rules
- test cases for state transitions

Gate:

```text
cost_state_contract_gate
content_free_operational_event_gate
privacy_boundary_gate
```

---

## CCP-WP-003 — BlockingJobRecord and job taxonomy

Priority: P0

Target:

```text
backend/services/workflow_job_service.py
backend/services/workflow_engine.py
backend/worker.py
future source/export/deletion/corpus/encryption workers
```

Purpose:

Generalize current workflow-run job tracking into a job registry capable of preventing unsafe shutdown.

Required planning outcomes:

- accepted blocking job type enum
- mapping from workflow runs to blocking jobs
- planned mapping for transcription, report/export, deletion/purge, encryption migration, and corpus recompute
- owner/artifact binding rules
- heartbeat field requirements
- timeout/cancel/resume/safe-shutdown behavior vocabulary

Gate:

```text
blocking_job_registry_gate
job_heartbeat_gate
job_safe_shutdown_gate
```

---

## CCP-WP-004 — Idle evaluator contract

Priority: P0

Target:

```text
backend/services/power_service.py
backend/api/routes/power.py
backend/services/workflow_job_service.py
frontend or future client heartbeat
```

Purpose:

Make the idle decision explicit and safe.

Required planning outcomes:

- authenticated activity signal definition
- heartbeat behavior
- idle timer start/reset rules
- idle pending state and grace period
- manual keep-awake interaction
- blocking job checks
- exact `should_sleep` semantics
- tests for active user, active job, idle user, and stale state

Gate:

```text
idle_evaluator_gate
keep_awake_bounds_gate
job_safe_shutdown_gate
```

---

## CCP-WP-005 — Shutdown coordinator and preflight plan

Priority: P0

Target:

```text
future control-plane service
AWS/ECS/RDS/VPC endpoint automation
backend/services/power_service.py
worker and queue services
```

Purpose:

Define how manual and automatic shutdown should decide whether it is safe to stop or scale down resources.

Required planning outcomes:

- shutdown request contract
- shutdown preflight result contract
- automatic idle shutdown flow
- manual sleep flow
- blocking job denial/delay behavior
- safe-cancel/checkpoint/resume behavior
- idempotency requirements
- failed-shutdown representation
- content-free event fields

Gate:

```text
job_safe_shutdown_gate
failed_wake_shutdown_gate
deployment_documentation_reconciliation_gate
```

---

## CCP-WP-006 — Wake, handoff, retry, and failure plan

Priority: P0

Target:

```text
backend/api/routes/power.py
backend/services/power_service.py
future Lambda/CodeBuild/ECS/RDS orchestration
login/wake surface
```

Purpose:

Define a minimal, secure, user-visible wake path.

Required planning outcomes:

- wake request contract
- owner login/manual wake trigger behavior
- handoff token lifetime and signing requirements
- handoff purpose and scope
- wake progress states
- retry wake behavior
- failed wake reason codes
- maintenance fallback
- no sensitive content exposure before auth/handoff

Gate:

```text
wake_path_security_gate
handoff_token_gate
failed_wake_shutdown_gate
```

---

## CCP-WP-007 — Queue and worker recovery integration

Priority: P0

Target:

```text
backend/worker.py
backend/services/workflow_job_service.py
backend/services/workflow_engine.py
backend/api/routes/queue.py
```

Purpose:

Ensure queued, running, stale, failed, cancelled, and resumed jobs interact safely with sleep/wake transitions.

Required planning outcomes:

- queue readiness signal
- worker health signal
- worker in-flight signal
- stale recovery behavior across wake/resume
- max attempts behavior
- API vs dedicated-worker ownership of resume
- queue route authentication/reconciliation posture
- no duplicate execution on wake/restart

Gate:

```text
queue_worker_recovery_gate
blocking_job_registry_gate
regression_gate
```

---

## CCP-WP-008 — Kill-mode product semantics plan

Priority: P0

Target:

```text
backend/services/workflow_job_service.py
config/settings.py
future UI/report/status surfaces
```

Purpose:

Clarify long-job kill behavior so cost protection does not corrupt analysis, reports, deletion, exports, or corpus state.

Required planning outcomes:

- job classes affected by kill mode
- whether kill mode cancels all jobs or only offending job class
- user-facing status language
- validation/report/corpus staleness behavior
- post-kill idle timer behavior
- regression tests

Gate:

```text
kill_mode_semantics_gate
analysis_state_integrity_gate
corpus_staleness_gate
```

---

## CCP-WP-009 — Content-free control-plane event plan

Priority: P0

Target:

```text
backend/core/logging_config.py
backend/core/log_sanitize.py
backend/core/audit.py
backend/services/power_service.py
backend/worker.py
future ControlPlaneEvent
```

Purpose:

Ensure power, queue, worker, idle, wake, sleep, failure, maintenance, and kill-mode events never store sensitive content.

Required planning outcomes:

- allowed event fields
- forbidden event fields
- reason-code vocabulary
- event retention posture
- tests for representative logs/events
- alignment with 003-D lifecycle/audit/redaction gates

Gate:

```text
content_free_operational_event_gate
log_redaction_gate
privacy_boundary_gate
```

---

## CCP-WP-010 — Deployment documentation reconciliation

Priority: P0

Target:

```text
docs/developer/aws-operations.md
README.md
docs/README.md
docs/planning/README.md
docs/planning/phases/README.md
.github/workflows historical references
```

Purpose:

Resolve conflicts between current cleared-workflow posture and older AWS operations guidance.

Required planning outcomes:

- identify GitHub Actions references that are stale/reference only
- define accepted manual sleep/wake documentation path
- distinguish current implemented power surfaces from desired control-plane target
- preserve historical notes without making them current authority
- update contributor/agent guidance when implementation starts

Gate:

```text
deployment_documentation_reconciliation_gate
GitHub_Actions_restoration_gate
release_readiness_gate
```

---

# P1 Work Packages

## CCP-WP-011 — Manual controls and owner-only operations plan

Priority: P1

Target:

```text
backend/api/routes/power.py
future UI
future auth/authorization layer
```

Purpose:

Define owner-only manual wake, sleep, keep-awake, retry wake, cancel job, enter maintenance, and clear maintenance controls.

Gate:

```text
manual_sleep_wake_gate
keep_awake_bounds_gate
privacy_boundary_gate
```

---

## CCP-WP-012 — Maintenance mode implementation plan

Priority: P1

Target:

```text
backend/services/power_service.py
backend/api/routes/power.py
future UI/status page
```

Purpose:

Represent intentional unavailability separately from failed wake, failed shutdown, or ordinary asleep state.

Gate:

```text
maintenance_mode_gate
content_free_operational_event_gate
```

---

## CCP-WP-013 — Public vs authenticated status policy

Priority: P1

Target:

```text
backend/api/routes/power.py
wake/status surface
frontend/status UI
```

Purpose:

Decide which power/status details can be public and which require owner authentication.

Gate:

```text
wake_path_security_gate
privacy_boundary_gate
metadata_sensitivity_gate
```

---

## CCP-WP-014 — Analysis/deletion/export/corpus state integrity plan

Priority: P1

Target:

```text
analysis workflow services
validation services
retention/deletion services
export services
corpus/graph services
```

Purpose:

Ensure shutdown, cancellation, retry, resume, and kill mode do not corrupt analysis scope, transcript version basis, validation state, deletion cascade state, export materialization, or corpus staleness.

Gate:

```text
analysis_state_integrity_gate
deletion_cascade_safety_gate
export_safety_gate
corpus_staleness_gate
```

---

## CCP-WP-015 — Cost-state API and DTO plan

Priority: P1

Target:

```text
backend/api/schemas.py
backend/api/routes/power.py
future /api/v1 control routes
```

Purpose:

Define user-facing and admin-facing DTOs for status, wake, sleep, keep-awake, blocking jobs, failures, and maintenance without exposing sensitive content.

Gate:

```text
cost_state_contract_gate
ui_language_gate
privacy_boundary_gate
```

---

## CCP-WP-016 — Control-plane observability plan

Priority: P1

Target:

```text
CloudWatch metrics/logs
backend/worker.py
backend/services/power_service.py
future dashboards
```

Purpose:

Define metrics and dashboards for queue depth, worker health, active jobs, idle status, wake duration, shutdown duration, failures, and kill-mode events.

Gate:

```text
content_free_operational_event_gate
release_readiness_gate
```

---

## CCP-WP-017 — GitHub Actions replacement/restoration plan

Priority: P1

Target:

```text
.github/workflows
infra/dev
scripts
release/deployment docs
```

Purpose:

Define whether and how GitHub Actions should return after the accepted control-plane model exists.

Gate:

```text
GitHub_Actions_restoration_gate
job_safe_shutdown_gate
privacy_boundary_gate
release_readiness_gate
```

---

# P2 Work Packages

## CCP-WP-018 — Scheduled wake windows

Priority: P2

Target:

```text
future control-plane policy
future UI settings
```

Purpose:

Consider scheduled availability windows for personal mode after manual and idle flows are safe.

Gate:

```text
future_availability_policy_gate
cost_state_contract_gate
```

---

## CCP-WP-019 — Enterprise AvailabilityPolicy

Priority: P2

Target:

```text
future enterprise policy layer
future workspace/org admin model
```

Purpose:

Defer always-on, scheduled uptime, autoscaling, SLO, and delegated admin controls to future enterprise posture.

Gate:

```text
future_enterprise_policy_gate
privacy_boundary_gate
release_readiness_gate
```

---

## CCP-WP-020 — Advanced autoscaling and SLO plan

Priority: P2

Target:

```text
future infrastructure
future monitoring/alerting
```

Purpose:

Plan enterprise-grade autoscaling, alerting, and availability objectives after personal-mode control plane is stable.

Gate:

```text
future_enterprise_policy_gate
release_readiness_gate
```

---

# Dependency Order

Recommended order for later implementation:

```text
CCP-WP-001
CCP-WP-002
CCP-WP-003
CCP-WP-004
CCP-WP-005
CCP-WP-006
CCP-WP-007
CCP-WP-008
CCP-WP-009
CCP-WP-010
CCP-WP-011 through CCP-WP-017
```

Do not restore GitHub Actions, add new power automation, or expand retained background work before CCP-WP-001 through CCP-WP-010 are planned and gated.

---

# Decision

These packages are ready to feed 003-G and the 003-H exit review.
