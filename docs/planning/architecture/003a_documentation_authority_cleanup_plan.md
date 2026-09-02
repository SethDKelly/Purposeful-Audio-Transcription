# 003-A Documentation Authority Cleanup and Historical Material Reconciliation Plan

## Status

Accepted as the Phase 003-A documentation authority cleanup plan.

This plan defines how living documentation, historical material, legacy design docs, user/developer docs, and implementation reference material should be treated during the foundation refactor planning phase.

It does not authorize broad code, schema, UI, prompt, deployment, or pipeline changes.

---

# Purpose

Prevent stale documentation from reasserting product authority during implementation planning.

Phase 003-A exists because the repository contains valuable prototype, user, developer, design, release, and archived planning material created before the concept reset.

Those materials should not be discarded blindly, but they must be classified so future agents know whether they are:

- current authority
- active planning authority
- reference material
- historical material
- superseded material
- pending reconciliation
- implementation reference

---

# Accepted Authority Rule

```text
Current concept authority and accepted Phase 002 architecture decisions govern future planning.
Legacy docs may inform implementation only after reconciliation.
```

---

# Current Authority Stack

Use this authority order until changed by a later accepted exit review:

```text
docs/concepts/
→ docs/planning/architecture/002i_phase_002_exit_review_consolidation.md
→ docs/planning/inventories/002i_phase_003_authorized_scope.md
→ docs/planning/phases/003_foundation_refactor_planning_authority_cleanup.md
→ accepted Phase 003 subgroup outputs
→ reconciled implementation plans
→ code
```

The concept authority order still remains:

```text
concept design
→ product philosophy
→ domain model
→ security/privacy model
→ analysis philosophy
→ implementation architecture
→ code
```

---

# Documentation Classification Model

## Current authority

Documents that govern product meaning, accepted concepts, and active planning.

Examples:

- `docs/concepts/`
- Phase 002 exit review and accepted architecture outputs
- Phase 003 overview and accepted subgroup outputs
- mandatory phase exit gate policy

## Active planning authority

Documents that define the currently active phase or subgroup.

Examples:

- `docs/planning/phases/003_foundation_refactor_planning_authority_cleanup.md`
- `docs/planning/phases/003a_documentation_authority_cleanup_historical_material_reconciliation.md`

## Reference material

Documents that may contain useful implementation, product, or design ideas, but are not current authority unless reconciled.

Examples:

- legacy user docs
- legacy developer docs
- prior design package docs
- older planning backlogs

## Historical material

Documents that describe past state and should not be edited to pretend they are current.

Examples:

- release notes
- archived planning docs
- old phase files retained for provenance

## Superseded material

Documents or sections whose product identity, terminology, lifecycle rules, safety posture, or operating assumptions conflict with accepted concepts.

Superseded material should be marked, linked to current authority, or replaced by future implementation plans.

## Pending reconciliation

Documents that have not yet been fully audited against concept authority.

Use this for areas that are likely useful but may contain stale framing.

## Implementation reference

Code, migrations, scripts, infrastructure, and operational notes that describe how the prototype currently works.

Implementation reference is not product authority.

---

# 003-A Cleanup Decisions

## 1. Living indexes must point to Phase 003

Repository entry points should now show:

```text
Phase 002 complete
Phase 003 active
003-A complete
003-B next
```

Living indexes include:

- root `README.md`
- `docs/README.md`
- `docs/planning/README.md`
- `docs/planning/phases/README.md`

## 2. Phase 003 should have its own overview

The project should not rely only on 002-I to define Phase 003.

Phase 003 has a dedicated overview:

```text
docs/planning/phases/003_foundation_refactor_planning_authority_cleanup.md
```

## 3. Older docs remain available but classified

Legacy docs should not be deleted or rewritten wholesale during 003-A.

They remain useful reference material, but future implementation planning must reconcile them against accepted concepts before treating them as current.

## 4. Release notes remain historical

Release notes should not be edited to match current concept status.

They document past project state and should remain historical unless a later retrospective document is added.

## 5. Design package remains reference pending targeted reconciliation

The older `docs/design/` package contains useful domain, ontology, evidence, UI, and testing material.

It should be treated as reference material until Phase 003-B through 003-G reconcile the relevant sections.

## 6. User and developer docs remain reference pending future rewrite

User-facing and developer-facing docs may contain outdated product identity, deployment, UI, or workflow assumptions.

They should remain available but must not override current concept/architecture authority.

## 7. Code remains implementation reference until planned refactor

Existing code and migrations can inform implementation planning.

They do not override accepted product concepts, retention rules, privacy rules, analysis boundaries, or cost-state requirements.

---

# Historical Reconciliation States

Use these reconciliation labels in future audits:

| Label | Meaning |
|---|---|
| `current_authority` | Governs current concept or active planning |
| `active_planning` | Governs the current subgroup or phase |
| `reference_pending_reconciliation` | Useful but not yet reconciled with accepted concepts |
| `historical` | Retained for provenance/past state |
| `superseded` | Conflicts with accepted concepts or has been replaced |
| `implementation_reference` | Describes current prototype behavior, not product authority |
| `deferred` | Valid potential direction but not current scope |

---

# Agent Guidance

Future agents should:

1. start with `README.md`, `docs/README.md`, `docs/planning/README.md`, and `docs/planning/phases/README.md`
2. treat `docs/concepts/` as highest current product authority
3. treat Phase 002 architecture outputs as accepted planning authority
4. treat Phase 003 outputs as active implementation-planning authority
5. cite older docs only as reference, unless reconciled by an accepted Phase 003 subgroup
6. avoid restoring old workflows, terminology, product framing, or deployment assumptions without gate review
7. avoid treating code as product authority where it conflicts with accepted concepts

---

# Acceptance Gates Satisfied by 003-A

003-A directly supports:

- documentation authority gate
- terminology drift gate
- release readiness gate, for documentation status only

003-A prepares later groups for:

- domain mapping gate
- retention gate
- privacy boundary gate
- analysis boundary gate
- cost state gate
- UI language gate
- workflow replacement gate
- evaluation gate

---

# Non-goals

003-A does not implement:

- code changes
- schema migrations
- prompt changes
- validator changes
- report rendering changes
- frontend changes
- deployment changes
- workflow restoration
- release note rewrites
- full user guide rewrite
- full developer guide rewrite

---

# Handoff to 003-B

003-B should use this cleanup plan to inspect domain terminology and produce implementation-ready mapping plans without allowing legacy docs or code names to override accepted concepts.

The next subgroup is:

```text
003-B — Domain Terminology and Concept Mapping Implementation Plan
```