# Phase 002 — Concept-to-Architecture Refactor Roadmap

## Status

Complete.

This phase translated the accepted concept foundation into architecture and refactor planning.

It was not an implementation phase.

---

# Purpose

Phase 002 mapped accepted concepts to current implementation areas, identified terminology drift, defined architecture plans, and created a safe refactor sequence.

The goal was to prevent the old implementation from reasserting product authority while preserving useful prototype work.

---

# Inputs

Primary authority:

```text
docs/concepts/
```

Key accepted decisions:

- product identity
- conceptual boundary
- data lifecycle
- retention/encryption posture
- hypothesis-aware reflection boundary
- therapeutic reflection language
- safety boundary
- personal operating model
- cost state
- future enterprise posture
- refactor readiness

---

# Completed subgroups

| Subphase | Status | Purpose |
|---|---|---|
| 002-A — Documentation Authority and Terminology Inventory | Complete | Identify current authority surfaces, stale wording, and terminology mapping |
| 002-B — Concept-to-Domain Model Mapping | Complete | Map accepted concepts to current entities, schemas, services, and gaps |
| 002-C — Data Lifecycle and Retention Architecture Plan | Complete | Translate lifecycle/retention decisions into architecture requirements |
| 002-D — Privacy Boundary and Encryption Architecture Plan | Complete | Define owner scope, access, encryption, redaction, deletion, and corpus-scope architecture |
| 002-E — Analysis Boundary, Hypothesis, and Safety Architecture Plan | Complete | Map non-diagnostic hypothesis reasoning, corpus-aware confidence, and safety override into schemas/prompts/validators |
| 002-F — Cost State and Personal Deployment Architecture Plan | Complete | Map sleep/wake and personal-mode cost posture into deployment architecture |
| 002-G — UI/UX Concept Alignment Plan | Complete | Align user-facing concepts, labels, flows, and report language |
| 002-H — Refactor Backlog, Sequencing, and Acceptance Gates | Complete | Build the implementation backlog and gates |
| 002-I — Phase 002 Exit Review and Consolidation | Complete | Consolidate Phase 002 and authorize Phase 003 |

---

# Mandatory exit gate result

Phase 002 completed its mandatory exit review:

```text
002-I — Phase 002 Exit Review and Consolidation
```

Exit decision:

```text
Phase 002 passes exit review.
Phase 002 is complete.
Phase 003 is authorized with explicit scope.
Broad implementation rewrite remains blocked.
```

---

# Accepted outputs

| Subphase | Outputs |
|---|---|
| 002-A | `docs/planning/inventories/002a_documentation_authority_inventory.md`, `docs/planning/inventories/002a_terminology_inventory.md` |
| 002-B | `docs/planning/inventories/002b_concept_domain_model_mapping.md`, `docs/planning/inventories/002b_domain_gap_register.md` |
| 002-C | `docs/planning/architecture/002c_data_lifecycle_retention_architecture_plan.md`, `docs/planning/inventories/002c_artifact_retention_matrix.md` |
| 002-D | `docs/planning/architecture/002d_privacy_boundary_encryption_architecture_plan.md`, `docs/planning/inventories/002d_artifact_privacy_encryption_matrix.md`, `docs/planning/inventories/002d_corpus_reasoning_scope_rules.md` |
| 002-E | `docs/planning/architecture/002e_analysis_boundary_hypothesis_safety_architecture_plan.md`, `docs/planning/inventories/002e_analysis_boundary_contracts.md`, `docs/planning/inventories/002e_validation_gate_matrix.md` |
| 002-F | `docs/planning/architecture/002f_cost_state_personal_deployment_architecture_plan.md`, `docs/planning/inventories/002f_cost_state_transition_matrix.md`, `docs/planning/inventories/002f_personal_deployment_control_requirements.md` |
| 002-G | `docs/planning/architecture/002g_ui_ux_concept_alignment_plan.md`, `docs/planning/inventories/002g_ui_ux_language_matrix.md`, `docs/planning/inventories/002g_user_flow_alignment_inventory.md` |
| 002-H | `docs/planning/architecture/002h_refactor_backlog_sequencing_acceptance_gates.md`, `docs/planning/inventories/002h_refactor_backlog.md`, `docs/planning/inventories/002h_acceptance_gate_matrix.md` |
| 002-I | `docs/planning/architecture/002i_phase_002_exit_review_consolidation.md`, `docs/planning/inventories/002i_phase_002_output_inventory.md`, `docs/planning/inventories/002i_phase_003_authorized_scope.md` |

---

# Consolidated gates carried forward

Phase 002 carries forward these gates for Phase 003 and later implementation planning:

- documentation authority gate
- terminology drift gate
- domain mapping gate
- retention gate
- deletion cascade gate
- privacy boundary gate
- encryption baseline gate
- log redaction gate
- export boundary gate
- analysis boundary gate
- hypothesis boundary gate
- confidence calibration gate
- safety override gate
- corpus reasoning gate
- corpus staleness gate
- reflection point gate
- report scope gate
- UI language gate
- cost state gate
- job-safe shutdown gate
- workflow replacement gate
- evaluation gate
- regression gate
- release readiness gate

---

# Non-goals preserved

Phase 002 did not:

- modify production behavior
- implement encryption
- change data schemas
- rewrite prompts
- build new UI
- restore GitHub Actions
- deploy infrastructure

Those remain governed by Phase 003 and later gate decisions.

---

# Exit criteria result

Phase 002 exit criteria are satisfied:

- all subgroups 002-A through 002-H are complete
- 002-I exit review is complete
- accepted architecture decisions are consolidated
- stale documentation handling is identified for Phase 003
- the next phase is explicitly named
- implementation readiness is decided

---

# Next authorized phase

```text
Phase 003 — Foundation Refactor Planning and Authority Cleanup
```

Recommended next subgroup:

```text
003-A — Documentation Authority Cleanup and Historical Material Reconciliation
```
