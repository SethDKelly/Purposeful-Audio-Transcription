# 009 — React API Contract and Release-Candidate Readiness

## Phase Goal

Stabilize the React/API contract and define release-candidate criteria for v2.

This phase comes after the core correctness and trust work because React should rely on stable APIs.

---

# Part 1 — OpenAPI-Generated React Client

## Problem

Hand-written React API types can drift from backend schemas.

## Target

Generate or contract-check React types from FastAPI OpenAPI.

## Tasks

- [ ] Generate OpenAPI schema in CI (extend existing `scripts/export_openapi.py` if needed).
- [x] OpenAPI path snapshot exists (`tests/snapshots/openapi_v1_paths.json` — Phase 51); keep green and extend if `/api/v1` auth/evidence paths change.
- [ ] Generate TypeScript client or schema types.
- [ ] Replace hand-written API response types where feasible.
- [ ] Add CI check for client/schema drift (beyond path-list snapshot).
- [ ] Document API breaking-change policy.

## Acceptance Criteria

- React types match backend schemas.
- API contract changes are visible in CI.
- React uses generated or schema-checked client.

---

# Part 2 — Product API Stability

## Recommended Stable Endpoints

```text
POST   /api/v1/transcripts
GET    /api/v1/transcripts/{id}
PATCH  /api/v1/transcripts/{id}/turns
GET    /api/v1/workflows
POST   /api/v1/workflow-runs
GET    /api/v1/workflow-runs/{id}/status
GET    /api/v1/reports/{id}
GET    /api/v1/reports/{id}/findings
GET    /api/v1/reports/{id}/evidence
POST   /api/v1/findings/{id}/feedback
GET    /api/v1/cases/{id}
GET    /api/v1/cases/{id}/timeline
POST   /api/v1/exports
```

Tasks:

- [ ] Ensure endpoint response shapes are stable.
- [ ] Add error response standard.
- [ ] Include request IDs in errors.
- [ ] Hide raw LLM output from product-facing APIs.
- [ ] Keep raw output behind admin/debug access.

---

# Part 3 — v2 Release-Candidate Gate

The app can be called v2 release candidate when the following pass:

## Auth

- [ ] Email login works.
- [ ] Ownership checks pass.
- [ ] No public shared API key required for normal users.

## Evidence

- [ ] Evidence snippets are concise.
- [ ] Evidence quote IDs are valid.
- [ ] Old reports remain valid after transcript edits.
- [ ] Reports are bound to transcript/evidence versions.

## Worker

- [ ] Atomic job claiming passes concurrency tests.
- [ ] Duplicate job execution is prevented.
- [ ] Worker health/queue metrics exist.

## Safety

- [ ] Safety policy is config-driven.
- [ ] Safety red-team fixtures pass.
- [ ] Definitive diagnostic/adjudicative claims are blocked.
- [ ] Serious safety concerns are not mutualized.

## Graph/Case

- [ ] Graph edges have confidence/rationale/evidence where possible.
- [ ] Case evidence is transcript/version-specific.
- [ ] Longitudinal claims cite multiple sessions when claiming recurrence.

## React/API

- [ ] React uses generated or contract-checked API client.
- [ ] OpenAPI drift is detected.
- [ ] React primary flow passes E2E test.

## Evaluation

- [ ] Golden fixture evals pass.
- [ ] Safety fixture evals pass.
- [ ] Evidence precision evals pass.
- [ ] Forbidden-claim evals pass.
- [ ] Tenet compliance report is generated.

---

# v2 GA Gate

Do not call the app v2 GA until:

- external UAT feedback is incorporated
- privacy/security posture is documented
- backup/restore is tested
- data deletion/export flows are verified
- React primary UI cutover is complete or Streamlit is admin-only
- operational monitoring is credible
- critical safety/evidence bugs are resolved.
