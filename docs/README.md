# Documentation Index

## Current documentation authority

The current design authority is the concept foundation:

```text
concept design
→ product philosophy
→ domain model
→ security/privacy model
→ analysis philosophy
→ implementation architecture
→ code
```

Start here:

| Area | Document |
|---|---|
| Concept foundation | [concepts/README.md](concepts/README.md) |
| Phase 001 acceptance | [concepts/021_concept_acceptance_summary.md](concepts/021_concept_acceptance_summary.md) |
| Refactor readiness | [concepts/022_refactor_readiness_decision.md](concepts/022_refactor_readiness_decision.md) |
| Planning index | [planning/README.md](planning/README.md) |
| Phase sequence | [planning/phases/README.md](planning/phases/README.md) |
| Completed Phase 002 roadmap | [planning/phases/002_concept_to_architecture_refactor_roadmap.md](planning/phases/002_concept_to_architecture_refactor_roadmap.md) |
| Phase 002 exit review | [planning/phases/002i_phase_exit_review_consolidation.md](planning/phases/002i_phase_exit_review_consolidation.md) |
| Mandatory exit gate policy | [planning/phase_exit_gate_policy.md](planning/phase_exit_gate_policy.md) |

## Current plan status

Phase 002 is complete.

The next authorized phase is:

```text
Phase 003 — Foundation Refactor Planning and Authority Cleanup
```

The recommended next subgroup is:

```text
003-A — Documentation Authority Cleanup and Historical Material Reconciliation
```

## Product identity

| Name | Current role |
|---|---|
| Purposeful Audio Transcription | Historical repository name / legacy shell |
| Secure Conversation Analysis and Reflection System | Current concept-level product identity |
| Relationship Reasoning Engine (RRE) | Internal analysis-engine identity |
| Audio transcription | Input capability, not product identity |

## User documentation

Existing user documentation remains useful, but may contain legacy product names or workflow assumptions. It should be reconciled during Phase 003 and later refactor phases.

| Document | Description |
|---|---|
| [user/getting-started.md](user/getting-started.md) | Legacy getting-started path |
| [user/user-guide.md](user/user-guide.md) | Legacy application guide |
| [user/deployment.md](user/deployment.md) | AWS deployment pointers |
| [user/model-setup.md](user/model-setup.md) | Bedrock / Transcribe setup |

## Developer documentation

Developer documentation remains useful as implementation reference material, but it is not product authority when it conflicts with accepted concept decisions.

| Document | Description |
|---|---|
| [developer/development.md](developer/development.md) | Development setup |
| [developer/architecture.md](developer/architecture.md) | Existing service/data-flow reference |
| [developer/api-reference.md](developer/api-reference.md) | Existing REST API summary |
| [developer/aws-operations.md](developer/aws-operations.md) | Existing AWS operation notes |
| [developer/aws-deployment.md](developer/aws-deployment.md) | Existing AWS architecture notes |
| [developer/log-redaction.md](developer/log-redaction.md) | Existing redaction design |

## Design package

The older design package is reference material. Phase 003 should determine which parts are accepted, superseded, renamed, or deferred for implementation refactor planning.

| Document | Topic |
|---|---|
| [design/01_product_vision_and_scope.md](design/01_product_vision_and_scope.md) | Legacy product vision / scope |
| [design/03_domain_model.md](design/03_domain_model.md) | Existing domain model |
| [design/04_knowledge_ontology.md](design/04_knowledge_ontology.md) | Existing ontology |
| [design/09_evidence_confidence_and_citations.md](design/09_evidence_confidence_and_citations.md) | Evidence model reference |
| [design/11_ui_ux_design.md](design/11_ui_ux_design.md) | Existing UI reference |
| [design/14_testing_evaluation_and_safety.md](design/14_testing_evaluation_and_safety.md) | Testing/safety reference |

## Planning

| Document | Description |
|---|---|
| [planning/README.md](planning/README.md) | Planning authority index |
| [planning/phases/](planning/phases/) | Phase sequence |
| [planning/architecture/](planning/architecture/) | Phase architecture plans |
| [planning/inventories/](planning/inventories/) | Phase inventories |
| [planning/deferred_backlog.md](planning/deferred_backlog.md) | Existing deferred backlog reference |
| [planning/general_backlog.md](planning/general_backlog.md) | Existing general backlog reference |
| [archived/planning/](archived/planning/) | Historical planning archive |

## Releases

Release documents remain historical. They should not be edited to match current status unless explicitly marked as retrospective notes.

| Document | Description |
|---|---|
| [releases/v1.0.0.md](releases/v1.0.0.md) | Historical release note |
| [releases/v0.9.0.md](releases/v0.9.0.md) | Historical release note |
| [releases/v0.8.0.md](releases/v0.8.0.md) | Historical release note |
| [releases/v0.7.0.md](releases/v0.7.0.md) | Historical release note |

## Status rule

Living indexes, contributor instructions, and planning docs must not carry independently maintained stale status. Current status should point to the phase sequence and mandatory exit review for the current phase.
