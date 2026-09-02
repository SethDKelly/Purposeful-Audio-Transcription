# Phase 004 — Controlled Foundation Refactor Implementation

## Status

Active.

Phase 004 is authorized by the Phase 003 exit review and consolidation.

This phase begins controlled foundation implementation under the accepted concept, architecture, and gate model.

It is not a broad implementation rewrite.

---

# Purpose

Phase 004 implements foundation changes in bounded, dependency-aware subgroups so the prototype can move toward the accepted product concept without losing existing behavior or reintroducing authority drift.

The phase exists to execute Phase 003 work packages while preserving:

- concept authority
- documentation authority
- domain compatibility
- lifecycle and retention semantics
- privacy and owner scope
- analysis boundaries and validation gates
- cost-state and job-safe shutdown semantics
- UI/report product-boundary alignment
- evaluation and regression discipline

---

# Governing Inputs

Primary authority:

```text
docs/concepts/
docs/planning/architecture/003h_phase_003_exit_review_consolidation.md
docs/planning/inventories/003h_phase_004_authorized_scope.md
docs/planning/inventories/004_phase_division_verification.md
```

Supporting Phase 003 implementation plans:

```text
docs/planning/architecture/003a_documentation_authority_cleanup_plan.md
docs/planning/architecture/003b_domain_terminology_concept_mapping_implementation_plan.md
docs/planning/architecture/003c_data_lifecycle_retention_foundation_implementation_plan.md
docs/planning/architecture/003d_privacy_boundary_encryption_baseline_implementation_plan.md
docs/planning/architecture/003e_analysis_boundary_validation_implementation_plan.md
docs/planning/architecture/003f_cost_state_control_plane_implementation_plan.md
docs/planning/architecture/003g_ui_report_alignment_implementation_plan.md
```

---

# Phase Division Verification

Phase 004 has been verified as appropriately divided.

Verification record:

```text
docs/planning/inventories/004_phase_division_verification.md
```

Result:

```text
Phase 004 is appropriately divided.
Proceed with 004-A.
```

---

# Required Subgroups

| Subphase | Status | Purpose |
|---|---|---|
| 004-A — Implementation Authority Lock, Agent Rules, and Documentation Guardrails | Complete | Install contributor/agent guardrails before code implementation begins |
| 004-B — Domain Terminology Compatibility and Concept Contract Implementation | Next | Add aliases/contracts/DTO posture for accepted domain language without destructive rename-first refactor |
| 004-C — Lifecycle, Retention, SourceArtifact, and Deletion-Cascade Foundation | Planned | Implement lifecycle/retention foundations and deletion cascade contracts incrementally |
| 004-D — Privacy Boundary, Owner Scope, Route, Redaction, and Encryption Baseline | Planned | Harden owner scope, route access, redaction, lifecycle events, and baseline encryption verification |
| 004-E — AnalysisScope, ValidationResult, SafetyPosture, Hypothesis, and Corpus Gates | Planned | Implement analysis-boundary contracts and validators before expanding reports/corpus/export behavior |
| 004-F — Cost-State Control Plane, Blocking Jobs, Idle, Wake, and Shutdown Safety | Planned | Implement or reconcile control-plane contracts and job-safe shutdown behavior |
| 004-G — UI/Report Alignment, Scope Display, Export/Delete Previews, and Status Surfaces | Planned | Align user-facing surfaces after supporting contracts/gates exist |
| 004-H — Evaluation, Regression, Release Readiness, and Implementation Backlog Closure | Planned | Consolidate tests, regressions, release gates, and implementation backlog status |
| 004-I — Phase 004 Exit Review and Consolidation | Mandatory gate | Decide whether implementation phase passes and whether another phase is authorized |

---

# Phase 004 Operating Rule

Every implementation subgroup must name:

1. the Phase 003 work packages it is executing
2. the applicable gates
3. compatibility posture
4. test/verification expectations
5. migration posture, when relevant
6. deferred or blocked work
7. subgroup exit result

Subgroups may implement only their accepted scope.

---

# Current Accepted Outputs

| Subphase | Outputs |
|---|---|
| Phase 004 division verification | `docs/planning/inventories/004_phase_division_verification.md` |
| 004-A | `AGENTS.md`, `.cursor/rules/concept-refactor-guardrails.mdc`, `docs/planning/implementation_guardrails.md`, `docs/planning/architecture/004a_implementation_authority_lock_agent_rules_documentation_guardrails.md`, `docs/planning/inventories/004a_guardrail_surface_inventory.md`, `docs/planning/inventories/004a_agent_rule_checklist.md` |

---

# Blocked Unless Later Authorized and Gated

Phase 004 does not automatically authorize:

- broad backend rewrite
- broad frontend rewrite
- destructive class/table renames without compatibility and migration plan
- production schema/data migration execution
- prompt replacement without validation gates
- report renderer rewrite without ReportScope and validation gates
- corpus expansion without privacy/retention/scope/staleness gates
- export expansion without export-readiness/privacy gates
- GitHub Actions restoration without cost-state, privacy, job-safety, and release-readiness gates
- production cloud changes without control-plane/shutdown gates
- long-term retained audio
- enterprise org/workspace/RBAC/SSO/compliance/billing
- always-on enterprise availability

---

# Mandatory Exit Gate

Phase 004 cannot be considered complete until 004-I is complete.

The exit review must consolidate:

- actual implementation completed
- code/schema/docs/tests changed
- gates satisfied or failed
- deferred work
- blocked work
- compatibility posture
- migration status
- next phase readiness

---

# Exit Criteria

Phase 004 is complete only when:

- all accepted subgroups 004-A through 004-H are complete, modified, or explicitly blocked
- 004-I exit review is complete
- implementation changes are mapped to Phase 003 work packages
- required gates are checked
- tests/regressions are recorded
- deferred decisions are explicit
- next phase is named
- implementation authorization is accepted, modified, or blocked

---

# Next Phase

Proceed to:

```text
004-B — Domain Terminology Compatibility and Concept Contract Implementation
```
