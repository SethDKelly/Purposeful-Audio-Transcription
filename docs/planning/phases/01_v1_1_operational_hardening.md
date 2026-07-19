# 01 — v1.1 Operational Hardening Plan

## Phase Goal

Make the current application reliable, clean, secure at service boundaries, and easier to deploy.

This phase addresses shortfalls in the current v1 application before expanding product scope.

---

# Primary Outcomes

By the end of v1.1:

- tests run consistently in local and CI environments
- repo artifacts are cleaned up
- deployment docs reflect the actual API/UI/worker architecture
- UI/API/worker services have clear boundaries
- ECS deploys can target individual components
- worker queues have operational guardrails
- service-specific health checks and smoke tests exist
- IAM permissions begin moving toward least privilege

---

# Workstream A — Test Invocation and Repo Hygiene

## Problems

- Plain `pytest` may fail due to import path/package setup.
- Some test execution paths depend on `python -m pytest`.
- The repo/archive may include `__pycache__` and `.pyc` files.
- Runtime config may contain archived source materials such as prompt zip/session notes.

## Implementation Tasks

- [x] Fix test imports so both `pytest` and `python -m pytest` work.
- [x] Add `tests/__init__.py` if needed.
- [x] Standardize CI test command.
- [x] Ensure GitHub Actions uses the same invocation as local dev docs.
- [x] Remove `__pycache__`, `.pyc`, and generated artifacts from the repo.
- [x] Strengthen `.gitignore`.
- [x] Move non-runtime prompt source archives out of `config/prompts/`.
- [x] Add a CI check that fails if `.pyc` or `__pycache__` files are committed.

## Acceptance Criteria

- `pytest tests/ -q` works.
- `python -m pytest tests/ -q` works.
- CI test command is documented.
- Repo contains no committed Python cache artifacts.
- Runtime config folders only contain runtime config.

---

# Workstream B — Update stale planning and deployment docs

## Implementation Tasks

- [x] Update `docs/developer/aws-deployment.md` (not under `planning/`).
- [x] Document current API / UI / **worker** service topology.
- [x] Document current ECS service names (`rre-dev-api`, `rre-dev-ui`, `rre-dev-worker`).
- [x] Document ALB routing and health checks.
- [x] Document worker deployment and smoke-test behavior.
- [x] Update stale version / deploy-policy references (tag or manual; not every `main` push).
- [x] Keep active roadmap in `docs/planning/phases/` (do not revive `implementing.md`).
- [x] Triage leftovers into `deferred_backlog.md` / `general_backlog.md` per [07](07_backlog_triage_and_docs_update_plan.md).

## Acceptance Criteria

- Docs match actual deployed architecture.
- No planning doc implies an obsolete single-container deployment.
- Worker is represented in deployment diagrams and operational notes.
- Active roadmap points to v1.1–v2 plans under `phases/`.

---

# Workstream C — Selective Component Deployment

## Problem

Even with separate containers, deployment may still behave like an all-or-nothing release.

## Implementation Tasks

- [x] Add a deploy parameter: `component = all | api | ui | worker`.
- [x] Use separate image tags for API/backend and UI.
- [x] Let worker reuse the API/backend image with a different command.
- [x] Add path-based deploy logic if appropriate. _(Declined: tags + `workflow_dispatch` only; path filters conflict with pause/cost policy.)_
- [x] Include worker in deployment wait and health checks.
- [x] Add service-specific smoke tests.

## Acceptance Criteria

- UI-only changes can deploy without rebuilding API image.
- API-only changes can deploy without rebuilding UI image.
- Worker deployment is explicitly handled.
- Rollback path is documented per service.

---

# Workstream D — Service-Specific IAM Hardening

## Target IAM Model

| Service | Permissions |
|---|---|
| UI | minimal; no Bedrock, no Transcribe, no S3 audio access, preferably no DB secret |
| API | DB, job creation, limited S3/Transcribe if needed |
| Worker | DB, Bedrock, Transcribe, S3, workflow execution |
| Execution Role | image pull, logs, required secrets only |

## Implementation Tasks

- [x] Create separate task roles for UI, API, and worker.
- [x] Remove Bedrock/Transcribe access from UI.
- [x] Restrict secret access per service.
- [x] Document IAM boundaries.
- [x] Add Terraform comments explaining permission boundaries.
- [x] Validate that UI cannot access backend-only secrets.

## Acceptance Criteria

- UI task role has no analysis-provider permissions.
- Worker role has only required job execution permissions.
- API role does not have broader permissions than needed.
- IAM design is documented.

---

# Workstream E — Worker Queue Operations

## Implementation Tasks

- [x] Add max jobs claimed per polling cycle.
- [x] Add max in-flight jobs per worker.
- [ ] Add queue depth metrics.
- [ ] Add oldest queued job age metric.
- [ ] Add stale job recovery.
- [x] Add retry exhaustion state.
- [ ] Add failed-job review endpoint or admin view.
- [ ] Add worker health endpoint.
- [ ] Add CloudWatch alarms for queue age, failure rate, and worker health.
- [ ] Add rate-limit-aware throttling for model/provider calls.

## Acceptance Criteria

- Worker cannot claim unlimited jobs.
- Failed and stale jobs are visible.
- Retries are bounded.
- Queue depth and job age can be monitored.
- Worker health is included in deployment smoke checks.

---

# Workstream F — Streamlit/API Boundary Cleanup

## Goal

Prepare for React by making Streamlit behave like an external API client.

## Implementation Tasks

- [ ] Audit Streamlit imports.
- [ ] Remove direct imports from `backend.services`, `backend.repositories`, `backend.db`, and workflow internals where feasible.
- [ ] Create or strengthen a UI API client layer.
- [ ] Ensure Streamlit uses `BACKEND_API_URL`.
- [ ] Ensure UI does not need DB credentials.
- [ ] Ensure UI does not directly call Bedrock/Transcribe.
- [ ] Document UI/API boundary.

## Acceptance Criteria

- Streamlit can run as a separate client against the deployed API.
- UI code calls backend through API endpoints.
- No direct analysis execution from UI process.
- This work sets up React readiness.

---

# Workstream G — Service Observability

## Implementation Tasks

- [ ] Add request IDs to logs across API and worker.
- [ ] Include workflow/job IDs in logs.
- [ ] Add structured logging fields.
- [ ] Add service-level dashboards for API, worker, provider calls, DB, and UI.
- [ ] Add smoke test scripts for API, UI, and worker.

## Acceptance Criteria

- A failing workflow can be traced through API → job → worker → module runs.
- Logs include request/job IDs.
- Basic service health is visible without digging into raw logs.

---

# v1.1 Exit Criteria

v1.1 is complete when tests and CI are stable, repo hygiene issues are cleaned up, deployment docs are current, selective deployment works or is substantially implemented, worker queue has basic guardrails, service IAM boundaries are documented and partially enforced, Streamlit is substantially API-client oriented, and observability is sufficient for debugging full-suite jobs.
