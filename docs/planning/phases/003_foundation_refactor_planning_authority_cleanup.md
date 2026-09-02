# Phase 003 — Foundation Refactor Planning and Authority Cleanup

## Status

Active.

Phase 003 is authorized by the Phase 002 exit review.

This phase converts Phase 002 architecture decisions into implementation-ready foundation plans while cleaning up documentation authority and historical material.

It is not a broad implementation rewrite.

---

# Purpose

Phase 003 prepares the project for safe implementation refactoring by ensuring that accepted concepts, architecture decisions, terminology, lifecycle rules, privacy boundaries, analysis boundaries, cost-state rules, UI/report language, and acceptance gates are packaged into actionable implementation plans.

Phase 003 exists to prevent implementation work from being driven by stale prototype assumptions, old v2.1 planning material, or transcription-only product framing.

---

# Governing Inputs

Primary authority:

```text
docs/concepts/
docs/planning/architecture/002i_phase_002_exit_review_consolidation.md
docs/planning/inventories/002i_phase_003_authorized_scope.md
```

Supporting Phase 002 architecture outputs:

```text
docs/planning/architecture/002c_data_lifecycle_retention_architecture_plan.md
docs/planning/architecture/002d_privacy_boundary_encryption_architecture_plan.md
docs/planning/architecture/002e_analysis_boundary_hypothesis_safety_architecture_plan.md
docs/planning/architecture/002f_cost_state_personal_deployment_architecture_plan.md
docs/planning/architecture/002g_ui_ux_concept_alignment_plan.md
docs/planning/architecture/002h_refactor_backlog_sequencing_acceptance_gates.md
```

---

# Phase Division Verification

Phase 003 has been verified as appropriately divided.

Verification record:

```text
docs/planning/inventories/003_phase_division_verification.md
```

Result:

```text
Phase 003 is appropriately divided.
Proceed with 003-A.
```

---

# Required Subgroups

| Subphase | Status | Purpose |
|---|---|---|
| 003-A — Documentation Authority Cleanup and Historical Material Reconciliation | Complete | Reconcile stale docs, mark historical/reference material, and lock current authority |
| 003-B — Domain Terminology and Concept Mapping Implementation Plan | Complete | Convert accepted concept/domain mappings into implementation-ready planning targets |
| 003-C — Data Lifecycle / Retention Foundation Implementation Plan | Complete | Prepare lifecycle, retention, deletion, and artifact-state implementation plan |
| 003-D — Privacy Boundary / Encryption Baseline Implementation Plan | Next | Prepare owner scope, log redaction, service access, encryption baseline, and encryption target plan |
| 003-E — Analysis Boundary / Validation Implementation Plan | Planned | Prepare analysis scopes, lens contracts, hypotheses, safety posture, validators, prompts, reports, corpus reasoning, and evaluation plan |
| 003-F — Cost-State Control Plane Implementation Plan | Planned | Prepare sleep/wake, job safety, workflow replacement, and control-plane implementation plan |
| 003-G — UI/Report Alignment Implementation Plan | Planned | Prepare UI/report terminology, evidence scope, safety, retention, corpus, export, and cost-state implementation plan |
| 003-H — Phase 003 Exit Review and Consolidation | Mandatory gate | Consolidate Phase 003 and authorize or block the next numbered phase |

---

# Mandatory Exit Gate

Phase 003 cannot be considered complete until 003-H is complete.

The exit review must consolidate:

- accepted Phase 003 plans
- authority cleanup results
- historical material reconciliation status
- implementation work packages
- mandatory gates attached to work packages
- deferred questions
- next phase readiness

---

# Current Accepted Outputs

| Subphase | Outputs |
|---|---|
| Phase 003 division verification | `docs/planning/inventories/003_phase_division_verification.md` |
| 003-A | `docs/planning/architecture/003a_documentation_authority_cleanup_plan.md`, `docs/planning/inventories/003a_living_authority_surface_audit.md`, `docs/planning/inventories/003a_historical_material_reconciliation_inventory.md` |
| 003-B | `docs/planning/architecture/003b_domain_terminology_concept_mapping_implementation_plan.md`, `docs/planning/inventories/003b_domain_concept_mapping_inventory.md`, `docs/planning/inventories/003b_domain_terminology_migration_work_packages.md` |
| 003-C | `docs/planning/architecture/003c_data_lifecycle_retention_foundation_implementation_plan.md`, `docs/planning/inventories/003c_lifecycle_artifact_implementation_matrix.md`, `docs/planning/inventories/003c_retention_deletion_work_packages.md`, `docs/planning/inventories/003c_deletion_cascade_gate_checklist.md` |

---

# Non-goals

Phase 003 does not automatically authorize:

- broad backend refactor
- schema migration execution
- prompt replacement
- validator implementation
- report renderer rewrite
- frontend component rewrite
- deployment automation restoration
- GitHub Actions restoration
- cloud infrastructure changes
- retention worker implementation
- encryption implementation
- production data migration

Any such work must be planned, gated, and authorized by later subgroup or phase decisions.

---

# Exit Criteria

Phase 003 is complete only when:

- all accepted subgroups 003-A through 003-G are complete
- 003-H exit review is complete
- stale/historical documentation handling is explicit
- implementation work packages are sequenced
- mandatory gates are attached to work packages
- deferred decisions are explicit
- the next phase is named
- implementation authorization is accepted, modified, or blocked
