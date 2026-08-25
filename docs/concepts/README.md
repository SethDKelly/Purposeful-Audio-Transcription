# Concept Design Foundation

## Purpose

This folder is the current conceptual design authority for the conversation analysis application.

The application began from a plausible product idea and then moved quickly into implementation. That produced useful code, but implementation details began to become the design authority.

This folder resets the design from ground zero and now governs refactor planning.

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

| Subphase | Status | Planning Doc |
|---|---|---|
| 002-A — Documentation Authority and Terminology Inventory | Complete | `../planning/phases/002a_documentation_authority_terminology_inventory.md` |
| 002-B — Concept-to-Domain Model Mapping | Next | TBD |
| 002-I — Phase 002 Exit Review and Consolidation | Mandatory gate | TBD |

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

## Next phase

Proceed to:

```text
002-B — Concept-to-Domain Model Mapping
```

Do not begin implementation refactoring until Phase 002 reaches its mandatory exit review and consolidation gate.
