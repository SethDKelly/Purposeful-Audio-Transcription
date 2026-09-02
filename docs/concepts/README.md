# Concept Design Foundation

## Purpose

This folder is the current conceptual design authority for the conversation analysis application.

The application began from a plausible product idea and then moved quickly into implementation. That produced useful code, but implementation details began to become the design authority.

This folder resets the design from ground zero and governs refactor planning.

## Core premise

The application is a secure conversation analysis and reflection system.

It analyzes transcripts, which may be derived from recordings, using evidence-based psychological, behavioral, therapeutic, cognitive, and relational lenses. It supports reflection and longitudinal understanding.

The application may consider psychological or diagnostic-framework-informed hypotheses as reflection contexts, but it must not diagnose, label, adjudicate, or claim clinical certainty.

## Authority order

```text
Concept design
→ Product philosophy
→ Domain model
→ Security/privacy model
→ Analysis philosophy
→ Implementation architecture
→ Code
```

Current planning authority flows through:

```text
docs/concepts/
→ Phase 002 exit review and architecture outputs
→ Phase 003 overview and accepted subgroup outputs
→ reconciled implementation plans
→ code
```

## Foundation read order

1. `000_concept_reset_charter.md`
2. `001_product_premise.md`
3. `002_concept_design_method.md`
4. `003_concept_catalog.md`
5. `004_concept_composition.md`
6. `005_security_privacy_retention_concepts.md`
7. `006_cost_availability_concepts.md`
8. `007_analysis_philosophy.md`
9. `008_future_enterprise_transition.md`
10. `009_refactor_mapping.md`
11. `010_open_questions.md`

## Phase 001 decision closure

| Subphase | Status | Decision Docs |
|---|---|---|
| 001-A — Product Identity, Naming, and Conceptual Boundary | Accepted | `011_product_identity_decision.md`, `012_concept_boundary_decision.md` |
| 001-B — Data Lifecycle, Retention, and Encryption Decisions | Accepted | `013_data_lifecycle_decision.md`, `014_retention_and_encryption_decision.md` |
| 001-C — Hypothesis-Aware Reflection and Non-Diagnostic Boundary | Accepted | `015_hypothesis_reflection_boundary.md`, `016_therapeutic_lens_language_decision.md`, `017_safety_boundary_decision.md` |
| 001-D — Personal Operating Model, User Role, and Cost State | Accepted | `018_personal_operating_model_decision.md`, `019_cost_state_decision.md`, `020_future_enterprise_posture_decision.md` |
| 001-E — Concept Acceptance and Refactor Readiness | Complete | `021_concept_acceptance_summary.md`, `022_refactor_readiness_decision.md` |

## Phase 002 refactor roadmap

Phase 002 is complete and consolidated.

Key outputs:

| Area | Planning Doc |
|---|---|
| Phase 002 roadmap | `../planning/phases/002_concept_to_architecture_refactor_roadmap.md` |
| Phase 002 exit review | `../planning/phases/002i_phase_exit_review_consolidation.md` |
| Phase 003 authorization | `../planning/inventories/002i_phase_003_authorized_scope.md` |

## Phase 003 foundation refactor planning

Phase 003 is active.

| Subphase | Status | Planning Doc |
|---|---|---|
| 003-A — Documentation Authority Cleanup and Historical Material Reconciliation | Complete | `../planning/phases/003a_documentation_authority_cleanup_historical_material_reconciliation.md` |
| 003-B — Domain Terminology and Concept Mapping Implementation Plan | Complete | `../planning/phases/003b_domain_terminology_concept_mapping_implementation_plan.md` |
| 003-C — Data Lifecycle / Retention Foundation Implementation Plan | Complete | `../planning/phases/003c_data_lifecycle_retention_foundation_implementation_plan.md` |
| 003-D — Privacy Boundary / Encryption Baseline Implementation Plan | Complete | `../planning/phases/003d_privacy_boundary_encryption_baseline_implementation_plan.md` |
| 003-E — Analysis Boundary / Validation Implementation Plan | Complete | `../planning/phases/003e_analysis_boundary_validation_implementation_plan.md` |
| 003-F — Cost-State Control Plane Implementation Plan | Complete | `../planning/phases/003f_cost_state_control_plane_implementation_plan.md` |
| 003-G — UI/Report Alignment Implementation Plan | Next | TBD |
| 003-H — Phase 003 Exit Review and Consolidation | Mandatory gate | TBD |

## Current working identity

```text
Secure Conversation Analysis and Reflection System
```

## Current terminology defaults

| Area | Decision |
|---|---|
| Product concept | Secure Conversation Analysis and Reflection System |
| Repository shell | Purposeful Audio Transcription |
| Internal engine | Relationship Reasoning Engine / RRE |
| Input capability | Audio transcription |
| Therapeutic concepts | Therapeutic reflection lenses |
| Diagnostic frameworks | Reasoning references, not clinical authority |
| User model | Personal owner/operator |
| Cost posture | Cost State; aggressive sleep/wake in personal mode |
| Enterprise | Future policy/deployment layer |
| Workflow/module execution | Reflection Run / Reflection Lens product language with implementation aliases |
| Report guidance | Reflection Point, not recommendation/intervention by default |
| Multi-transcript reasoning | Case Evidence Corpus or explicit selected transcript scope |
| Lifecycle and retention | Audio ephemeral; drafts temporary; saved/case transcripts durable until deletion; derived artifacts inherit evidence-basis retention |
| Privacy and encryption | Owner-scoped retained artifacts; content-free logs; infrastructure encryption baseline; application/field-level encryption target |
| Analysis validation | Explicit analysis scope; evidence-linked output; bounded hypotheses; structured safety posture; corpus lineage and staleness gates |
| Cost-state control plane | Explicit owner-visible sleep/wake; job-safe shutdown; content-free power events; GitHub Actions restoration gated |

## Next phase

Proceed to:

```text
003-G — UI/Report Alignment Implementation Plan
```

Do not begin broad implementation refactoring until Phase 003 reaches its mandatory exit review and consolidation gate.
