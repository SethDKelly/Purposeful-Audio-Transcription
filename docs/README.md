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
003-C next
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

## User documentation

Existing user documentation remains useful, but may contain legacy product names or workflow assumptions. It should be reconciled during Phase 003 and later refactor phases.

| Document | Description |
|---|---|
| [user/getting-started.md](user/getting-started.md) | Legacy getting-started path; reference pending reconciliation |
| [user/user-guide.md](user/user-guide.md) | Legacy application guide; reference pending reconciliation |
| [user/deployment.md](user/deployment.md) | AWS deployment pointers; reference pending reconciliation |
| [user/model-setup.md](user/model-setup.md) | Bedrock / Transcribe setup; reference pending reconciliation |

## Developer documentation

Developer documentation remains useful as implementation reference material, but it is not product authority when it conflicts with accepted concept decisions.

| Document | Description |
|---|---|
| [developer/development.md](developer/development.md) | Development setup; implementation reference |
| [developer/architecture.md](developer/architecture.md) | Existing service/data-flow reference; pending reconciliation |
| [developer/api-reference.md](developer/api-reference.md) | Existing REST API summary; implementation reference |
| [developer/aws-operations.md](developer/aws-operations.md) | Existing AWS operation notes; pending cost-state reconciliation |
| [developer/aws-deployment.md](developer/aws-deployment.md) | Existing AWS architecture notes; pending workflow/control-plane reconciliation |
| [developer/log-redaction.md](developer/log-redaction.md) | Existing redaction design; pending verification against current content-free log requirements |

## Design package

The older design package is reference material. Phase 003 should determine which parts are accepted, superseded, renamed, or deferred for implementation refactor planning.

| Document | Topic |
|---|---|
| [design/01_product_vision_and_scope.md](design/01_product_vision_and_scope.md) | Legacy product vision / scope; reference pending reconciliation |
| [design/03_domain_model.md](design/03_domain_model.md) | Existing domain model; reconciled at planning level by 003-B |
| [design/04_knowledge_ontology.md](design/04_knowledge_ontology.md) | Existing ontology; feed 003-B / 003-E |
| [design/09_evidence_confidence_and_citations.md](design/09_evidence_confidence_and_citations.md) | Evidence model reference; feed 003-E |
| [design/11_ui_ux_design.md](design/11_ui_ux_design.md) | Existing UI reference; feed 003-G |
| [design/14_testing_evaluation_and_safety.md](design/14_testing_evaluation_and_safety.md) | Testing/safety reference; feed 003-E / later evaluation |

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

| Document | Description |
|---|---|
| [releases/v1.0.0.md](releases/v1.0.0.md) | Historical release note |
| [releases/v0.9.0.md](releases/v0.9.0.md) | Historical release note |
| [releases/v0.8.0.md](releases/v0.8.0.md) | Historical release note |
| [releases/v0.7.0.md](releases/v0.7.0.md) | Historical release note |

## Status rule

Living indexes, contributor instructions, and planning docs must not carry independently maintained stale status. Current status should point to the phase sequence and mandatory exit review for the current phase.

Next subgroup:

```text
003-C — Data Lifecycle / Retention Foundation Implementation Plan
```