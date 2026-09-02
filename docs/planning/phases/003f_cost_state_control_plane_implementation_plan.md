# 003-F — Cost-State Control Plane Implementation Plan

## Status

Complete.

This subgroup converts accepted cost-state architecture into implementation-ready control-plane plans.

It does not implement code, schema migrations, DynamoDB changes, Lambda/CodeBuild changes, ECS/RDS/VPC endpoint automation, GitHub Actions, auth changes, worker changes, queue changes, UI changes, monitoring changes, alerting changes, deployment changes, or production data migrations.

---

# Purpose

003-F prepares cost-state and personal deployment work so later implementation can make low-cost sleep/wake behavior safe, visible, and compatible with retained transcript analysis.

It answers:

- Which cost-state/control-plane foundations already exist in the prototype?
- How should accepted cost-state vocabulary reconcile with current power-service terms?
- What should `CostStateRecord` or equivalent represent?
- How should blocking jobs be generalized beyond workflow runs?
- How should idle evaluation combine authenticated activity and job activity?
- How should wake, handoff, retry, failed wake, manual sleep, and maintenance work?
- How should shutdown preflight prevent corruption of analysis, deletion, export, and corpus state?
- How should GitHub Actions remain blocked until replacement/restoration is gated?
- How should future enterprise availability remain a policy layer?

---

# Outputs

| Output | Document |
|---|---|
| Cost-state control-plane implementation plan | `../architecture/003f_cost_state_control_plane_implementation_plan.md` |
| Cost-state control surface matrix | `../inventories/003f_cost_state_control_surface_matrix.md` |
| Cost-state control-plane work packages | `../inventories/003f_cost_state_work_packages.md` |
| Job-safe shutdown gate checklist | `../inventories/003f_job_safe_shutdown_gate_checklist.md` |

---

# Implementation Reference Reviewed

003-F reviewed the accepted Phase 002 cost-state architecture, prior Phase 003 foundation plans, and current implementation references including:

```text
docs/concepts/019_cost_state_decision.md
docs/planning/architecture/002f_cost_state_personal_deployment_architecture_plan.md
docs/planning/inventories/002f_cost_state_transition_matrix.md
docs/planning/inventories/002f_personal_deployment_control_requirements.md
docs/planning/architecture/003c_data_lifecycle_retention_foundation_implementation_plan.md
docs/planning/architecture/003d_privacy_boundary_encryption_baseline_implementation_plan.md
docs/planning/architecture/003e_analysis_boundary_validation_implementation_plan.md
config/settings.py
backend/services/power_service.py
backend/api/routes/power.py
backend/services/workflow_job_service.py
backend/worker.py
backend/services/workflow_engine.py
backend/main.py
backend/api/routes/queue.py
docs/developer/aws-operations.md
```

---

# Current Baseline Findings

The prototype already has useful cost-state foundations:

- settings for power control, power state table, handoff secret, idle sleep window, worker mode, worker polling, job timeout, stale recovery, max attempts, and kill mode
- DynamoDB-backed `PowerStateStore` with local no-op behavior when disabled
- power status, admin idle status, authenticated heartbeat, handoff, and start-idle-timer routes under `/api/v1/ops/power`
- signed time-limited handoff tokens
- idle status that considers active jobs and idle duration
- worker health reporting in-flight counts and active run IDs
- workflow job service for background execution, dedicated worker queueing, in-flight tracking, queue stats, stale recovery, kill mode, resume, cancellation, and retry
- API/worker startup behavior that resumes incomplete jobs in different deployment modes
- AWS operations documentation describing the dev sleep/wake concept and residual cost posture

The prototype is not yet sufficient for the accepted cost-state model because accepted state vocabulary is not fully reconciled with current `awake`/`sleeping` terms, blocking jobs are workflow-centric rather than generalized, shutdown coordination is not first-class, manual keep-awake and maintenance are not mature, queue routes need privacy/auth reconciliation, kill-mode semantics are coarse, and older GitHub Actions/manual-pause guidance conflicts with the current cleared-workflow posture.

---

# Accepted Decisions

## 1. Cost State is a control-plane contract

Cost State should be represented as a product-aware control-plane contract, not as hidden infrastructure trivia or analysis state.

## 2. State vocabulary must be reconciled before automation expands

Current terms such as `awake` and `sleeping` may remain temporarily as aliases, but product/control-plane planning should converge on accepted state names.

## 3. CostStateRecord should centralize availability posture

A central state record or equivalent should represent wake, activity, idle, shutdown, failure, maintenance, and update metadata without sensitive content.

## 4. Blocking jobs must generalize beyond workflow runs

Workflow runs are the current foundation, but the mature model must cover transcription, transcript preparation, reflection runs, reports, exports, deletion cascades, purge workers, encryption migrations, and corpus recompute jobs.

## 5. Idle shutdown requires both no user activity and no blocking jobs

Frontend quietness is not enough to sleep. Server-side authenticated activity and blocking job activity must both be evaluated.

## 6. Shutdown must be preflighted and idempotent

Manual and automatic shutdown should delay, deny, cancel safely, checkpoint, resume, or fail cleanly based on job policy.

## 7. Wake and handoff must be secure and visible

Wake should remain owner-initiated or explicitly scheduled, handoff tokens must be signed and short-lived, and failed wake should be visible/actionable.

## 8. GitHub Actions remain blocked until replaced or restored through gates

Older operations docs referencing GitHub Actions manual sleep are reference/stale for Phase 003 purposes. Future restoration must pass cost-state, privacy, job-safety, and release-readiness gates.

## 9. Enterprise availability remains future policy

Always-on, scheduled, autoscaled, monitored, delegated enterprise availability should be a future policy layer over stable core concepts.

---

# Work Package Summary

003-F defines work packages for:

```text
CCP-WP-001 — Cost-state authority and vocabulary reconciliation
CCP-WP-002 — CostStateRecord contract
CCP-WP-003 — BlockingJobRecord and job taxonomy
CCP-WP-004 — Idle evaluator contract
CCP-WP-005 — Shutdown coordinator and preflight plan
CCP-WP-006 — Wake, handoff, retry, and failure plan
CCP-WP-007 — Queue and worker recovery integration
CCP-WP-008 — Kill-mode product semantics plan
CCP-WP-009 — Content-free control-plane event plan
CCP-WP-010 — Deployment documentation reconciliation
CCP-WP-011 — Manual controls and owner-only operations plan
CCP-WP-012 — Maintenance mode implementation plan
CCP-WP-013 — Public vs authenticated status policy
CCP-WP-014 — Analysis/deletion/export/corpus state integrity plan
CCP-WP-015 — Cost-state API and DTO plan
CCP-WP-016 — Control-plane observability plan
CCP-WP-017 — GitHub Actions replacement/restoration plan
```

P2 decisions remain for scheduled wake windows, enterprise `AvailabilityPolicy`, and advanced autoscaling/SLO planning.

---

# Gates Carried Forward

003-F carries forward these gates:

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

003-G should prepare UI/report implementation planning for showing cost-state status and controls without making low-cost operation look like product failure and without implying that operational state changes analysis/report meaning.

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
- deployment changes
- production data migration

---

# Exit Criteria

003-F is complete when:

- cost-state control-plane implementation plan exists
- cost-state control surface matrix exists
- cost-state work packages exist
- job-safe shutdown gate checklist exists
- current implementation references are reviewed at planning level
- 003-G and 003-H handoffs are explicit
- Phase 003 indexes are updated
- broad implementation remains blocked

All criteria are satisfied.

---

# Next Phase

Proceed to:

```text
003-G — UI/Report Alignment Implementation Plan
```
