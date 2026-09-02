# 004-A — Implementation Authority Lock, Agent Rules, and Documentation Guardrails

## Status

Complete.

This subgroup verifies the Phase 004 logical subdivision and installs repository-facing guardrails before controlled implementation begins.

It does not implement backend domain changes, schema migrations, API changes, prompts, validators, report rendering, UI components, retention workers, encryption, cost-state control-plane changes, deployment automation, GitHub Actions, cloud infrastructure, or production data migrations.

---

# Purpose

004-A prevents implementation drift by creating concise, accessible guardrails for agents, Cursor, Codex, contributors, and future subgroup execution.

It answers:

- Is the Phase 004 subdivision logical?
- Where should contributors and agents look before changing implementation?
- What authority order should be followed?
- Which work remains blocked?
- Which gates must future implementation carry forward?
- How should future changes identify scope, gates, compatibility, migration, and verification?
- What is the next authorized subgroup?

---

# Outputs

| Output | Document |
|---|---|
| Phase 004 division verification | `../inventories/004_phase_division_verification.md` |
| Phase 004 overview | `004_controlled_foundation_refactor_implementation.md` |
| Implementation guardrails | `../implementation_guardrails.md` |
| Repository agent rules | `../../AGENTS.md` |
| Cursor guardrails | `../../../.cursor/rules/concept-refactor-guardrails.mdc` |
| Implementation authority plan | `../architecture/004a_implementation_authority_lock_agent_rules_documentation_guardrails.md` |
| Guardrail surface inventory | `../inventories/004a_guardrail_surface_inventory.md` |
| Agent rule checklist | `../inventories/004a_agent_rule_checklist.md` |

---

# Phase 004 Division Verification

Result:

```text
Phase 004 is appropriately divided.
Proceed with 004-A.
```

The division is accepted because it starts with guardrails, preserves dependency order, separates foundation implementation areas, avoids broad rewrite, keeps GitHub Actions and enterprise expansion gated, and includes the mandatory 004-I exit review.

---

# Guardrail Surfaces Added

004-A added:

```text
AGENTS.md
.cursor/rules/concept-refactor-guardrails.mdc
docs/planning/implementation_guardrails.md
docs/planning/phases/004_controlled_foundation_refactor_implementation.md
docs/planning/architecture/004a_implementation_authority_lock_agent_rules_documentation_guardrails.md
docs/planning/inventories/004_phase_division_verification.md
docs/planning/inventories/004a_guardrail_surface_inventory.md
docs/planning/inventories/004a_agent_rule_checklist.md
```

---

# Accepted Decisions

## 1. Phase 004 is properly divided

The 004-A through 004-I structure is logical and remains accepted without modification.

## 2. Guardrails must precede code implementation

004-A is the correct first subgroup because future implementation must be bounded by concept authority, Phase 003 gates, and Phase 004 subgroup scope.

## 3. `AGENTS.md` is the repository-level agent rule entry point

Agents and contributors should begin there before implementation work.

## 4. `.cursor/rules/concept-refactor-guardrails.mdc` is the Cursor-native rule surface

Cursor sessions should receive always-applied guardrails without needing to load every planning file into context.

## 5. `docs/planning/implementation_guardrails.md` is the canonical compact guardrail reference

It should remain concise and updated as Phase 004 progresses.

## 6. Later implementation must identify work packages and gates

Future changes must state subgroup, Phase 003 packages executed, gates, compatibility posture, migration posture, verification, and deferred work.

## 7. Broad rewrite remains blocked

004-A does not authorize broad backend/frontend rewrite, destructive renames, production migrations, GitHub Actions restoration, cloud automation changes, enterprise expansion, prompt replacement, report renderer rewrite, corpus expansion, or export expansion.

---

# Verification

004-A verification consisted of:

- reading Phase 003 exit review and Phase 004 authorization
- reading current planning phase index
- searching for existing repository-level agent/Cursor guardrails
- adding missing guardrail surfaces
- adding Phase 004 overview and division verification
- adding the 004-A plan, inventory, and checklist
- updating living indexes to show 004-A complete and 004-B next

No code or runtime behavior was changed.

---

# Handoff to 004-B

004-B should begin controlled foundation implementation with domain terminology compatibility and concept contracts.

It should use:

```text
AGENTS.md
.cursor/rules/concept-refactor-guardrails.mdc
docs/planning/implementation_guardrails.md
docs/planning/phases/004_controlled_foundation_refactor_implementation.md
docs/planning/architecture/003b_domain_terminology_concept_mapping_implementation_plan.md
docs/planning/inventories/003b_domain_concept_mapping_inventory.md
docs/planning/inventories/003b_domain_terminology_migration_work_packages.md
```

Expected posture:

```text
compatibility / alias / contract first
no destructive rename-first refactor
no production migration unless explicitly gated
```

---

# Non-goals

004-A does not implement:

- code changes
- schema migrations
- domain model changes
- API field changes
- prompt changes
- validator changes
- report renderer changes
- UI component changes
- retention/deletion behavior changes
- owner/auth/privacy changes
- encryption changes
- cost-state worker/control-plane changes
- GitHub Actions restoration
- deployment/cloud changes
- production data migration

---

# Exit Criteria

004-A is complete when:

- Phase 004 subdivision is verified
- Phase 004 overview exists
- repository-level agent rules exist
- Cursor rule surface exists
- compact implementation guardrails exist
- 004-A implementation authority plan exists
- guardrail surface inventory exists
- agent rule checklist exists
- living indexes show 004-A complete and 004-B next
- broad implementation rewrite remains blocked

All criteria are satisfied.

---

# Next Phase

Proceed to:

```text
004-B — Domain Terminology Compatibility and Concept Contract Implementation
```
