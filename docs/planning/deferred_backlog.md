# Deferred backlog

Items that were **part of a planned phase** (or explicitly sequenced on the active roadmap) but are **not fully scheduled** yet, or still wait on a dependency.

**Priority:** Prefer these over [general_backlog.md](general_backlog.md) when picking work outside the active band.

**Active roadmap:** [phases/](phases/) (current: **v1.1**).  
Historical phase log: [../archived/planning/phases.md](../archived/planning/phases.md) · Executive view: [../archived/planning/executive_roadmap.md](../archived/planning/executive_roadmap.md).

**Ops standing rules:** AWS-only product; pause when idle; deploy on minor-version tags or manual dispatch.

---

## Scheduled into active roadmap (do not duplicate work)

| Item | Band | Plan |
|------|------|------|
| Test invocation / repo hygiene | v1.1 | [phases/01](phases/01_v1_1_operational_hardening.md) Workstream A |
| Deployment docs + worker topology | v1.1 | [phases/01](phases/01_v1_1_operational_hardening.md) Workstream B |
| Selective component deploy | v1.1 | [phases/01](phases/01_v1_1_operational_hardening.md) Workstream C |
| Service-specific IAM | v1.1 | [phases/01](phases/01_v1_1_operational_hardening.md) Workstream D |
| Worker queue / backpressure / alarms | v1.1 | [phases/01](phases/01_v1_1_operational_hardening.md) Workstream E |
| Streamlit as API-only client | v1.1 | [phases/01](phases/01_v1_1_operational_hardening.md) Workstream F |
| Service observability / smoke | v1.1 | [phases/01](phases/01_v1_1_operational_hardening.md) Workstream G |
| Golden eval harness / richer A/B tooling | v1.2 | [phases/02](phases/02_v1_2_evaluation_safety_api_react_readiness.md) |
| Safety red-team fixtures / forbidden-claim scoring | v1.2 | [phases/02](phases/02_v1_2_evaluation_safety_api_react_readiness.md) |
| React frontend | v1.3 (+ readiness in v1.2) | [phases/03](phases/03_v1_3_react_mvp_product_depth.md) · [phases/06](phases/06_react_transition_plan.md) |
| Knowledge graph UI richness | v1.4 | [phases/04](phases/04_v1_4_platform_maturity_react_expansion.md) |
| Production AWS account | v2.0 / late v1.4 | [phases/05](phases/05_v2_0_future_state_architecture.md) |
| Collaborative review (full) / professional mode | v1.4–v2.0 | product-depth plans |
| Distributed job queue (Celery/Redis) | After v1.1 worker guardrails | Prefer deepen worker first |
| Prometheus `/metrics` / telemetry dashboards | After v1.1 G | observability maturity |

---

## Still deferred (not yet scheduled)

### Ingest & media

| Item | Origin / dependency | Notes |
|------|---------------------|-------|
| **Multi-file audio upload & transcript stitching** | Was P2-A | Prefer stitch over audio concat. Prep + worker exist; schedule when product asks. |
| **Async / background Transcribe UX** | Needs polish on worker UX | Submit → poll/status + UI progress. |

### Analysis & prompts

| Item | Origin / dependency | Notes |
|------|---------------------|-------|
| **Module `inference:` YAML block** | After construct expectations + telemetry | Per-module temperature / max tokens. |
| **Haiku / cheaper model routing** | After telemetry soak | Keep Sonnet for hard lenses + meta. |
| **Raise module concurrency (4–5)** | After parallel=3 soak | Config tune only. |
| **Eval script: construct coverage** | Eval harness detail | Fold into v1.2 runner when built. |

### Collaboration (beyond scheduled bands)

| Item | Notes |
|------|-------|
| **Finding feedback UI (extended)** | Richer notes/tags after v1.3 feedback UX |
| **Multi-conversation report pack (import path)** | After case export workflows settle |
| **Real-time collaborative editing** | Needs auth beyond shared API key |

### Platform

| Item | Notes |
|------|-------|
| **Pinned lockfile (`uv.lock`)** | Opportunistic CI harden |
| **Module scaffolding CLI** | After ontology expectations (already shipped) — still unscheduled |

---

## How items leave this list

1. Assign to a `phases/0N` workstream (or ship and archive as Phase 50+).
2. Or demote to [general_backlog.md](general_backlog.md) if priority is withdrawn.
3. Remove/annotate the row here.
