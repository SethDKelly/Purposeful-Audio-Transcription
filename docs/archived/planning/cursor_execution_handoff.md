# 08 — Cursor execution handoff

> **Archived** one-time handoff (pre-numeric). Active plan: [../../planning/phases/001_v2_1_phase_sequence_overview.md](../../planning/phases/001_v2_1_phase_sequence_overview.md) (`001`–`009`).

## Goal

Execute the active band in `docs/planning/phases/` without inventing a parallel doc tree.

**Current band:** [../../planning/phases/001_v2_1_phase_sequence_overview.md](../../planning/phases/001_v2_1_phase_sequence_overview.md)  
**Archive:** Phases **1–54** in [phases.md](phases.md)

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
| Completed history | `docs/archived/planning/phases.md` + `bands/` |
| AWS architecture | `docs/developer/aws-deployment.md` |

Do **not** recreate `implementing.md`, `future_considerations.md`, or root-level `roadmap_v1_*.md` duplicates.

Reclassify uncovered items into deferred vs general; do not delete.

When a band ships: append the next Phase number to `archived/planning/phases.md`, **move** the detail checklist into `archived/planning/bands/`, update `executive_roadmap.md`, and retarget `deferred_backlog` / `phases/README` so only unfinished work stays under `planning/phases/`.

---

## Step 3 — Checklists

Use the checkboxes already in each phase file. When implementing, tick tasks and note PR / commit.

---

## Step 4 — Preserve uncovered items

Anything not covered by the active band stays in:

- [../../planning/deferred_backlog.md](../../planning/deferred_backlog.md) — still want it when unblocked
- [../../planning/general_backlog.md](../../planning/general_backlog.md) — no schedule

---

## Step 5 — Prioritize the active band

v1.1–v1.4 and v2.0 foundation are **complete**. Do not reopen them unless fixing regressions.

v2.1 start order (superseded — see numeric `001`–`009`):

1. Core tenets / governance (**002**)  
2. Auth MVP — **email OTP** per [../../planning/auth_rbac_plan.md](../../planning/auth_rbac_plan.md) / ADR 001 (**003**)  
3. Evidence precision + snapshots (**004**–**005**)  
4. Worker atomicity / safety / graph (**006**–**008**)  
5. React API contract + RC (**009**); ALB cutover deferred to GA  

---

## Step 6 — React rule

React must not import backend services or touch DB/AWS directly. Clients talk HTTP to `/api/v1`. Streamlit remains admin/eval only ([../../planning/streamlit_role_decision.md](../../planning/streamlit_role_decision.md)).

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
| 1 | Tenet governance wiring (**002** leftovers) |
| 2 | Email OTP auth + ownership (**003**) |
| 3 | Evidence precision (**004**) |
| 4 | Evidence snapshots (**005**) |
| 5 | Atomic worker claim (**006**) |

---

## Done definition for roadmap integration

- `phases/` is the obvious active plan (`10` current)  
- deferred/general backlogs hold the rest  
- archive phase numbers match shipped bands (next write: **55**)  
- React is primary product path; Streamlit admin/eval  
- AWS docs mention API + UI + worker (+ web when cut over)  
