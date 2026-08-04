# Planning

Active planning for the **Relationship Reasoning Engine** after **v1.0.0**.

The roadmap is guided by the [core product tenets](../product/core_tenets.md):

- evidence traceability · confidence calibration · multi-lens analysis · non-diagnostic discipline
- longitudinal case tracking · professional workflow fit · safety-aware framing · structured reasoning graph

Prioritize work that strengthens these tenets. Stay **market-agnostic** (no clinician/couples/enterprise specialization in the core engine yet).

| Document | Purpose |
|----------|---------|
| **[phases/](phases/)** | **Active execution** — start at [001](phases/001_v2_1_phase_sequence_overview.md) → [009](phases/009_v2_1_react_api_contract_and_release_candidate_readiness.md) |
| **[v2_readiness_assessment.md](v2_readiness_assessment.md)** | Why next work → v2 beta/RC, not yet GA |
| **[v2_future_state_architecture.md](v2_future_state_architecture.md)** | v2 vision / north star |
| **[auth_rbac_plan.md](auth_rbac_plan.md)** | Auth path — **email OTP first** (ADR 001); Cognito/SSO later |
| **[react_frontend_plan.md](react_frontend_plan.md)** | React stack, screens, API client, deploy |
| **[streamlit_role_decision.md](streamlit_role_decision.md)** | Streamlit admin/eval (ALB cutover deferred) |
| **[deferred_backlog.md](deferred_backlog.md)** | Items not in `001`–`009` (or waiting on a dependency) |
| **[general_backlog.md](general_backlog.md)** | Unprioritized ideas (no commitment) |

### Archive practice

When a phase/band ships:

1. Append to [../archived/planning/phases.md](../archived/planning/phases.md) (next free number: **55**).
2. Move detail checklists from `phases/` → [../archived/planning/bands/](../archived/planning/bands/).
3. Refresh executive roadmap and backlog pointers.
4. Keep `phases/` limited to unfinished work (+ README).

Completed history: [../archived/planning/](../archived/planning/) (Phases **1–54**).

**Design anchors:** [../design/01_product_vision_and_scope.md](../design/01_product_vision_and_scope.md) · [../design/04_knowledge_ontology.md](../design/04_knowledge_ontology.md) · [../design/03_domain_model.md](../design/03_domain_model.md)

**AWS ops:** [../developer/aws-operations.md](../developer/aws-operations.md) · [../developer/aws-deployment.md](../developer/aws-deployment.md) · [../../infra/dev/README.md](../../infra/dev/README.md)
