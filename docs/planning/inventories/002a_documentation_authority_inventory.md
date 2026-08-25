# 002-A Documentation Authority Inventory

## Status

Accepted as the Phase 002-A documentation authority inventory.

---

# Current authority tiers

## Tier 1 — Current design authority

| Path | Authority |
|---|---|
| `docs/concepts/README.md` | Concept foundation index |
| `docs/concepts/021_concept_acceptance_summary.md` | Phase 001 accepted concept consolidation |
| `docs/concepts/022_refactor_readiness_decision.md` | Refactor-readiness and Phase 002 sequence |
| `docs/planning/phase_exit_gate_policy.md` | Mandatory phase exit gate policy |
| `docs/planning/phases/002_concept_to_architecture_refactor_roadmap.md` | Active Phase 002 plan |

## Tier 2 — Current living indexes

| Path | Required posture |
|---|---|
| `README.md` | Repository entry point; must reflect concept-reset/refactor-planning status |
| `docs/README.md` | Documentation index; must point to current authority |
| `docs/planning/README.md` | Planning index; must point to active phase and exit gate |
| `docs/planning/phases/README.md` | Active phase sequence |

## Tier 3 — Reference material pending reconciliation

| Path group | Status |
|---|---|
| `docs/design/` | Reference material; not current authority until reconciled |
| `docs/developer/` | Implementation reference; not product authority |
| `docs/product/core_tenets.md` | Durable tenets, but terminology may need alignment with concept decisions |
| `docs/security/` | Security reference; must be reconciled with retention/encryption decisions |
| `docs/evaluation/` | Evaluation reference; must be reconciled with accepted boundaries |
| `docs/planning/phases/*v2_1*` | Older planning/reference material unless carried forward |
| `docs/releases/` | Historical release notes |
| `docs/archived/` | Historical archive |

---

# Documentation drift risks

| Risk | Required handling |
|---|---|
| Old active phase references | Update living indexes immediately |
| Old product identity | Replace in living docs; preserve in history docs |
| GitHub Actions references | Mark as stale until new pipeline plan exists |
| Clinical/diagnostic language | Reframe as reasoning references, not product authority |
| Enterprise framing | Keep as future policy/deployment layer |
| Release documents | Preserve as historical unless explicitly amended |

---

# 002-A actions taken

- Updated root README to reflect concept-reset/refactor-planning status.
- Updated docs index to identify current authority.
- Updated planning index and phase index to point to Phase 002.
- Added mandatory phase exit gate policy.
- Added Phase 002 overview and 002-A phase document.
- Added terminology inventory.

---

# Open reconciliation backlog

Later phases should inspect and reconcile:

- older design package terminology
- developer architecture language
- user guide terminology
- security docs vs accepted retention/encryption posture
- evaluation docs vs hypothesis/safety boundary
- stale workflow/deploy instructions
- v2.1 numeric phase files

Do not rewrite all reference docs in 002-A. Use this inventory to guide the architecture roadmap.
