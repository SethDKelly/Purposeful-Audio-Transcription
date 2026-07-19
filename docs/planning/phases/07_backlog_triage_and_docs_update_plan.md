# 07 — Backlog triage and docs update

## Purpose

Keep planning coherent: active work lives in `docs/planning/phases/`; nothing useful is lost from older backlogs.

---

## Rule

Do **not** delete backlog items unless they are obsolete **and** already completed.

Instead:

- assign covered items to a v1.1–v2.0 phase file (checkbox / workstream)
- leave unscheduled-but-valuable items in [../deferred_backlog.md](../deferred_backlog.md)
- leave unprioritized ideas in [../general_backlog.md](../general_backlog.md)
- mark rows `Completed`, `Superseded`, `Scheduled (v1.x)`, or `No longer planned`
- preserve rationale where possible

---

## Canonical planning layout (current)

```text
docs/
  planning/
    README.md
    deferred_backlog.md          # prioritized, not yet / not fully scheduled
    general_backlog.md           # no priority
    phases/                      # ACTIVE ROADMAP
      00_unified_roadmap_overview.md
      01_v1_1_operational_hardening.md
      02_v1_2_evaluation_safety_api_react_readiness.md
      03_v1_3_react_mvp_product_depth.md
      04_v1_4_platform_maturity_react_expansion.md
      05_v2_0_future_state_architecture.md
      06_react_transition_plan.md
      07_backlog_triage_and_docs_update_plan.md
      08_cursor_execution_handoff.md
  archived/planning/
    executive_roadmap.md         # Phases 1–49 summary
    phases.md                    # sequential completed phases
  developer/
    aws-deployment.md            # AWS architecture (not under planning/)
    aws-operations.md
```

Do **not** recreate `implementing.md`, `future_considerations.md`, or flat `roadmap_v1_*.md` files at the planning root — this `phases/` folder is the roadmap.

---

## Categories

| Category | Where |
|----------|--------|
| Active roadmap | `phases/01`–`05` |
| Deferred but valuable | `deferred_backlog.md` |
| Unprioritized ideas | `general_backlog.md` |
| Completed history | `archived/planning/phases.md` |
| Superseded | Annotate in place, then drop on next cleanup |

---

## Scheduled into active roadmap (from prior deferred lists)

### v1.1 — [01](01_v1_1_operational_hardening.md)

- test invocation + repo hygiene
- deployment docs truth (API / UI / worker)
- selective component deployment
- service-specific IAM
- worker queue operations
- service observability
- Streamlit/API boundary cleanup

### v1.2 — [02](02_v1_2_evaluation_safety_api_react_readiness.md)

- golden evaluation harness
- safety red-team fixtures
- forbidden-claim scoring
- module version comparison
- `/api/v1` contract stabilization
- OpenAPI / client readiness
- React stack decision (implementation in v1.3)

### v1.3 — [03](03_v1_3_react_mvp_product_depth.md)

- React MVP
- evidence-linked report viewer
- case model depth / feedback UX
- long-transcript chunking foundation
- React deploy path

### v1.4 — [04](04_v1_4_platform_maturity_react_expansion.md)

- graph exploration UI richness
- longitudinal case dashboard maturity
- auth/RBAC planning
- supply-chain / backup drills
- Streamlit admin-only decision

### v2.0 — [05](05_v2_0_future_state_architecture.md)

- React primary UI
- platform / multi-user maturity
- evaluation release gates
- safety governance
- production deployment maturity

---

## Docs to keep current

| Doc | Action |
|-----|--------|
| [../../developer/aws-deployment.md](../../developer/aws-deployment.md) | Reflect API + UI + **worker**, selective deploy, IAM targets, ALB/health |
| [../../developer/aws-operations.md](../../developer/aws-operations.md) | Worker smoke, pause includes worker |
| [../deferred_backlog.md](../deferred_backlog.md) | Tag rows scheduled into v1.x; leave true deferrals |
| [../general_backlog.md](../general_backlog.md) | Speculative only |
| [../../archived/planning/](../../archived/planning/) | Append when bands ship |

---

## Acceptance

Docs are aligned when: one active roadmap (`phases/`), deferred vs general backlogs are clear, deployment docs match infra (including worker), React is staged via [06](06_react_transition_plan.md), and v1.1 is obviously the current work.
