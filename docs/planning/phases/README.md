# Relationship Reasoning Engine — Active roadmap (v1.1 → v2.0)

This folder is the **canonical active plan** after v1.0.0. Historical Phases 1–49 live in [../../archived/planning/phases.md](../../archived/planning/phases.md).

## How to use

1. Read [00_unified_roadmap_overview.md](00_unified_roadmap_overview.md).
2. Execute the current band (today: **v1.4 complete → next v2.0 planning**).
3. Keep unscheduled-but-valuable items in [../deferred_backlog.md](../deferred_backlog.md); unprioritized ideas in [../general_backlog.md](../general_backlog.md).
4. When a band ships, append numbered phases to the archived phase log (starting at **50** for v1.1).

## Files

| File | Role |
|------|------|
| [00_unified_roadmap_overview.md](00_unified_roadmap_overview.md) | Strategy + phase order |
| [01_v1_1_operational_hardening.md](01_v1_1_operational_hardening.md) | Reliability, deploy, IAM, worker ops |
| [02_v1_2_evaluation_safety_api_react_readiness.md](02_v1_2_evaluation_safety_api_react_readiness.md) | Eval harness, safety fixtures, API contracts |
| [03_v1_3_react_mvp_product_depth.md](03_v1_3_react_mvp_product_depth.md) | React MVP + product depth |
| [04_v1_4_platform_maturity_react_expansion.md](04_v1_4_platform_maturity_react_expansion.md) | React expansion + platform maturity — **complete** |
| [05_v2_0_future_state_architecture.md](05_v2_0_future_state_architecture.md) | **Next** — v2 target architecture |
| [06_react_transition_plan.md](06_react_transition_plan.md) | Streamlit → React transition |
| [07_backlog_triage_and_docs_update_plan.md](07_backlog_triage_and_docs_update_plan.md) | How to triage backlog without losing items |
| [08_cursor_execution_handoff.md](08_cursor_execution_handoff.md) | Execution rules + first PR order |

## Core strategy

```text
operational reliability
→ security boundaries
→ evaluation quality
→ safety testing
→ API stability
→ React product UI
→ case/longitudinal depth
→ v2 platform maturity
```

Do **not** add analysis modules for breadth. Durable assets are API contracts, domain model, evidence, ontology/graph, evaluation harness, workflow engine, case model, safety boundaries, and product UX.
