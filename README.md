# Purposeful Audio Transcription

This repository currently contains the prototype/reference implementation for the working product concept:

```text
Secure Conversation Analysis and Reflection System
```

The original repository name, **Purposeful Audio Transcription**, is historical. Audio transcription remains an input capability, but the accepted product concept is private, evidence-linked conversation analysis and reflection over transcripts.

## Current status

The repository has completed concept-to-architecture refactor planning.

Current design authority remains:

```text
docs/concepts/
```

Completed architecture/refactor planning:

```text
docs/planning/phases/002_concept_to_architecture_refactor_roadmap.md
```

The current active phase is:

```text
Phase 003 — Foundation Refactor Planning and Authority Cleanup
```

Current subgroup status:

```text
003-A complete
003-B next
```

GitHub Actions workflows have been intentionally cleared. New workflows should be introduced only after the refactor roadmap and cost-state/control-plane planning define the new pipeline and gate model.

## Product concept

The product is a secure conversation analysis and reflection system that uses evidence-linked transcripts, psychological and behavioral reflection lenses, confidence calibration, and longitudinal case memory to help a user examine communication patterns without diagnosing people or making clinical/legal determinations.

## Entry points

| Area | Start here |
|---|---|
| Concept authority | [docs/concepts/README.md](docs/concepts/README.md) |
| Planning authority | [docs/planning/README.md](docs/planning/README.md) |
| Phase sequence | [docs/planning/phases/README.md](docs/planning/phases/README.md) |
| Active Phase 003 overview | [docs/planning/phases/003_foundation_refactor_planning_authority_cleanup.md](docs/planning/phases/003_foundation_refactor_planning_authority_cleanup.md) |
| Completed 003-A summary | [docs/planning/phases/003a_documentation_authority_cleanup_historical_material_reconciliation.md](docs/planning/phases/003a_documentation_authority_cleanup_historical_material_reconciliation.md) |
| Completed Phase 002 roadmap | [docs/planning/phases/002_concept_to_architecture_refactor_roadmap.md](docs/planning/phases/002_concept_to_architecture_refactor_roadmap.md) |
| Phase 002 exit review | [docs/planning/phases/002i_phase_exit_review_consolidation.md](docs/planning/phases/002i_phase_exit_review_consolidation.md) |
| Documentation index | [docs/README.md](docs/README.md) |
| Phase exit gate policy | [docs/planning/phase_exit_gate_policy.md](docs/planning/phase_exit_gate_policy.md) |

## Important boundary

The application may use therapeutic, psychological, behavioral, and diagnostic-framework-informed concepts as evidence-limited reasoning references. It must not present itself as a clinician, therapist, diagnostic tool, treatment system, adjudicator, or workplace surveillance tool.

## Legacy implementation

The existing implementation remains valuable as a prototype/reference implementation. It should be mapped to the accepted concepts before broad code refactoring resumes.

Legacy user, developer, design, release, planning, code, and infrastructure materials remain reference, historical, or implementation-reference material unless explicitly reconciled by Phase 003 or a later accepted phase.

## License

See repository license file.
