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

Phase 004 adds implementation guardrails before controlled foundation implementation proceeds:

```text
AGENTS.md
.cursor/rules/concept-refactor-guardrails.mdc
docs/planning/implementation_guardrails.md
```

Start here:

| Area | Document |
|---|---|
| Agent/contributor rules | [../AGENTS.md](../AGENTS.md) |
| Cursor guardrail rule | [../.cursor/rules/concept-refactor-guardrails.mdc](../.cursor/rules/concept-refactor-guardrails.mdc) |
| Implementation guardrails | [planning/implementation_guardrails.md](planning/implementation_guardrails.md) |
| Concept foundation | [concepts/README.md](concepts/README.md) |
| Domain terminology compatibility guide | [domain/README.md](domain/README.md) |
| Planning index | [planning/README.md](planning/README.md) |
| Phase sequence | [planning/phases/README.md](planning/phases/README.md) |
| Phase 004 overview | [planning/phases/004_controlled_foundation_refactor_implementation.md](planning/phases/004_controlled_foundation_refactor_implementation.md) |
| Completed 004-A summary | [planning/phases/004a_implementation_authority_lock_agent_rules_documentation_guardrails.md](planning/phases/004a_implementation_authority_lock_agent_rules_documentation_guardrails.md) |
| Completed 004-B summary | [planning/phases/004b_domain_terminology_compatibility_concept_contract_implementation.md](planning/phases/004b_domain_terminology_compatibility_concept_contract_implementation.md) |
| Phase 004 division verification | [planning/inventories/004_phase_division_verification.md](planning/inventories/004_phase_division_verification.md) |
| Phase 004 authorized scope | [planning/inventories/003h_phase_004_authorized_scope.md](planning/inventories/003h_phase_004_authorized_scope.md) |
| Phase 003 exit review | [planning/phases/003h_phase_exit_review_consolidation.md](planning/phases/003h_phase_exit_review_consolidation.md) |
| Mandatory exit gate policy | [planning/phase_exit_gate_policy.md](planning/phase_exit_gate_policy.md) |

## Current plan status

Phase 001 is complete.

Phase 002 is complete.

Phase 003 is complete.

Phase 004 is active.

Current subgroup status:

```text
004-A complete
004-B complete
004-C next
004-I mandatory exit gate
```

Phase 004 is authorized with controlled, gate-driven implementation scope. Broad implementation rewrite remains blocked.

## Product identity

| Name | Current role |
|---|---|
| Purposeful Audio Transcription | Historical repository name / legacy shell |
| Secure Conversation Analysis and Reflection System | Current concept-level product identity |
| Relationship Reasoning Engine (RRE) | Internal analysis-engine identity |
| Audio transcription | Input capability, not product identity |

## Phase 004 implementation outputs

| Area | Document / Surface |
|---|---|
| Phase 004 overview | [planning/phases/004_controlled_foundation_refactor_implementation.md](planning/phases/004_controlled_foundation_refactor_implementation.md) |
| Phase 004 division verification | [planning/inventories/004_phase_division_verification.md](planning/inventories/004_phase_division_verification.md) |
| Implementation guardrails | [planning/implementation_guardrails.md](planning/implementation_guardrails.md) |
| 004-A authority plan | [planning/architecture/004a_implementation_authority_lock_agent_rules_documentation_guardrails.md](planning/architecture/004a_implementation_authority_lock_agent_rules_documentation_guardrails.md) |
| 004-A guardrail surface inventory | [planning/inventories/004a_guardrail_surface_inventory.md](planning/inventories/004a_guardrail_surface_inventory.md) |
| 004-A agent rule checklist | [planning/inventories/004a_agent_rule_checklist.md](planning/inventories/004a_agent_rule_checklist.md) |
| 004-A phase summary | [planning/phases/004a_implementation_authority_lock_agent_rules_documentation_guardrails.md](planning/phases/004a_implementation_authority_lock_agent_rules_documentation_guardrails.md) |
| 004-B domain contract implementation record | [planning/architecture/004b_domain_terminology_compatibility_concept_contract_implementation.md](planning/architecture/004b_domain_terminology_compatibility_concept_contract_implementation.md) |
| 004-B domain contract surface inventory | [planning/inventories/004b_domain_contract_surface_inventory.md](planning/inventories/004b_domain_contract_surface_inventory.md) |
| 004-B domain compatibility gate checklist | [planning/inventories/004b_domain_compatibility_gate_checklist.md](planning/inventories/004b_domain_compatibility_gate_checklist.md) |
| 004-B phase summary | [planning/phases/004b_domain_terminology_compatibility_concept_contract_implementation.md](planning/phases/004b_domain_terminology_compatibility_concept_contract_implementation.md) |
| Domain terminology guide | [domain/README.md](domain/README.md) |
| Runtime concept contracts | `../backend/domain/concept_contracts.py` |
| Domain contract tests | `../tests/test_domain_concept_contracts.py` |

## Completed Phase 003 planning outputs

| Area | Document |
|---|---|
| Phase 003 exit review | [planning/architecture/003h_phase_003_exit_review_consolidation.md](planning/architecture/003h_phase_003_exit_review_consolidation.md) |
| Phase 003 output inventory | [planning/inventories/003h_phase_003_output_inventory.md](planning/inventories/003h_phase_003_output_inventory.md) |
| Phase 004 authorized scope | [planning/inventories/003h_phase_004_authorized_scope.md](planning/inventories/003h_phase_004_authorized_scope.md) |
| Authority cleanup | [planning/architecture/003a_documentation_authority_cleanup_plan.md](planning/architecture/003a_documentation_authority_cleanup_plan.md) |
| Domain terminology mapping | [planning/architecture/003b_domain_terminology_concept_mapping_implementation_plan.md](planning/architecture/003b_domain_terminology_concept_mapping_implementation_plan.md) |
| Lifecycle / retention implementation plan | [planning/architecture/003c_data_lifecycle_retention_foundation_implementation_plan.md](planning/architecture/003c_data_lifecycle_retention_foundation_implementation_plan.md) |
| Privacy/encryption implementation plan | [planning/architecture/003d_privacy_boundary_encryption_baseline_implementation_plan.md](planning/architecture/003d_privacy_boundary_encryption_baseline_implementation_plan.md) |
| Analysis boundary / validation implementation plan | [planning/architecture/003e_analysis_boundary_validation_implementation_plan.md](planning/architecture/003e_analysis_boundary_validation_implementation_plan.md) |
| Cost-state control-plane implementation plan | [planning/architecture/003f_cost_state_control_plane_implementation_plan.md](planning/architecture/003f_cost_state_control_plane_implementation_plan.md) |
| UI/report alignment implementation plan | [planning/architecture/003g_ui_report_alignment_implementation_plan.md](planning/architecture/003g_ui_report_alignment_implementation_plan.md) |

## User documentation

Existing user documentation remains useful, but may contain legacy product names or workflow assumptions. It should be reconciled during Phase 004 and later refactor phases before being treated as current product authority.

## Developer documentation

Developer documentation remains useful as implementation reference material, but it is not product authority when it conflicts with accepted concept decisions.

Key developer references include development setup, architecture, API reference, AWS operations/deployment notes, and log-redaction notes. These remain pending reconciliation unless Phase 004 or a later accepted phase explicitly accepts them.

## Design package

The older design package is reference material. Phase 003 classified and reconciled its authority role; implementation must continue to prefer accepted concept and Phase 003 planning authority when conflicts exist.

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
004-C — Lifecycle, Retention, SourceArtifact, and Deletion-Cascade Foundation
```
