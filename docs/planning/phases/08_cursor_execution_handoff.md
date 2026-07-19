# 08 — Cursor execution handoff

## Goal

Execute the v1.1 → v2.0 roadmap in `docs/planning/phases/` without inventing a parallel doc tree.

---

## Step 1 — Inspect repository

Review `docs/planning/`, `docs/`, `backend/`, `ui/`, `config/`, `tests/`, `infra/`, `.github/workflows/`.

Mark recommendations as already shipped (v1.0), partial, or missing.

---

## Step 2 — Planning docs (canonical)

| Role | Path |
|------|------|
| Active roadmap | `docs/planning/phases/` |
| Deferred (priority) | `docs/planning/deferred_backlog.md` |
| General (no priority) | `docs/planning/general_backlog.md` |
| Completed history | `docs/archived/planning/` |
| AWS architecture | `docs/developer/aws-deployment.md` |

Do **not** recreate `implementing.md`, `future_considerations.md`, or root-level `roadmap_v1_*.md` duplicates.

Reclassify uncovered items into deferred vs general; do not delete.

---

## Step 3 — Checklists

Use the checkboxes already in each phase file. When implementing, tick tasks and note PR / commit.

---

## Step 4 — Preserve uncovered items

Anything not covered by v1.1–v2.0 stays in:

- [../deferred_backlog.md](../deferred_backlog.md) — still want it when unblocked
- [../general_backlog.md](../general_backlog.md) — no schedule

---

## Step 5 — Prioritize v1.1 first

Do not start React until v1.1 is largely done and v1.2 API/eval prerequisites are underway.

v1.1 start order:

1. Test invocation + repo hygiene  
2. Docs truth (API/UI/worker)  
3. Selective deploy  
4. Service-specific IAM  
5. Worker queue/backpressure  
6. Streamlit/API boundary  
7. Observability / smoke  

---

## Step 6 — React rule

React must not import backend services or touch DB/AWS directly. Clients talk HTTP to the API (eventually `/api/v1`). Stabilize contracts in v1.2 before React screens in v1.3.

---

## Step 7 — Testing requirements

Prefer: unit, integration, golden, safety fixtures, API contract tests, deploy smoke; Playwright once React exists.

Canonical local/CI command:

```text
python -m pytest tests/ -q
```

(Bare `pytest` works only when the venv `Scripts`/`bin` directory is on `PATH`.)

---

## Step 8 — Avoid scope creep

```text
reliability → evaluation → safety → API stability → React MVP → case depth → platform maturity
```

No new analysis modules unless required to exercise the platform.

---

## Step 9 — Suggested first PRs

| PR | Scope |
|----|--------|
| 1 | Planning alignment (this folder + backlog tags + aws-deployment paths) |
| 2 | Test/repo hygiene (`python -m pytest`, cache guards, prompt source archives out of runtime) |
| 3 | Selective deploy (`component=all\|api\|ui\|worker`) + worker in wait/smoke |
| 4 | Service-specific IAM design/implementation |
| 5 | Evaluation harness scaffold (v1.2) |

---

## Done definition for roadmap integration

- `phases/` is the obvious active plan  
- deferred/general backlogs hold the rest  
- v1.1 is the current implementation focus  
- React is staged, not immediate  
- AWS docs mention API + UI + worker  
