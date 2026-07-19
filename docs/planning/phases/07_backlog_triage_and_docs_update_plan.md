# 07 — Backlog triage and docs update

## Purpose

Keep planning coherent: active work lives in `docs/planning/phases/`; nothing useful is lost from older backlogs.

---

## Rule

Do **not** delete backlog items unless they are obsolete **and** already completed.

Instead:

- assign covered items to a phase file (checkbox / workstream)
- leave unscheduled-but-valuable items in [../deferred_backlog.md](../deferred_backlog.md)
- leave unprioritized ideas in [../general_backlog.md](../general_backlog.md)
- mark rows `Completed`, `Superseded`, `Scheduled (vN.x)`, or `No longer planned`
- preserve rationale where possible
- when a band ships: append **Phase N** to [../../archived/planning/phases.md](../../archived/planning/phases.md) and refresh [../../archived/planning/executive_roadmap.md](../../archived/planning/executive_roadmap.md)

---

## Canonical planning layout (current)

```text
docs/
  planning/
    README.md
    deferred_backlog.md          # prioritized, not yet / not fully done
    general_backlog.md           # no priority
    auth_rbac_plan.md
    streamlit_role_decision.md
    react_frontend_plan.md
    phases/                      # ACTIVE ROADMAP
      00_unified_roadmap_overview.md
      01 … 04                    # completed bands (v1.1–v1.4)
      05_v2_0_future_state_architecture.md
      09_v2_0_foundation_execution.md   # complete
      10_v2_1_cutover_auth_and_graph_depth.md  # ACTIVE
      06_react_transition_plan.md
      07_backlog_triage_and_docs_update_plan.md
      08_cursor_execution_handoff.md
  archived/planning/
    executive_roadmap.md
    phases.md                    # Phases 1–54 complete; next 55
  developer/
    aws-deployment.md
    aws-operations.md
```

Do **not** recreate `implementing.md`, `future_considerations.md`, or flat `roadmap_v1_*.md` files at the planning root — this `phases/` folder is the roadmap.

---

## Categories

| Category | Where |
|----------|--------|
| Active roadmap | `phases/10` (vision `05`) |
| Deferred but valuable | `deferred_backlog.md` |
| Unprioritized ideas | `general_backlog.md` |
| Completed history | `archived/planning/phases.md` |
| Superseded | Annotate in place, then drop on next cleanup |

---

## Band → archive map

| Band | Archive phase | Status |
|------|---------------|--------|
| v1.1 | 50 | Complete |
| v1.2 | 51 | Complete |
| v1.3 | 52 | Complete |
| v1.4 | 53 | Complete |
| v2.0 foundation | 54 | Complete |
| v2.1 cutover/auth/graph | 55 (when done) | **Active** |

---

## Docs to keep current

| Doc | Action |
|-----|--------|
| [../../developer/aws-deployment.md](../../developer/aws-deployment.md) | Reflect API + UI + worker + **web**, selective deploy, ALB cutover when live |
| [../../developer/aws-operations.md](../../developer/aws-operations.md) | Worker/web smoke, pause includes web when deployed |
| [../deferred_backlog.md](../deferred_backlog.md) | Completed bands → archive table; schedule next band rows |
| [../general_backlog.md](../general_backlog.md) | Speculative only |
| [../../archived/planning/](../../archived/planning/) | Append when bands ship |

---

## Acceptance

Docs are aligned when: one active roadmap (`phases/`), deferred vs general backlogs are clear, archive phase numbers match shipped bands, deployment docs match infra, and the **current** band is obvious ([10](10_v2_1_cutover_auth_and_graph_depth.md)).
