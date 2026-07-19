# 10 — v2.1 Cutover, Auth, and Graph Depth

## Phase Goal

Continue toward full v2 readiness after the [09 foundation slice](09_v2_0_foundation_execution.md).

Vision context: [05_v2_0_future_state_architecture.md](05_v2_0_future_state_architecture.md).

---

## Primary Outcomes

- React is the **deployed** primary UI (ALB cutover)
- Auth path moves beyond shared API key (implement [../auth_rbac_plan.md](../auth_rbac_plan.md) minimum viable Cognito or equivalent)
- Graph reasoning and case workflows deepen beyond MVP
- Remaining ops drills from data governance are executed and recorded

---

## Workstream A — React ALB cutover

- [ ] Push `frontend-react` image to ECR `rre-dev-web`
- [ ] Set `web_desired_count = 1` and apply Terraform
- [ ] ALB default → React; Streamlit under `/admin*` (or separate host)
- [ ] Deploy smoke: React ingest → report; Streamlit eval reachable
- [ ] Update [aws-deployment.md](../../developer/aws-deployment.md) topology as live

## Workstream B — Auth MVP

- [ ] Implement Cognito (or equivalent) for React product UI per auth plan
- [ ] Attach `subject_id` / ownership checks on case & transcript reads
- [ ] Keep break-glass API key for admin/worker if needed
- [ ] Document migration from shared-key UAT

## Workstream C — Graph and case depth

- [ ] Contradiction / divergence surfacing in React graph + report
- [ ] Evidence-weighted or longitudinal construct tracking (incremental)
- [ ] Case-level report package export
- [ ] Split-turn in prepare _(from deferred prep UX)_

## Workstream D — Platform drills

- [ ] Execute RDS snapshot restore drill; record results in ops notes
- [ ] Confirm secret rotation procedure once in a dry run
- [ ] Optional: S3 + CloudFront design spike for React static hosting

## Workstream E — Worker UX maturity

- [ ] Module-level status in React Analyze
- [ ] Cancel / attempt visibility polish
- [ ] Partial module rerun if cheap on existing job control

---

## Exit Criteria

v2.1 is complete when React owns the live ALB primary journey, a real auth path exists for external UAT, graph/case depth is visibly stronger than the v1.4/v2.0-foundation MVP, and ops cutover/drills are no longer paper-only.
