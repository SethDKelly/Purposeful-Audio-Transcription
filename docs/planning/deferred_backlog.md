# Deferred backlog

Items that were **part of a planned phase** (or explicitly sequenced) but are **not** in the active numeric sequence, or still wait on a dependency.

**Priority:** Prefer these over [general_backlog.md](general_backlog.md) when picking work outside `001`–`009`.

**Active roadmap:** [phases/](phases/) — **v2.1 numeric** starting at [001](phases/001_v2_1_phase_sequence_overview.md).  
Historical phase log: [../archived/planning/phases.md](../archived/planning/phases.md) (Phases **1–54**) · Executive view: [../archived/planning/executive_roadmap.md](../archived/planning/executive_roadmap.md).

**Ops standing rules:** AWS-only product; pause when idle; deploy on minor-version tags or manual dispatch.

**Tenet alignment (phase 002):** Active `001`–`009` items strengthen core tenets. Rows below either (a) support reliability/security/external readiness required for those tenets, or (b) are explicitly post-RC. Speculative breadth (extra modules, market specialization, local models) stays in [general_backlog.md](general_backlog.md).

---

## Completed bands (archived — do not re-schedule)

| Band | Archive | Detail checklist |
|------|---------|------------------|
| v1.1 Operational hardening | Phase **50** | [bands/01](../archived/planning/bands/01_v1_1_operational_hardening.md) |
| v1.2 Eval / safety / API v1 / React readiness | Phase **51** | [bands/02](../archived/planning/bands/02_v1_2_evaluation_safety_api_react_readiness.md) |
| v1.3 React MVP | Phase **52** | [bands/03](../archived/planning/bands/03_v1_3_react_mvp_product_depth.md) |
| v1.4 Platform maturity | Phase **53** | [bands/04](../archived/planning/bands/04_v1_4_platform_maturity_react_expansion.md) |
| v2.0 foundation slice | Phase **54** | [bands/09](../archived/planning/bands/09_v2_0_foundation_execution.md) |

Summaries: [../archived/planning/phases.md](../archived/planning/phases.md).

---

## Scheduled into active roadmap (do not duplicate work)

| Item | Phase | Plan |
|------|-------|------|
| Core tenets + PR/eval governance | **002** | [phases/002](phases/002_v2_1_core_tenets_and_governance.md) · [core_tenets.md](../product/core_tenets.md) |
| Simple email auth + resource ownership | **003** | [phases/003](phases/003_v2_1_simple_email_auth_and_ownership.md) · [ADR 001](../developer/architecture_decisions/adr_001_simple_email_auth_before_enterprise_sso.md) · [auth_rbac_plan.md](auth_rbac_plan.md) |
| Evidence precision (concise spans) | **004** | [phases/004](phases/004_v2_1_evidence_precision.md) · [ADR 002](../developer/architecture_decisions/adr_002_concise_evidence_spans.md) |
| Evidence snapshots / transcript versioning | **005** | [phases/005](phases/005_v2_1_evidence_snapshots_and_versioning.md) |
| Atomic worker job claim (remaining gap) | **006** | [phases/006](phases/006_v2_1_worker_atomicity_and_operational_safety.md) |
| Safety policy + non-diagnostic enforcement | **007** | [phases/007](phases/007_v2_1_safety_policy_and_non_diagnostic_enforcement.md) |
| Graph edge evidence + case correctness | **008** | [phases/008](phases/008_v2_1_graph_relationship_evidence_and_case_correctness.md) |
| OpenAPI-generated / contract-checked React client + RC gates | **009** | [phases/009](phases/009_v2_1_react_api_contract_and_release_candidate_readiness.md) |

---

## Deferred from superseded band 10 (post-RC / GA / later)

Former combined plan: [bands/10 superseded](../archived/planning/bands/10_v2_1_cutover_auth_and_graph_depth_superseded.md).

| Item | When | Notes |
|------|------|-------|
| React ALB cutover (`rre-dev-web`, `/admin` Streamlit) | **v2 GA** (see [009](phases/009_v2_1_react_api_contract_and_release_candidate_readiness.md) GA gate) | [streamlit_role_decision.md](streamlit_role_decision.md) |
| Cognito / enterprise SSO | After email auth (**003**) + pilots | [auth_rbac_plan.md](auth_rbac_plan.md) · ADR 001 |
| Graph contradiction / divergence UX | After **008** | Depth beyond edge evidence |
| Case-level report package export | After **008** / RC | Product packaging |
| Split-turn in prepare | Later | Leftover from [bands/03](../archived/planning/bands/03_v1_3_react_mvp_product_depth.md) |
| RDS restore + secret-rotation drills (execute) | **v2 GA** | [data_governance.md](../developer/data_governance.md) |
| Worker/module status UX polish | After **006** | React Analyze polish |
| S3 + CloudFront for React | Post-cutover | Optional static hosting |
| Production AWS account | v2.x / late | [v2_future_state_architecture.md](v2_future_state_architecture.md) |
| Distributed job queue (Celery/Redis) | After worker maturity | Prefer deepen ECS worker first |
| Prometheus `/metrics` | After observability soak | Optional maturity |

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
| **Haiku / cheaper model routing** | After telemetry soak | Cost optimization — does not strengthen tenets by itself; keep deferred. |
| **Raise module concurrency (4–5)** | After parallel=3 soak | Reliability/perf only. |
| **Module `inference:` YAML block** | After construct expectations + telemetry | Prompt tuning affordance — not tenet-critical. |

### Collaboration

| Item | Notes |
|------|-------|
| **Finding feedback UI (extended)** | Richer notes/tags beyond v1.3/v1.4 labels |
| **Multi-conversation report pack (import path)** | After case export settles |
| **Real-time collaborative editing** | Needs auth (**003**) first |

### Platform

| Item | Notes |
|------|-------|
| **Pinned lockfile (`uv.lock`)** | Opportunistic CI harden; npm lock already present |
| **Module scaffolding CLI** | After ontology expectations — still unscheduled |

---

## How items leave this list

1. Assign to a `phases/00N` workstream (or ship and archive as Phase 55+).
2. Or demote to [general_backlog.md](general_backlog.md) if priority is withdrawn.
3. Remove/annotate the row here.
