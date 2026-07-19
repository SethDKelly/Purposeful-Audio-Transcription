# Deferred backlog

Items that were **part of a planned phase** (or explicitly sequenced on the active roadmap) but are **not fully scheduled** yet, or still wait on a dependency.

**Priority:** Prefer these over [general_backlog.md](general_backlog.md) when picking work outside the active band.

**Active roadmap:** [phases/](phases/) (current: **v2.1** — [10_v2_1_cutover_auth_and_graph_depth.md](phases/10_v2_1_cutover_auth_and_graph_depth.md)).  
Historical phase log: [../archived/planning/phases.md](../archived/planning/phases.md) (Phases **1–54**) · Executive view: [../archived/planning/executive_roadmap.md](../archived/planning/executive_roadmap.md).

**Ops standing rules:** AWS-only product; pause when idle; deploy on minor-version tags or manual dispatch.

---

## Completed bands (archived — do not re-schedule)

| Band | Archive | Plan |
|------|---------|------|
| v1.1 Operational hardening | Phase **50** | [phases/01](phases/01_v1_1_operational_hardening.md) |
| v1.2 Eval / safety / API v1 / React readiness | Phase **51** | [phases/02](phases/02_v1_2_evaluation_safety_api_react_readiness.md) |
| v1.3 React MVP | Phase **52** | [phases/03](phases/03_v1_3_react_mvp_product_depth.md) |
| v1.4 Platform maturity | Phase **53** | [phases/04](phases/04_v1_4_platform_maturity_react_expansion.md) |
| v2.0 foundation slice | Phase **54** | [phases/09](phases/09_v2_0_foundation_execution.md) |

Formerly “scheduled into active roadmap” rows for the above are **done** — see archive, not this section.

---

## Scheduled into active roadmap (do not duplicate work)

| Item | Band | Plan |
|------|------|------|
| React ALB cutover (`rre-dev-web`, `/admin` Streamlit) | v2.1 | [phases/10](phases/10_v2_1_cutover_auth_and_graph_depth.md) Workstream A |
| Cognito / auth MVP beyond shared API key | v2.1 | [phases/10](phases/10_v2_1_cutover_auth_and_graph_depth.md) Workstream B · [auth_rbac_plan.md](auth_rbac_plan.md) |
| Graph contradiction / longitudinal construct depth | v2.1 | [phases/10](phases/10_v2_1_cutover_auth_and_graph_depth.md) Workstream C |
| Case-level report package | v2.1 | [phases/10](phases/10_v2_1_cutover_auth_and_graph_depth.md) Workstream C |
| Split-turn in prepare | v2.1 | [phases/10](phases/10_v2_1_cutover_auth_and_graph_depth.md) Workstream C · leftover from [phases/03](phases/03_v1_3_react_mvp_product_depth.md) |
| RDS restore + secret-rotation drills (execute) | v2.1 | [phases/10](phases/10_v2_1_cutover_auth_and_graph_depth.md) Workstream D · [data_governance.md](../developer/data_governance.md) |
| Worker/module status UX polish | v2.1 | [phases/10](phases/10_v2_1_cutover_auth_and_graph_depth.md) Workstream E |
| Production AWS account | v2.x / late | [phases/05](phases/05_v2_0_future_state_architecture.md) |
| S3 + CloudFront for React | v2.1 spike → later | [phases/10](phases/10_v2_1_cutover_auth_and_graph_depth.md) Workstream D |
| Distributed job queue (Celery/Redis) | After worker UX maturity | Prefer deepen ECS worker first |
| Prometheus `/metrics` | After v1.1 observability | Optional maturity |

---

## Still deferred (not yet scheduled)

### Ingest & media

| Item | Origin / dependency | Notes |
|------|---------------------|-------|
| **Multi-file audio upload & transcript stitching** | Was P2-A | Prefer stitch over audio concat. Prep + worker exist; schedule when product asks. |
| **Async / background Transcribe UX** | Needs polish on worker UX | Submit → poll/status + UI progress; overlaps v2.1 E lightly. |

### Analysis & prompts

| Item | Origin / dependency | Notes |
|------|---------------------|-------|
| **Module `inference:` YAML block** | After construct expectations + telemetry | Per-module temperature / max tokens. |
| **Haiku / cheaper model routing** | After telemetry soak | Keep Sonnet for hard lenses + meta. |
| **Raise module concurrency (4–5)** | After parallel=3 soak | Config tune only. |

### Collaboration

| Item | Notes |
|------|-------|
| **Finding feedback UI (extended)** | Richer notes/tags beyond v1.3/v1.4 labels |
| **Multi-conversation report pack (import path)** | After case export (v2.1 C) settles |
| **Real-time collaborative editing** | Needs auth (v2.1 B) first |

### Platform

| Item | Notes |
|------|-------|
| **Pinned lockfile (`uv.lock`)** | Opportunistic CI harden; npm lock already present |
| **Module scaffolding CLI** | After ontology expectations — still unscheduled |
| **OpenAPI-generated TS client in CI** | Hand client ships; `scripts/export_openapi.py` exists — wire when drift hurts |

---

## How items leave this list

1. Assign to a `phases/0N` workstream (or ship and archive as Phase 55+).
2. Or demote to [general_backlog.md](general_backlog.md) if priority is withdrawn.
3. Remove/annotate the row here.
