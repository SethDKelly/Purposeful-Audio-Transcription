# Phase 002 — Concept-to-Architecture Refactor Roadmap

## Status

Active.

This phase translates the accepted concept foundation into architecture and refactor planning.

It is not an implementation phase.

---

# Purpose

Phase 002 maps accepted concepts to current implementation areas, identifies terminology drift, defines architecture plans, and creates a safe refactor sequence.

The goal is to prevent the old implementation from reasserting product authority while preserving useful prototype work.

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

# Required subgroups

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
| 002-I — Phase 002 Exit Review and Consolidation | Next mandatory gate | Consolidate Phase 002 and authorize or block Phase 003 |

---

# Mandatory exit gate

Phase 002 cannot be considered complete until `002-I` is complete.

The exit review must consolidate:

- accepted architecture decisions
- terminology changes
- stale/superseded docs
- deferred questions
- refactor sequence
- implementation readiness result

---

# Current accepted outputs

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

---

# Non-goals

Phase 002 does not:

- modify production behavior
- implement encryption
- change data schemas
- rewrite prompts
- build new UI
- restore GitHub Actions
- deploy infrastructure

Those belong after the Phase 002 exit review.

---

# Exit criteria

Phase 002 is complete only when:

- all subgroups 002-A through 002-H are complete
- 002-I exit review is complete
- accepted architecture decisions are consolidated
- stale documentation has been updated, marked historical, or placed in a migration list
- the next phase is explicitly named
- implementation readiness is decided yes/no
