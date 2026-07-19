# v2.0 Foundation Execution Band

Companion to [05_v2_0_future_state_architecture.md](05_v2_0_future_state_architecture.md).
This band ships the first **readiness slice** toward v2 — not the full future-state vision.

## Goal

Close the highest-leverage gaps vs v2 readiness criteria: safety governance UX + audit,
eval release gates, professional report packages, queryable findings on `/api/v1`, and
deploy cutover scaffolding.

## Workstreams

### A — Safety governance

- [x] React Analyze: safety assessment + safety-mode toggle
- [x] React Report: safety-mode / safety_flags framing
- [x] Persist `SafetyEvent` (scan / safety_mode_enabled)
- [x] `GET /api/v1/transcripts/{id}/safety-assessment`
- [x] `GET /api/v1/.../safety-events`

### B — Evaluation release gates

- [x] CI workflow `.github/workflows/eval-release-gates.yml` (OpenAPI + golden offline + safety)
- [x] `EvaluationRun` persistence + list/get/create API
- [x] React Evaluations page

### C — Professional reporting

- [x] Server ZIP report package (`POST /api/v1/exports` format=`package`)
- [x] Manifest includes confidence legend + version/prompt hashes
- [x] React downloads ZIP package

### D — Queryable findings / cases

- [x] `GET /api/v1/workflow-runs/{id}/findings` (+ drilldown)
- [x] Case pinned findings API + React list
- [x] Longitudinal/compare already on v1 (from v1.4)

### E — Deployment direction

- [x] Document React-primary cutover (Streamlit `/admin`)
- [x] `rre-dev-web` ECS/ECR already provisioned (`web_desired_count` default 0)
- [ ] Ops: push web image, set `web_desired_count=1`, flip ALB default (manual)

## Exit for this band

Foundation complete when gates CI exists, safety events are auditable, report packages are
server-built, findings are on `/api/v1`, and React surfaces safety + evals. Full v2 vision
(Cognito, S3+CloudFront, deep graph reasoning) remains future work.

**Status:** Foundation band complete (ops ALB cutover still manual).
