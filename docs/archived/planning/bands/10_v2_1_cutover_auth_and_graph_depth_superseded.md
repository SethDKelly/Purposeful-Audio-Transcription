# 10 — v2.1 Cutover, Auth, and Graph Depth (superseded)

> **Superseded.** Canonical active plan is the numeric sequence [001](../../../planning/phases/001_v2_1_phase_sequence_overview.md)–[009](../../../planning/phases/009_v2_1_react_api_contract_and_release_candidate_readiness.md).  
> Auth MVP is **email OTP** ([ADR 001](../../../developer/architecture_decisions/adr_001_simple_email_auth_before_enterprise_sso.md)), not Cognito.  
> Leftover workstreams (ALB cutover, Cognito/SSO, contradiction UX, case package, split-turn, ops drills, worker UX) live in [../../../planning/deferred_backlog.md](../../../planning/deferred_backlog.md) under “Deferred from superseded band 10”.

## Original phase goal (historical)

Continue toward full v2 readiness after the [09 foundation slice](09_v2_0_foundation_execution.md) (Phase **54**).

Vision context: [../../../planning/v2_future_state_architecture.md](../../../planning/v2_future_state_architecture.md).

---

## Primary Outcomes (original)

- React is the **deployed** primary UI (ALB cutover)
- Auth path moves beyond shared API key (Cognito-first — **superseded by email OTP**)
- Graph reasoning and case workflows deepen beyond MVP
- Remaining ops drills from data governance are executed and recorded

---

## Workstream A — React ALB cutover → deferred (v2 GA)

- [ ] Push `frontend-react` image to ECR `rre-dev-web`
- [ ] Set `web_desired_count = 1` and apply Terraform
- [ ] ALB default → React; Streamlit under `/admin*` (or separate host)
- [ ] Deploy smoke: React ingest → report; Streamlit eval reachable
- [ ] Update [aws-deployment.md](../../../developer/aws-deployment.md) topology as live

## Workstream B — Auth MVP → replaced by [phases/003](../../../planning/phases/003_v2_1_simple_email_auth_and_ownership.md)

- [ ] ~~Implement Cognito~~ → email OTP + session cookie (ADR 001)
- [ ] Ownership checks → `owner_user_id` (not `subject_id`)
- [ ] Keep break-glass API key for admin/worker if needed
- [ ] Document migration from shared-key UAT

## Workstream C — Graph and case depth → partial in 008; rest deferred

- [ ] Contradiction / divergence surfacing → deferred after **008**
- [ ] Evidence-weighted / longitudinal construct tracking → incremental in **008** + deferred
- [ ] Case-level report package export → deferred
- [ ] Split-turn in prepare → deferred

## Workstream D — Platform drills → deferred (v2 GA)

- [ ] Execute RDS snapshot restore drill; record results in ops notes
- [ ] Confirm secret rotation procedure once in a dry run
- [ ] Optional: S3 + CloudFront design spike for React static hosting

## Workstream E — Worker UX maturity → deferred after **006**

- [ ] Module-level status in React Analyze
- [ ] Cancel / attempt visibility polish
- [ ] Partial module rerun if cheap on existing job control

---

## Exit Criteria (original — superseded)

v2.1 completion is now defined by [001 global exit criteria](../../../planning/phases/001_v2_1_phase_sequence_overview.md) and [009 RC/GA gates](../../../planning/phases/009_v2_1_react_api_contract_and_release_candidate_readiness.md).
