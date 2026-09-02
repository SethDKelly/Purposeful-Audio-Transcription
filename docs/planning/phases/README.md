# Planning Phases

This folder holds planning phases for the concept-reset refactor sequence.

## Current authority

The concept foundation remains the highest planning authority:

```text
docs/concepts/
```

Implementation guardrails for Phase 004 are installed at:

```text
AGENTS.md
.cursor/rules/concept-refactor-guardrails.mdc
docs/planning/implementation_guardrails.md
```

Phase 002 is complete and consolidated.

Phase 003 is complete and consolidated.

The current active phase is:

```text
Phase 004 — Controlled Foundation Refactor Implementation
```

Current status:

```text
004-A complete
004-B complete
004-C next
004-I mandatory exit gate
```

Older v2.1 numeric phase files remain reference material until they are reconciled, archived, or superseded during Phase 004 or later work.

---

# Completed Phase 002 Sequence

| File | Status | Role |
|---|---|---|
| [002_concept_to_architecture_refactor_roadmap.md](002_concept_to_architecture_refactor_roadmap.md) | Complete | Phase 002 overview and sequence |
| [002a_documentation_authority_terminology_inventory.md](002a_documentation_authority_terminology_inventory.md) | Complete | Documentation authority and terminology inventory |
| [002b_concept_to_domain_model_mapping.md](002b_concept_to_domain_model_mapping.md) | Complete | Concept-to-domain model mapping |
| [002c_data_lifecycle_retention_architecture_plan.md](002c_data_lifecycle_retention_architecture_plan.md) | Complete | Data lifecycle and retention architecture plan |
| [002d_privacy_boundary_encryption_architecture_plan.md](002d_privacy_boundary_encryption_architecture_plan.md) | Complete | Privacy boundary and encryption architecture plan |
| [002e_analysis_boundary_hypothesis_safety_architecture_plan.md](002e_analysis_boundary_hypothesis_safety_architecture_plan.md) | Complete | Analysis boundary, hypothesis, and safety architecture plan |
| [002f_cost_state_personal_deployment_architecture_plan.md](002f_cost_state_personal_deployment_architecture_plan.md) | Complete | Cost state and personal deployment architecture plan |
| [002g_ui_ux_concept_alignment_plan.md](002g_ui_ux_concept_alignment_plan.md) | Complete | UI/UX concept alignment plan |
| [002h_refactor_backlog_sequencing_acceptance_gates.md](002h_refactor_backlog_sequencing_acceptance_gates.md) | Complete | Refactor backlog, sequencing, and acceptance gates |
| [002i_phase_exit_review_consolidation.md](002i_phase_exit_review_consolidation.md) | Complete | Phase 002 exit review and consolidation |

---

# Completed Phase 003 Sequence

| File | Status | Role |
|---|---|---|
| [003_foundation_refactor_planning_authority_cleanup.md](003_foundation_refactor_planning_authority_cleanup.md) | Complete | Phase 003 overview and sequence |
| [003a_documentation_authority_cleanup_historical_material_reconciliation.md](003a_documentation_authority_cleanup_historical_material_reconciliation.md) | Complete | Documentation authority cleanup and historical material reconciliation |
| [003b_domain_terminology_concept_mapping_implementation_plan.md](003b_domain_terminology_concept_mapping_implementation_plan.md) | Complete | Domain terminology and concept mapping implementation plan |
| [003c_data_lifecycle_retention_foundation_implementation_plan.md](003c_data_lifecycle_retention_foundation_implementation_plan.md) | Complete | Data lifecycle / retention foundation implementation plan |
| [003d_privacy_boundary_encryption_baseline_implementation_plan.md](003d_privacy_boundary_encryption_baseline_implementation_plan.md) | Complete | Privacy boundary / encryption baseline implementation plan |
| [003e_analysis_boundary_validation_implementation_plan.md](003e_analysis_boundary_validation_implementation_plan.md) | Complete | Analysis boundary / validation implementation plan |
| [003f_cost_state_control_plane_implementation_plan.md](003f_cost_state_control_plane_implementation_plan.md) | Complete | Cost-state control plane implementation plan |
| [003g_ui_report_alignment_implementation_plan.md](003g_ui_report_alignment_implementation_plan.md) | Complete | UI/report alignment implementation plan |
| [003h_phase_exit_review_consolidation.md](003h_phase_exit_review_consolidation.md) | Complete | Phase 003 exit review and consolidation |

---

# Phase 003 Exit Result

```text
Phase 003 passes exit review.
Phase 003 is complete.
Phase 004 is authorized with controlled implementation scope.
Broad implementation rewrite remains blocked.
```

---

# Active Phase 004 Sequence

Phase 004 is authorized as:

```text
Phase 004 — Controlled Foundation Refactor Implementation
```

| File / Subphase | Status | Role |
|---|---|---|
| [004_controlled_foundation_refactor_implementation.md](004_controlled_foundation_refactor_implementation.md) | Active | Phase 004 overview and sequence |
| [004a_implementation_authority_lock_agent_rules_documentation_guardrails.md](004a_implementation_authority_lock_agent_rules_documentation_guardrails.md) | Complete | Implementation authority lock, agent rules, and documentation guardrails |
| [004b_domain_terminology_compatibility_concept_contract_implementation.md](004b_domain_terminology_compatibility_concept_contract_implementation.md) | Complete | Domain terminology compatibility and concept contract implementation |
| 004c_lifecycle_retention_sourceartifact_deletion_cascade_foundation.md | Next | Lifecycle, retention, SourceArtifact, and deletion-cascade foundation |
| 004d_privacy_boundary_owner_scope_route_redaction_encryption_baseline.md | Planned | Privacy boundary, owner scope, route, redaction, and encryption baseline |
| 004e_analysis_scope_validation_safety_hypothesis_corpus_gates.md | Planned | AnalysisScope, ValidationResult, SafetyPosture, Hypothesis, and corpus gates |
| 004f_cost_state_control_plane_blocking_jobs_idle_wake_shutdown_safety.md | Planned | Cost-state control plane, blocking jobs, idle, wake, and shutdown safety |
| 004g_ui_report_alignment_scope_display_export_delete_status_surfaces.md | Planned | UI/report alignment, scope display, export/delete previews, and status surfaces |
| 004h_evaluation_regression_release_readiness_backlog_closure.md | Planned | Evaluation, regression, release readiness, and implementation backlog closure |
| 004i_phase_exit_review_consolidation.md | Mandatory gate | Phase 004 exit review and consolidation |

---

# Phase 004 Guardrails

Before implementation work, read:

```text
AGENTS.md
.cursor/rules/concept-refactor-guardrails.mdc
docs/planning/implementation_guardrails.md
```

Every implementation subgroup must name Phase 003 work packages, applicable gates, compatibility posture, migration posture, tests/verification, and deferred work.

---

# Mandatory Exit Gate

Every numbered phase must end with an exit review and consolidation subgroup.

For Phase 004, the required final subgroup is:

```text
004-I — Phase 004 Exit Review and Consolidation
```

The next numbered phase may not start until 004-I is complete.

---

# Non-Goals

Do not start broad implementation refactoring merely because Phase 003 is complete.

Do not restore GitHub Actions until the new cost-state/control-plane and workflow replacement approach has passed the applicable Phase 004 gates.

Do not introduce enterprise org/workspace/RBAC/SSO/compliance/billing or always-on availability as Phase 004 baseline scope.
