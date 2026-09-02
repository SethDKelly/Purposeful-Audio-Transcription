# 004-A Guardrail Surface Inventory

## Status

Accepted as the Phase 004-A guardrail surface inventory.

---

# Purpose

Inventory the repository-facing guardrail surfaces installed or recognized by 004-A.

These surfaces are designed to keep Phase 004 implementation bounded, gate-driven, and aligned with the accepted concept model.

---

# Guardrail Surface Matrix

| Surface | Path | Status | Audience | Authority Role | Maintenance Rule |
|---|---|---|---|---|---|
| Concept authority | `docs/concepts/` | existing_authority | all contributors / agents | Highest product and design authority | Do not override from code or legacy docs |
| Phase exit policy | `docs/planning/phase_exit_gate_policy.md` | existing_authority | phase planners / agents | Requires every numbered phase to end with exit review | Keep referenced by phase indexes |
| Phase 003 exit review | `docs/planning/architecture/003h_phase_003_exit_review_consolidation.md` | existing_authority | Phase 004 implementers | Authorizes controlled implementation and carries gates forward | Do not loosen without later exit review |
| Phase 004 authorized scope | `docs/planning/inventories/003h_phase_004_authorized_scope.md` | existing_authority | Phase 004 implementers | Defines allowed/blocked Phase 004 scope | Use as authorization boundary |
| Phase 004 division verification | `docs/planning/inventories/004_phase_division_verification.md` | added_by_004a | planners / agents | Confirms Phase 004 subgroup split | Update only if Phase 004 structure changes by accepted decision |
| Phase 004 overview | `docs/planning/phases/004_controlled_foundation_refactor_implementation.md` | added_by_004a | all contributors / agents | Living Phase 004 sequence and status surface | Update after each Phase 004 subgroup |
| Implementation guardrails | `docs/planning/implementation_guardrails.md` | added_by_004a | all contributors / agents | Compact canonical guardrail reference | Keep concise; update when current subgroup changes |
| Agent rules | `AGENTS.md` | added_by_004a | Codex / agents / contributors | Repository-root operational rules | Keep high signal and reference deeper docs |
| Cursor rule | `.cursor/rules/concept-refactor-guardrails.mdc` | added_by_004a | Cursor sessions | Always-applied Cursor guardrail | Keep concise and synchronized with guardrails |
| 004-A plan | `docs/planning/architecture/004a_implementation_authority_lock_agent_rules_documentation_guardrails.md` | added_by_004a | planners / reviewers | Records the 004-A decision and installed surfaces | Historical after 004-A completion |
| 004-A checklist | `docs/planning/inventories/004a_agent_rule_checklist.md` | added_by_004a | reviewers / agents | Checklist for future implementation sessions | Use for PR/subgroup review |
| 004-A phase summary | `docs/planning/phases/004a_implementation_authority_lock_agent_rules_documentation_guardrails.md` | added_by_004a | phase readers | Closure summary and 004-B handoff | Historical after completion |
| Planning phases index | `docs/planning/phases/README.md` | living_index | all contributors / agents | Current phase/subgroup status | Update after each subgroup |
| Planning README | `docs/planning/README.md` | living_index | all contributors / agents | Planning entry point | Update after each subgroup when status changes |
| Docs README | `docs/README.md` | living_index | all contributors / agents | Documentation entry point | Update after major phase/subgroup changes |
| Root README | `README.md` | living_index | repo visitors / contributors | Repository entry point | Keep status current and non-duplicative |

---

# Surface Classification

## Current authority

```text
docs/concepts/
docs/planning/phase_exit_gate_policy.md
docs/planning/architecture/003h_phase_003_exit_review_consolidation.md
docs/planning/inventories/003h_phase_004_authorized_scope.md
docs/planning/phases/004_controlled_foundation_refactor_implementation.md
docs/planning/implementation_guardrails.md
AGENTS.md
.cursor/rules/concept-refactor-guardrails.mdc
```

## Living indexes

```text
README.md
docs/README.md
docs/concepts/README.md
docs/planning/README.md
docs/planning/phases/README.md
```

## Implementation-reference material

```text
backend/
frontend-react/
config/
docs/developer/
docs/design/
alembic/
Dockerfile.*
scripts / operational material where present
```

Implementation-reference material may inform work but does not override accepted authority.

## Historical/reference material

```text
release notes
archived planning
older v2.1 planning
legacy user docs
legacy developer docs not yet reconciled
```

Historical/reference material should not be deleted or rewritten as current truth merely because it is outdated.

---

# Guardrail Coverage Assessment

| Guardrail Need | Surface Coverage | Result |
|---|---|---|
| Agent entry point | `AGENTS.md` | Covered |
| Cursor-native rule | `.cursor/rules/concept-refactor-guardrails.mdc` | Covered |
| Compact canonical implementation rule | `docs/planning/implementation_guardrails.md` | Covered |
| Phase 004 status and sequence | `docs/planning/phases/004_controlled_foundation_refactor_implementation.md` | Covered |
| Phase subdivision verification | `docs/planning/inventories/004_phase_division_verification.md` | Covered |
| Gate checklist for agents | `docs/planning/inventories/004a_agent_rule_checklist.md` | Covered |
| Living index status | README/docs/planning indexes | Covered after 004-A index updates |

---

# Drift Risks

Potential future drift points:

- `AGENTS.md` and Cursor rules may fall behind the phase index.
- Root README may become stale if status is duplicated too often.
- Developer docs may still describe legacy operations or workflows.
- Code names may still expose legacy product framing until later Phase 004 subgroups reconcile them.
- GitHub Actions guidance may conflict with cleared-workflow status unless explicitly gated later.

Mitigation:

```text
Keep AGENTS.md and implementation_guardrails.md concise.
Use docs/planning/phases/README.md as the status source.
Update living indexes after each subgroup.
Do not rewrite historical docs as current authority without accepted reconciliation.
```

---

# Decision

The guardrail surface set is sufficient for 004-A.

Future Phase 004 implementation may proceed to 004-B only within the accepted gate-driven boundary.
