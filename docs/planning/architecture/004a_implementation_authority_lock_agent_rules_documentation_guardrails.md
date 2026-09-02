# 004-A Implementation Authority Lock, Agent Rules, and Documentation Guardrails

## Status

Accepted as the Phase 004-A implementation authority lock plan.

004-A is complete.

---

# Purpose

Install repository-facing guardrails before Phase 004 implementation work begins.

004-A ensures that agents, Cursor, Codex, and contributors can quickly identify:

- current authority order
- active phase/subgroup
- product boundary
- required gates
- compatibility-first implementation posture
- sensitive-data restrictions
- blocked work
- next subgroup

This protects implementation from drifting back into prototype authority or legacy transcription-only framing.

---

# Governing Inputs

Primary authority:

```text
docs/concepts/
docs/planning/architecture/003h_phase_003_exit_review_consolidation.md
docs/planning/inventories/003h_phase_004_authorized_scope.md
docs/planning/inventories/004_phase_division_verification.md
docs/planning/phases/004_controlled_foundation_refactor_implementation.md
```

Relevant Phase 003 gates:

```text
documentation authority gate
terminology drift gate
domain compatibility gate
privacy boundary gate
log redaction gate
analysis scope gate
report scope gate
cost state contract gate
job-safe shutdown gate
UI terminology gate
evaluation gate
regression gate
release readiness gate
```

---

# Phase 004 Division Verification

004-A first verified that the Phase 004 subdivision is logical.

Result:

```text
Phase 004 is appropriately divided.
Proceed with 004-A.
```

Verification record:

```text
docs/planning/inventories/004_phase_division_verification.md
```

---

# Implementation Authority Surfaces Installed

004-A adds these repository-facing guardrail surfaces:

| Surface | Path | Purpose |
|---|---|---|
| Agent rules | `AGENTS.md` | High-signal rules for Codex, Cursor, AI assistants, and contributors |
| Cursor rule | `.cursor/rules/concept-refactor-guardrails.mdc` | Always-applied Cursor guardrails for implementation sessions |
| Implementation guardrails | `docs/planning/implementation_guardrails.md` | Canonical concise guardrail reference for Phase 004 work |
| Phase 004 overview | `docs/planning/phases/004_controlled_foundation_refactor_implementation.md` | Current Phase 004 sequence, gates, status, and non-goals |
| 004-A plan | `docs/planning/architecture/004a_implementation_authority_lock_agent_rules_documentation_guardrails.md` | This implementation authority lock plan |
| Guardrail surface inventory | `docs/planning/inventories/004a_guardrail_surface_inventory.md` | Inventory of guardrail surfaces and intended authority role |
| Agent rule checklist | `docs/planning/inventories/004a_agent_rule_checklist.md` | Minimum checks future agents/contributors must pass |
| 004-A phase summary | `docs/planning/phases/004a_implementation_authority_lock_agent_rules_documentation_guardrails.md` | Subgroup summary and next-step handoff |

---

# Accepted Decisions

## 1. 004-A may install guardrails before code changes

This is the correct first Phase 004 implementation action because implementation authority must be locked before domain, lifecycle, privacy, analysis, cost-state, UI, or deployment work begins.

## 2. Agent rules belong at repository root

`AGENTS.md` provides a conventional high-signal entry point for agentic coding sessions and human contributors.

It should remain concise and link to deeper guardrails rather than duplicating every planning artifact.

## 3. Cursor rules should be explicit and always-applied

`.cursor/rules/concept-refactor-guardrails.mdc` provides a Cursor-native rule surface that keeps the concept refactor guardrails in the coding environment.

## 4. Planning guardrails should be canonical and compact

`docs/planning/implementation_guardrails.md` is the canonical compact rule surface for Phase 004 implementation.

It should be kept current if later Phase 004 subgroups change the authorized next step or gate posture.

## 5. Phase 004 overview becomes the living phase authority

`docs/planning/phases/004_controlled_foundation_refactor_implementation.md` is the living Phase 004 overview.

It should be updated by later subgroups as they complete.

## 6. Broad rewrite remains blocked

004-A does not loosen any Phase 003/004 boundaries.

Broad backend rewrite, frontend rewrite, production migrations, GitHub Actions restoration, enterprise expansion, prompt replacement, report renderer rewrite, corpus expansion, export expansion, and cloud automation changes remain blocked unless later subgroups explicitly authorize and gate them.

## 7. Compatibility-first implementation is mandatory

Future work should prefer aliases, adapters, additive contracts, and compatibility layers before destructive renames.

## 8. Sensitive-content restrictions are mandatory

No implementation work should add logs, telemetry, lifecycle events, status messages, or debug outputs that expose transcript bodies, audio, prompt payloads, raw model completions, report bodies, export contents, secrets, tokens, or login codes.

---

# Agent/Contributor Required Pattern

Every non-trivial Phase 004 change should record:

```text
Phase 004 subgroup:
Phase 003 work packages executed:
Applicable gates:
Compatibility posture:
Migration posture:
Tests / verification:
Deferred or explicitly not touched:
```

This keeps implementation review tied to the accepted planning model.

---

# Index Updates Required by 004-A

004-A updates living indexes to show:

```text
Phase 004 active
004-A complete
004-B next
004-I mandatory exit gate
```

The updated index surfaces are:

```text
README.md
docs/README.md
docs/concepts/README.md
docs/planning/README.md
docs/planning/phases/README.md
docs/planning/phases/004_controlled_foundation_refactor_implementation.md
```

---

# Handoff to 004-B

004-B should implement or prepare the first controlled domain compatibility changes.

It should begin from:

```text
docs/planning/architecture/003b_domain_terminology_concept_mapping_implementation_plan.md
docs/planning/inventories/003b_domain_concept_mapping_inventory.md
docs/planning/inventories/003b_domain_terminology_migration_work_packages.md
docs/planning/implementation_guardrails.md
AGENTS.md
.cursor/rules/concept-refactor-guardrails.mdc
```

004-B should not perform destructive physical renames first.

Expected first posture:

```text
alias / contract / adapter first
schema and API compatibility explicit
no production data migration unless gated
```

---

# Non-goals

004-A does not implement:

- backend domain class changes
- schema migrations
- API field changes
- prompt changes
- validator changes
- report renderer changes
- UI component changes
- retention workers
- encryption changes
- cost-state worker/control-plane changes
- GitHub Actions restoration
- cloud infrastructure automation
- production data migration

---

# Exit Criteria

004-A is complete when:

- Phase 004 subdivision is verified
- Phase 004 overview exists
- repository-level agent rules exist
- Cursor rule surface exists
- compact implementation guardrails exist
- guardrail surface inventory exists
- agent rule checklist exists
- 004-A phase summary exists
- living indexes show 004-A complete and 004-B next
- broad implementation rewrite remains blocked

All criteria are satisfied.

---

# Next Phase

Proceed to:

```text
004-B — Domain Terminology Compatibility and Concept Contract Implementation
```
