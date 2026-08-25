# Purposeful Audio Transcription

This repository currently contains the prototype/reference implementation for the working product concept:

```text
Secure Conversation Analysis and Reflection System
```

The original repository name, **Purposeful Audio Transcription**, is historical. Audio transcription remains an input capability, but the accepted product concept is private, evidence-linked conversation analysis and reflection over transcripts.

## Current status

The repository is in concept-to-architecture refactor planning.

The current design authority is:

```text
docs/concepts/
```

Active planning is:

```text
docs/planning/phases/002_concept_to_architecture_refactor_roadmap.md
```

GitHub Actions workflows have been intentionally cleared. New workflows should be introduced only after the refactor roadmap defines the new pipeline and gate model.

## Product concept

The product is a secure conversation analysis and reflection system that uses evidence-linked transcripts, psychological and behavioral reflection lenses, confidence calibration, and longitudinal case memory to help a user examine communication patterns without diagnosing people or making clinical/legal determinations.

## Entry points

| Area | Start here |
|---|---|
| Concept authority | [docs/concepts/README.md](docs/concepts/README.md) |
| Planning authority | [docs/planning/README.md](docs/planning/README.md) |
| Phase sequence | [docs/planning/phases/README.md](docs/planning/phases/README.md) |
| Documentation index | [docs/README.md](docs/README.md) |
| Phase exit gate policy | [docs/planning/phase_exit_gate_policy.md](docs/planning/phase_exit_gate_policy.md) |

## Important boundary

The application may use therapeutic, psychological, behavioral, and diagnostic-framework-informed concepts as evidence-limited reasoning references. It must not present itself as a clinician, therapist, diagnostic tool, treatment system, adjudicator, or workplace surveillance tool.

## Legacy implementation

The existing implementation remains valuable as a prototype/reference implementation. It should be mapped to the accepted concepts before broad code refactoring resumes.

## License

See repository license file.
