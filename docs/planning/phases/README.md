# Relationship Reasoning Engine — Active roadmap (v1.1 → v2.x)

This folder is the **canonical active plan** after v1.0.0. Historical Phases **1–54** live in [../../archived/planning/phases.md](../../archived/planning/phases.md).

## How to use

1. Read [00_unified_roadmap_overview.md](00_unified_roadmap_overview.md).
2. Execute the current band (today: **v2.1** — [10](10_v2_1_cutover_auth_and_graph_depth.md)).
3. Keep unscheduled-but-valuable items in [../deferred_backlog.md](../deferred_backlog.md); unprioritized ideas in [../general_backlog.md](../general_backlog.md).
4. When a band ships, append numbered phases to the archived phase log (next: **Phase 55**).

## Files

| File | Role |
|------|------|
| [00_unified_roadmap_overview.md](00_unified_roadmap_overview.md) | Strategy + phase order |
| [01_v1_1_operational_hardening.md](01_v1_1_operational_hardening.md) | Complete — Phase 50 |
| [02_v1_2_evaluation_safety_api_react_readiness.md](02_v1_2_evaluation_safety_api_react_readiness.md) | Complete — Phase 51 |
| [03_v1_3_react_mvp_product_depth.md](03_v1_3_react_mvp_product_depth.md) | Complete — Phase 52 |
| [04_v1_4_platform_maturity_react_expansion.md](04_v1_4_platform_maturity_react_expansion.md) | Complete — Phase 53 |
| [05_v2_0_future_state_architecture.md](05_v2_0_future_state_architecture.md) | v2 vision (north star) |
| [09_v2_0_foundation_execution.md](09_v2_0_foundation_execution.md) | Complete — Phase 54 |
| [10_v2_1_cutover_auth_and_graph_depth.md](10_v2_1_cutover_auth_and_graph_depth.md) | **Active** — cutover, auth, graph/case depth |
| [06_react_transition_plan.md](06_react_transition_plan.md) | Streamlit → React transition (mostly executed) |
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
→ v2 foundation
→ cutover + auth + graph depth
→ full v2 platform maturity
```

Do **not** add analysis modules for breadth. Durable assets are API contracts, domain model, evidence, ontology/graph, evaluation harness, workflow engine, case model, safety boundaries, and product UX.
