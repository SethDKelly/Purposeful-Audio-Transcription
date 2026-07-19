# 08 — Cursor execution handoff

## Goal

Execute the active band in `docs/planning/phases/` without inventing a parallel doc tree.

**Current band:** [10_v2_1_cutover_auth_and_graph_depth.md](10_v2_1_cutover_auth_and_graph_depth.md)  
**Archive:** Phases **1–54** in [../../archived/planning/phases.md](../../archived/planning/phases.md)

---

## Step 1 — Inspect repository

Review `docs/planning/`, `docs/`, `backend/`, `frontend-react/`, `ui/`, `config/`, `tests/`, `infra/`, `.github/workflows/`.

Mark recommendations as already shipped, partial, or missing.

---

## Step 2 — Planning docs (canonical)

| Role | Path |
|------|------|
| Active roadmap | `docs/planning/phases/` (start at `10`) |
| Deferred (priority) | `docs/planning/deferred_backlog.md` |
| General (no priority) | `docs/planning/general_backlog.md` |
| Completed history | `docs/archived/planning/` |
| AWS architecture | `docs/developer/aws-deployment.md` |

Do **not** recreate `implementing.md`, `future_considerations.md`, or root-level `roadmap_v1_*.md` duplicates.

Reclassify uncovered items into deferred vs general; do not delete.

When a band ships: append the next Phase number to `archived/planning/phases.md`, update `executive_roadmap.md`, retarget `deferred_backlog` / `README` pointers.

---

## Step 3 — Checklists

Use the checkboxes already in each phase file. When implementing, tick tasks and note PR / commit.

---

## Step 4 — Preserve uncovered items

Anything not covered by the active band stays in:

- [../deferred_backlog.md](../deferred_backlog.md) — still want it when unblocked
- [../general_backlog.md](../general_backlog.md) — no schedule

---

## Step 5 — Prioritize the active band

v1.1–v1.4 and v2.0 foundation are **complete**. Do not reopen them unless fixing regressions.

v2.1 start order:

1. React ALB cutover (`rre-dev-web`)  
2. Auth MVP (Cognito) per [../auth_rbac_plan.md](../auth_rbac_plan.md)  
3. Graph/case depth (contradiction, case package, split-turn)  
4. Ops drills (RDS restore, secret rotation)  
5. Worker/module status UX  

---

## Step 6 — React rule

React must not import backend services or touch DB/AWS directly. Clients talk HTTP to `/api/v1`. Streamlit remains admin/eval only ([../streamlit_role_decision.md](../streamlit_role_decision.md)).

---

## Step 7 — Testing requirements

Prefer: unit, integration, golden, safety fixtures, API contract tests, eval release gates, deploy smoke, Playwright.

Canonical local/CI command:

```text
python -m pytest tests/ -q
```

Eval gates: `.github/workflows/eval-release-gates.yml`.

---

## Step 8 — Avoid scope creep

```text
cutover → auth → graph/case depth → ops drills → full v2 platform
```

No new analysis modules unless required to exercise the platform.

---

## Step 9 — Suggested next PRs

| PR | Scope |
|----|--------|
| 1 | ALB/web cutover Terraform + deploy docs |
| 2 | Cognito / JWT auth MVP |
| 3 | Graph contradiction + case package export |
| 4 | Split-turn prepare UX |
| 5 | Documented RDS restore / secret-rotation drill results |

---

## Done definition for roadmap integration

- `phases/` is the obvious active plan (`10` current)  
- deferred/general backlogs hold the rest  
- archive phase numbers match shipped bands (next write: **55**)  
- React is primary product path; Streamlit admin/eval  
- AWS docs mention API + UI + worker (+ web when cut over)  
