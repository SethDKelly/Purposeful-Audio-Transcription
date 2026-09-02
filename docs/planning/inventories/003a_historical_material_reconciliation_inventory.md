# 003-A Historical Material Reconciliation Inventory

## Status

Accepted as the Phase 003-A historical material reconciliation inventory.

---

# Purpose

Classify existing repository documentation and implementation materials so future work can use them without confusing historical, reference, implementation, and current authority.

This inventory does not delete or rewrite historical material.

---

# Core Reconciliation Rule

```text
Use older material as evidence of prior design and implementation work, not as current authority unless a Phase 003 subgroup explicitly reconciles it with accepted concepts.
```

---

# Current Authority Materials

| Material | Classification | Notes |
|---|---|---|
| `docs/concepts/` | current_authority | Highest current product/concept authority |
| `docs/planning/phase_exit_gate_policy.md` | current_authority | Mandatory phase exit pattern |
| `docs/planning/architecture/002i_phase_002_exit_review_consolidation.md` | current_authority | Phase 002 closure and readiness decision |
| `docs/planning/inventories/002i_phase_003_authorized_scope.md` | current_authority | Authorizes Phase 003 scope |
| `docs/planning/phases/003_foundation_refactor_planning_authority_cleanup.md` | active_planning | Phase 003 overview |
| `docs/planning/phases/003a_documentation_authority_cleanup_historical_material_reconciliation.md` | active_planning | 003-A summary |

---

# Phase 002 Materials

| Material | Classification | Handling |
|---|---|---|
| `docs/planning/phases/002*_*.md` | completed_planning_authority | Retain as accepted Phase 002 record |
| `docs/planning/architecture/002*_*.md` | completed_architecture_authority | Use as accepted architecture planning input |
| `docs/planning/inventories/002*_*.md` | completed_inventory_authority | Use as accepted inventory/gate input |

Phase 002 materials are not historical in the same sense as old release notes. They are completed planning authority that Phase 003 should build from.

---

# Legacy User Documentation

| Material | Classification | Reconciliation Needed |
|---|---|---|
| `docs/user/getting-started.md` | reference_pending_reconciliation | May contain older onboarding, product identity, and flow assumptions |
| `docs/user/user-guide.md` | reference_pending_reconciliation | Should later align with transcript/case/corpus, evidence scope, retention, safety, and cost state |
| `docs/user/deployment.md` | reference_pending_reconciliation | May contain old deployment/workflow assumptions |
| `docs/user/model-setup.md` | reference_pending_reconciliation | Useful setup reference, but not product authority |

Handling rule:

```text
Do not treat legacy user docs as current product behavior until rewritten or explicitly reconciled.
```

---

# Legacy Developer Documentation

| Material | Classification | Reconciliation Needed |
|---|---|---|
| `docs/developer/development.md` | implementation_reference | Useful for setup; not product authority |
| `docs/developer/architecture.md` | reference_pending_reconciliation | Should be checked against Phase 002/003 architecture before implementation use |
| `docs/developer/api-reference.md` | implementation_reference | Describes current API surface; may not match future concept names |
| `docs/developer/aws-operations.md` | reference_pending_reconciliation | Must be reconciled with Cost State / control-plane planning |
| `docs/developer/aws-deployment.md` | reference_pending_reconciliation | Must not restore old workflow assumptions by default |
| `docs/developer/log-redaction.md` | reference_pending_reconciliation | Useful but must be verified against current content-free logging requirements |

---

# Legacy Design Package

| Material | Classification | Reconciliation Path |
|---|---|---|
| `docs/design/01_product_vision_and_scope.md` | reference_pending_reconciliation | Product identity and boundaries superseded where conflicts exist |
| `docs/design/02_system_architecture.md` | reference_pending_reconciliation | Use as implementation reference only after Phase 003 planning |
| `docs/design/03_domain_model.md` | reference_pending_reconciliation | Feed 003-B domain terminology plan |
| `docs/design/04_knowledge_ontology.md` | reference_pending_reconciliation | Feed 003-B and 003-E graph/ontology planning |
| `docs/design/05_data_model_and_schemas.md` | reference_pending_reconciliation | Feed 003-B through 003-D schema planning |
| `docs/design/06_analysis_modules.md` | reference_pending_reconciliation | Feed 003-E lens/contract planning |
| `docs/design/07_prompt_compiler.md` | reference_pending_reconciliation | Feed 003-E prompt/validator planning |
| `docs/design/08_workflow_engine.md` | reference_pending_reconciliation | Feed 003-E and 003-F as implementation reference |
| `docs/design/09_evidence_confidence_and_citations.md` | reference_pending_reconciliation | Feed 003-E evidence/confidence planning |
| `docs/design/10_synthesis_engine.md` | reference_pending_reconciliation | Feed 003-E report/synthesis planning |
| `docs/design/11_ui_ux_design.md` | reference_pending_reconciliation | Feed 003-G UI/report alignment planning |
| `docs/design/14_testing_evaluation_and_safety.md` | reference_pending_reconciliation | Feed 003-E and later evaluation planning |
| `docs/design/16_additional_thoughts.md` | reference_pending_reconciliation | Review for backlog-worthy ideas only |

Handling rule:

```text
The legacy design package is useful source material, but accepted concepts and Phase 002 architecture win on conflict.
```

---

# Existing Planning Backlogs and Phase Files

| Material | Classification | Handling |
|---|---|---|
| `docs/planning/deferred_backlog.md` | reference_pending_reconciliation | Mine for useful deferred items; do not treat as current priority without gate mapping |
| `docs/planning/general_backlog.md` | reference_pending_reconciliation | Reconcile against 002-H backlog before use |
| older `docs/planning/phases/` files outside current 002/003 sequence | historical_or_reference_pending_reconciliation | Keep for provenance unless later superseded or archived |
| `docs/archived/planning/` | historical | Retain as archive/provenance |

---

# Release Documents

| Material | Classification | Handling |
|---|---|---|
| `docs/releases/v1.0.0.md` | historical | Do not rewrite as current status |
| `docs/releases/v0.9.0.md` | historical | Do not rewrite as current status |
| `docs/releases/v0.8.0.md` | historical | Do not rewrite as current status |
| `docs/releases/v0.7.0.md` | historical | Do not rewrite as current status |

Release documents may be cited for historical state, not current product authority.

---

# Implementation and Infrastructure Material

| Material | Classification | Handling |
|---|---|---|
| `backend/` | implementation_reference | Current prototype behavior; must be mapped before broad refactor |
| `frontend/` or UI source directories | implementation_reference | Current UI behavior; must be audited against 002-G/003-G |
| `alembic/` | implementation_reference | Existing schema history; not a current domain authority by itself |
| `scripts/` | implementation_reference | Must be checked for cost-state, logging, and deployment assumptions |
| `Dockerfile*` | implementation_reference | Useful for later deployment planning |
| `.github/dependabot.yml` | implementation_reference | Dependency maintenance config, not deployment workflow authority |
| `.github/pull_request_template.md` | reference_pending_reconciliation | Should later carry gate reminders if PR flow resumes |
| `.github/workflows/` | absent/intentionally_cleared | Do not recreate until workflow replacement gate is satisfied |

---

# Supersession Rules

A legacy document or section is superseded when it conflicts with any of these accepted boundaries:

- product is reflection-first, transcript-enabled, not transcription-only
- audio is ephemeral by default
- transcript/case/corpus scope must be explicit
- hidden account-wide corpus inference is not allowed by default
- retained sensitive artifacts must be owner-scoped
- logs and telemetry must be content-free
- therapeutic/diagnostic frameworks are reasoning references, not clinical authority
- hypotheses are evidence-limited and non-diagnostic
- safety-aware framing overrides ordinary reflection
- cost state is a control-plane concept and must not corrupt jobs
- GitHub Actions workflows remain intentionally cleared until replacement is planned

---

# Reconciliation Actions for Later Groups

| Later Group | Reconciliation Focus |
|---|---|
| 003-B | legacy domain/design/code terminology |
| 003-C | data lifecycle, retention, drafts, deletion, exports |
| 003-D | owner scope, privacy, encryption, log redaction |
| 003-E | analysis modules, prompts, validators, hypotheses, safety, corpus reasoning |
| 003-F | deployment, operations, cost-state control plane, workflow replacement |
| 003-G | UI/report labels, flows, evidence scope, retention/export/safety/cost-state surfaces |

---

# Decision

No historical or legacy material should be deleted during 003-A.

The repository should preserve provenance while routing future implementation planning through current concepts, accepted Phase 002 architecture, and active Phase 003 subgroup outputs.