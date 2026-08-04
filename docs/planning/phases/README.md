# Relationship Reasoning Engine — Active roadmap

This folder holds **only unfinished execution phases** for the current band.

Completed history: [../../archived/planning/phases.md](../../archived/planning/phases.md) (Phases **1–54**) · detail checklists in [../../archived/planning/bands/](../../archived/planning/bands/).  
Living plans (not phases): [../](../) — vision, auth, React, backlogs, readiness.

## Active sequence — v2.1 (numeric)

Start at **[001](001_v2_1_phase_sequence_overview.md)**. Implement in order:

| File | Role |
|------|------|
| [001_v2_1_phase_sequence_overview.md](001_v2_1_phase_sequence_overview.md) | Sequence overview + dependency map |
| [002_v2_1_core_tenets_and_governance.md](002_v2_1_core_tenets_and_governance.md) | Tenets + PR/eval governance |
| [003_v2_1_simple_email_auth_and_ownership.md](003_v2_1_simple_email_auth_and_ownership.md) | Passwordless email auth + ownership |
| [004_v2_1_evidence_precision.md](004_v2_1_evidence_precision.md) | Concise evidence spans |
| [005_v2_1_evidence_snapshots_and_versioning.md](005_v2_1_evidence_snapshots_and_versioning.md) | Transcript/evidence version binding |
| [006_v2_1_worker_atomicity_and_operational_safety.md](006_v2_1_worker_atomicity_and_operational_safety.md) | Atomic job claim (remaining gap) |
| [007_v2_1_safety_policy_and_non_diagnostic_enforcement.md](007_v2_1_safety_policy_and_non_diagnostic_enforcement.md) | Config-driven safety / non-diagnostic |
| [008_v2_1_graph_relationship_evidence_and_case_correctness.md](008_v2_1_graph_relationship_evidence_and_case_correctness.md) | Graph edge evidence + case identity |
| [009_v2_1_react_api_contract_and_release_candidate_readiness.md](009_v2_1_react_api_contract_and_release_candidate_readiness.md) | OpenAPI client + v2 RC gates |

**Guiding tenets:** [../product/core_tenets.md](../../product/core_tenets.md) · Auth decision: [ADR 001](../../developer/architecture_decisions/adr_001_simple_email_auth_before_enterprise_sso.md)

Superseded combined band (cutover / Cognito-first): [../../archived/planning/bands/10_v2_1_cutover_auth_and_graph_depth_superseded.md](../../archived/planning/bands/10_v2_1_cutover_auth_and_graph_depth_superseded.md) — leftovers live in [../deferred_backlog.md](../deferred_backlog.md).

## When the sequence ships

1. Append **Phase 55** (and/or per-sub-phase notes) to [../../archived/planning/phases.md](../../archived/planning/phases.md).
2. Move completed checklists → [../../archived/planning/bands/](../../archived/planning/bands/).
3. Update [../../archived/planning/executive_roadmap.md](../../archived/planning/executive_roadmap.md) and deferred backlog.
4. Leave only unfinished work (and this README) here.

Do **not** add analysis modules for breadth. Prefer evidence, confidence, safety, ownership, and graph correctness.
