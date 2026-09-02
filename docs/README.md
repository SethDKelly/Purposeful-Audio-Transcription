# Documentation Index

## Current documentation authority

The current design authority is the concept foundation:

```text
concept design
→ product philosophy
→ domain model
→ security/privacy model
→ analysis philosophy
→ implementation architecture
→ code
```

Start here:

| Area | Document |
|---|---|
| Concept foundation | [concepts/README.md](concepts/README.md) |
| Phase 001 acceptance | [concepts/021_concept_acceptance_summary.md](concepts/021_concept_acceptance_summary.md) |
| Refactor readiness | [concepts/022_refactor_readiness_decision.md](concepts/022_refactor_readiness_decision.md) |
| Planning index | [planning/README.md](planning/README.md) |
| Phase sequence | [planning/phases/README.md](planning/phases/README.md) |
| Active Phase 003 overview | [planning/phases/003_foundation_refactor_planning_authority_cleanup.md](planning/phases/003_foundation_refactor_planning_authority_cleanup.md) |
| Completed 003-A summary | [planning/phases/003a_documentation_authority_cleanup_historical_material_reconciliation.md](planning/phases/003a_documentation_authority_cleanup_historical_material_reconciliation.md) |
| Completed 003-B summary | [planning/phases/003b_domain_terminology_concept_mapping_implementation_plan.md](planning/phases/003b_domain_terminology_concept_mapping_implementation_plan.md) |
| Completed 003-C summary | [planning/phases/003c_data_lifecycle_retention_foundation_implementation_plan.md](planning/phases/003c_data_lifecycle_retention_foundation_implementation_plan.md) |
| Completed 003-D summary | [planning/phases/003d_privacy_boundary_encryption_baseline_implementation_plan.md](planning/phases/003d_privacy_boundary_encryption_baseline_implementation_plan.md) |
| Completed 003-E summary | [planning/phases/003e_analysis_boundary_validation_implementation_plan.md](planning/phases/003e_analysis_boundary_validation_implementation_plan.md) |
| Completed Phase 002 roadmap | [planning/phases/002_concept_to_architecture_refactor_roadmap.md](planning/phases/002_concept_to_architecture_refactor_roadmap.md) |
| Phase 002 exit review | [planning/phases/002i_phase_exit_review_consolidation.md](planning/phases/002i_phase_exit_review_consolidation.md) |
| Mandatory exit gate policy | [planning/phase_exit_gate_policy.md](planning/phase_exit_gate_policy.md) |

## Current plan status

Phase 002 is complete.

The current active phase is:

```text
Phase 003 — Foundation Refactor Planning and Authority Cleanup
```

Current subgroup status:

```text
003-A complete
003-B complete
003-C complete
003-D complete
003-E complete
003-F next
```

## Product identity

| Name | Current role |
|---|---|
| Purposeful Audio Transcription | Historical repository name / legacy shell |
| Secure Conversation Analysis and Reflection System | Current concept-level product identity |
| Relationship Reasoning Engine (RRE) | Internal analysis-engine identity |
| Audio transcription | Input capability, not product identity |

## Current Phase 003 planning outputs

| Area | Document |
|---|---|
| Authority cleanup | [planning/architecture/003a_documentation_authority_cleanup_plan.md](planning/architecture/003a_documentation_authority_cleanup_plan.md) |
| Domain terminology mapping | [planning/architecture/003b_domain_terminology_concept_mapping_implementation_plan.md](planning/architecture/003b_domain_terminology_concept_mapping_implementation_plan.md) |
| Domain concept mapping inventory | [planning/inventories/003b_domain_concept_mapping_inventory.md](planning/inventories/003b_domain_concept_mapping_inventory.md) |
| Domain terminology work packages | [planning/inventories/003b_domain_terminology_migration_work_packages.md](planning/inventories/003b_domain_terminology_migration_work_packages.md) |
| Lifecycle / retention implementation plan | [planning/architecture/003c_data_lifecycle_retention_foundation_implementation_plan.md](planning/architecture/003c_data_lifecycle_retention_foundation_implementation_plan.md) |
| Lifecycle artifact matrix | [planning/inventories/003c_lifecycle_artifact_implementation_matrix.md](planning/inventories/003c_lifecycle_artifact_implementation_matrix.md) |
| Retention/deletion work packages | [planning/inventories/003c_retention_deletion_work_packages.md](planning/inventories/003c_retention_deletion_work_packages.md) |
| Deletion cascade checklist | [planning/inventories/003c_deletion_cascade_gate_checklist.md](planning/inventories/003c_deletion_cascade_gate_checklist.md) |
| Privacy/encryption implementation plan | [planning/architecture/003d_privacy_boundary_encryption_baseline_implementation_plan.md](planning/architecture/003d_privacy_boundary_encryption_baseline_implementation_plan.md) |
| Privacy/encryption surface matrix | [planning/inventories/003d_privacy_encryption_surface_matrix.md](planning/inventories/003d_privacy_encryption_surface_matrix.md) |
| Privacy/encryption work packages | [planning/inventories/003d_privacy_encryption_work_packages.md](planning/inventories/003d_privacy_encryption_work_packages.md) |
| Encryption/access gate checklist | [planning/inventories/003d_encryption_and_access_gate_checklist.md](planning/inventories/003d_encryption_and_access_gate_checklist.md) |
| Analysis boundary / validation implementation plan | [planning/architecture/003e_analysis_boundary_validation_implementation_plan.md](planning/architecture/003e_analysis_boundary_validation_implementation_plan.md) |
| Analysis validation surface matrix | [planning/inventories/003e_analysis_validation_surface_matrix.md](planning/inventories/003e_analysis_validation_surface_matrix.md) |
| Analysis validation work packages | [planning/inventories/003e_analysis_validation_work_packages.md](planning/inventories/003e_analysis_validation_work_packages.md) |
| Analysis validation gate checklist | [planning/inventories/003e_analysis_validation_gate_checklist.md](planning/inventories/003e_analysis_validation_gate_checklist.md) |

## User documentation

Existing user documentation remains useful, but may contain legacy product names or workflow assumptions. It should be reconciled during Phase 003 and later refactor phases.

## Developer documentation

Developer documentation remains useful as implementation reference material, but it is not product authority when it conflicts with accepted concept decisions.

Key developer references include development setup, architecture, API reference, AWS operations/deployment notes, and log-redaction notes. These remain pending reconciliation unless a Phase 003 subgroup explicitly accepts them.

## Design package

The older design package is reference material. Phase 003 should determine which parts are accepted, superseded, renamed, or deferred for implementation refactor planning.

## Planning

| Document | Description |
|---|---|
| [planning/README.md](planning/README.md) | Planning authority index |
| [planning/phases/](planning/phases/) | Phase sequence |
| [planning/architecture/](planning/architecture/) | Phase architecture plans |
| [planning/inventories/](planning/inventories/) | Phase inventories |
| [planning/deferred_backlog.md](planning/deferred_backlog.md) | Existing deferred backlog reference; pending reconciliation |
| [planning/general_backlog.md](planning/general_backlog.md) | Existing general backlog reference; pending reconciliation |
| [archived/planning/](archived/planning/) | Historical planning archive |

## Releases

Release documents remain historical. They should not be edited to match current status unless explicitly marked as retrospective notes.

## Status rule

Living indexes, contributor instructions, and planning docs must not carry independently maintained stale status. Current status should point to the phase sequence and mandatory exit review for the current phase.

Next subgroup:

```text
003-F — Cost-State Control Plane Implementation Plan
```
