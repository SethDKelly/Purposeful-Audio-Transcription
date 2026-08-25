# Planning Phases

This folder holds planning phases for the concept-reset refactor sequence.

## Current authority

The concept foundation remains the highest planning authority:

```text
docs/concepts/
```

Phase 002 is now complete and consolidated.

The next authorized phase is:

```text
Phase 003 — Foundation Refactor Planning and Authority Cleanup
```

Recommended next subgroup:

```text
003-A — Documentation Authority Cleanup and Historical Material Reconciliation
```

Older v2.1 numeric phase files remain reference material until they are reconciled, archived, or superseded during Phase 003 or later work.

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

# Phase 002 Exit Result

```text
Phase 002 passes exit review.
Phase 002 is complete.
Phase 003 is authorized with explicit scope.
Broad implementation rewrite remains blocked.
```

---

# Authorized Phase 003 Sequence

Phase 003 has been authorized by 002-I with this recommended sequence:

| Group | Status | Role |
|---|---|---|
| 003-A — Documentation Authority Cleanup and Historical Material Reconciliation | Next | Reconcile stale docs and lock current authority |
| 003-B — Domain Terminology and Concept Mapping Implementation Plan | Planned | Convert mappings into implementation planning targets |
| 003-C — Data Lifecycle / Retention Foundation Implementation Plan | Planned | Prepare lifecycle and retention implementation plan |
| 003-D — Privacy Boundary / Encryption Baseline Implementation Plan | Planned | Prepare owner scope, logs, encryption baseline and target plan |
| 003-E — Analysis Boundary / Validation Implementation Plan | Planned | Prepare analysis contracts, validators, prompts, reports, and eval plan |
| 003-F — Cost-State Control Plane Implementation Plan | Planned | Prepare sleep/wake, job safety, and workflow replacement plan |
| 003-G — UI/Report Alignment Implementation Plan | Planned | Prepare UI/report terminology, evidence scope, and safety/corpus surfaces |
| 003-H — Phase 003 Exit Review and Consolidation | Mandatory gate | Consolidate Phase 003 and authorize or block next phase |

---

# Mandatory Exit Gate

Every numbered phase must end with an exit review and consolidation subgroup.

For Phase 003, the required final subgroup is:

```text
003-H — Phase 003 Exit Review and Consolidation
```

The next numbered phase may not start until 003-H is complete.

---

# Non-Goals

Do not start broad implementation refactoring from this folder merely because Phase 002 is complete.

Do not restore GitHub Actions until the new cost-state/control-plane and workflow replacement approach is explicitly planned.
