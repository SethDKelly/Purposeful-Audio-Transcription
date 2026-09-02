# Planning

## Current planning authority

Active planning and controlled implementation are governed by the concept design foundation under:

```text
docs/concepts/
```

Phase 001 accepted the concept foundation and declared the project ready for refactor planning.

Phase 002 translated that concept foundation into architecture, backlog, sequencing, gates, and Phase 003 authorization.

Phase 003 converted Phase 002 architecture into implementation-ready foundation plans and completed the mandatory exit review.

Phase 004 is now active for controlled, gate-driven foundation implementation.

## Current status

| Phase | Status |
|---|---|
| Phase 001 — Concept Validation and Decision Closure | Complete |
| Phase 002 — Concept-to-Architecture Refactor Roadmap | Complete |
| Phase 003 — Foundation Refactor Planning and Authority Cleanup | Complete |
| Phase 004 — Controlled Foundation Refactor Implementation | Active |

Current subgroup status:

```text
004-A complete
004-B next
004-I mandatory exit gate
```

## Start here

| Document | Purpose |
|---|---|
| [../AGENTS.md](../AGENTS.md) | Repository-level agent/contributor rules |
| [../.cursor/rules/concept-refactor-guardrails.mdc](../.cursor/rules/concept-refactor-guardrails.mdc) | Cursor-native always-applied guardrails |
| [implementation_guardrails.md](implementation_guardrails.md) | Compact Phase 004 implementation guardrails |
| [phase_exit_gate_policy.md](phase_exit_gate_policy.md) | Mandatory exit review / consolidation rule for every phase |
| [phases/README.md](phases/README.md) | Phase sequence and current next subgroup |
| [phases/004_controlled_foundation_refactor_implementation.md](phases/004_controlled_foundation_refactor_implementation.md) | Active Phase 004 overview |
| [phases/004a_implementation_authority_lock_agent_rules_documentation_guardrails.md](phases/004a_implementation_authority_lock_agent_rules_documentation_guardrails.md) | Completed 004-A summary |
| [inventories/004_phase_division_verification.md](inventories/004_phase_division_verification.md) | Phase 004 division verification |
| [architecture/004a_implementation_authority_lock_agent_rules_documentation_guardrails.md](architecture/004a_implementation_authority_lock_agent_rules_documentation_guardrails.md) | 004-A implementation authority plan |
| [inventories/004a_guardrail_surface_inventory.md](inventories/004a_guardrail_surface_inventory.md) | 004-A guardrail surface inventory |
| [inventories/004a_agent_rule_checklist.md](inventories/004a_agent_rule_checklist.md) | 004-A agent rule checklist |
| [phases/003h_phase_exit_review_consolidation.md](phases/003h_phase_exit_review_consolidation.md) | Phase 003 exit review summary |
| [architecture/003h_phase_003_exit_review_consolidation.md](architecture/003h_phase_003_exit_review_consolidation.md) | Phase 003 exit decision and consolidation |
| [inventories/003h_phase_003_output_inventory.md](inventories/003h_phase_003_output_inventory.md) | Phase 003 output inventory |
| [inventories/003h_phase_004_authorized_scope.md](inventories/003h_phase_004_authorized_scope.md) | Phase 004 authorized scope |
| [phases/003_foundation_refactor_planning_authority_cleanup.md](phases/003_foundation_refactor_planning_authority_cleanup.md) | Completed Phase 003 overview |
| [architecture/003b_domain_terminology_concept_mapping_implementation_plan.md](architecture/003b_domain_terminology_concept_mapping_implementation_plan.md) | Domain terminology and concept mapping implementation plan for 004-B |
| [inventories/003b_domain_concept_mapping_inventory.md](inventories/003b_domain_concept_mapping_inventory.md) | Domain concept mapping inventory for 004-B |
| [inventories/003b_domain_terminology_migration_work_packages.md](inventories/003b_domain_terminology_migration_work_packages.md) | Domain terminology work packages for 004-B |

## Mandatory exit gate

Every numbered phase must end with an exit review and consolidation document before the next numbered phase begins.

For Phase 004, the mandatory gate is:

```text
004-I — Phase 004 Exit Review and Consolidation
```

## Planning rule

Phase 003 authorizes Phase 004 with explicit controlled implementation scope.

It does not authorize a broad implementation rewrite.

Phase 004 may perform controlled foundation implementation, implementation guardrail installation, compatibility layers, contract implementation, tests, and narrow documentation cleanup required to prevent authority drift.

Older user, developer, design, release, archived, planning, code, and infrastructure materials remain reference, historical, or implementation-reference material unless explicitly reconciled by Phase 003, Phase 004, or a later accepted phase.

Every implementation subgroup must identify:

```text
Phase 003 work packages executed
Applicable gates
Compatibility posture
Migration posture
Tests / verification
Deferred or explicitly not touched
```

Next subgroup:

```text
004-B — Domain Terminology Compatibility and Concept Contract Implementation
```
