# 002-A — Documentation Authority and Terminology Inventory

## Status

Complete for Phase 002 planning.

This subgroup identifies documentation authority surfaces, stale status risks, and terminology mappings before architecture mapping begins.

---

# Purpose

Phase 002-A prevents documentation drift from carrying old product assumptions into the refactor roadmap.

It answers:

- Which docs are current authority?
- Which docs are reference material only?
- Which living indexes needed immediate correction?
- Which terms are accepted?
- Which terms are legacy, discouraged, or caution-zone?
- What should 002-B use as its terminology basis?

---

# Outputs

| Output | Document |
|---|---|
| Documentation authority inventory | `../inventories/002a_documentation_authority_inventory.md` |
| Terminology inventory | `../inventories/002a_terminology_inventory.md` |
| Phase exit gate policy | `../phase_exit_gate_policy.md` |
| Active Phase 002 overview | `002_concept_to_architecture_refactor_roadmap.md` |

---

# Accepted authority order

```text
Concept design
→ Product philosophy
→ Domain model
→ Security/privacy model
→ Analysis philosophy
→ Implementation architecture
→ Code
```

---

# Living indexes updated

The following living indexes were updated as part of 002-A:

- root `README.md`
- `docs/README.md`
- `docs/planning/README.md`
- `docs/planning/phases/README.md`
- `docs/concepts/README.md`
- `docs/concepts/022_refactor_readiness_decision.md`
- `docs/planning/phases/001e_concept_acceptance_refactor_readiness.md`

---

# Key decisions

## 1. Concept docs are current authority

`docs/concepts/` is the current source of truth for product concept, analysis boundary, privacy/retention posture, cost posture, and refactor readiness.

## 2. Older implementation/design docs are reference material

Older design, developer, release, and v2.1 planning docs remain useful, but they must be reconciled before becoming implementation authority.

## 3. Current planning requires an exit gate

Every future phase must end with a phase exit review and consolidation subgroup.

## 4. Active terminology is now explicit

The current product identity is `Secure Conversation Analysis and Reflection System`.

`Purposeful Audio Transcription` is the historical repository shell.

`Relationship Reasoning Engine` is the internal engine identity.

`Audio transcription` is an input capability.

---

# Immediate stale-status corrections

Corrected current living indexes that still pointed to the old v2.1 sequence or removed GitHub Actions workflows.

Older detailed docs are not all rewritten in 002-A. They are inventoried for later reconciliation.

---

# Handoff to 002-B

002-B should use the terminology inventory and concept authority inventory to map accepted concepts to current implementation artifacts.

Proceed next to:

```text
002-B — Concept-to-Domain Model Mapping
```
