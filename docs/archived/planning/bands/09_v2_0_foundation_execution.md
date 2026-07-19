# v2.0 Foundation Execution Band

Companion to [../../../planning/v2_future_state_architecture.md](../../../planning/v2_future_state_architecture.md).
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
- [ ] Ops: push web image, set `web_desired_count=1`, flip ALB default _(deferred — see [deferred_backlog.md](../../../planning/deferred_backlog.md) post-RC / GA; superseded band [10](10_v2_1_cutover_auth_and_graph_depth_superseded.md))_

## Exit for this band

Foundation complete when gates CI exists, safety events are auditable, report packages are
server-built, findings are on `/api/v1`, and React surfaces safety + evals. Full v2 vision
(Cognito/SSO, S3+CloudFront, deep graph contradiction UX) remains deferred — see [deferred_backlog.md](../../../planning/deferred_backlog.md). Near-term auth is email OTP ([phases/003](../../../planning/phases/003_v2_1_simple_email_auth_and_ownership.md)).

**Status:** Foundation band complete (ops ALB cutover still manual).
