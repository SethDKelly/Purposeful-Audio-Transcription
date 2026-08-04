# Ontology v1 — Canonical Vocabulary

**Status:** Shipped in **v0.7.0**. Complements conceptual design in [../design/04_knowledge_ontology.md](../design/04_knowledge_ontology.md). Phase history: [../archived/planning/phases.md](../archived/planning/phases.md#phase-27--ontology-vocabulary-v1).

## Placement

Machine-readable definitions:

```text
config/ontology/constructs.yaml
config/ontology/relationships.yaml
```

Loader: `backend/core/ontology_registry.py`. Human summary stays in this doc.

Each type needs: **stable ID**, **label**, **description**, optional **confidence ceiling**, optional **aliases**.

## Construct types (minimum)

| ID | Intent |
|----|--------|
| `observation` | Observable utterance/behavior |
| `interpretation` | Inferred meaning beyond observation |
| `emotion` | Affective state |
| `need` | Underlying need |
| `value` | Stated or implied value |
| `belief` | Belief / assumption about self/other/world |
| `narrative` | Storyline the speaker is living in |
| `identity_theme` | Identity-relevant theme |
| `repair_attempt` | Bid to repair rupture |
| `missed_repair` | Repair opportunity missed |
| `escalation_point` | Moment that escalates conflict |
| `deescalation_point` | Moment that de-escalates |
| `interaction_cycle` | Recurring interaction pattern |
| `feedback_loop` | Reinforcing loop |
| `threat_cue` | Cue experienced as threat |
| `safety_cue` | Cue experienced as safety |
| `boundary` | Boundary stated or crossed |
| `assumption` | Unexamined assumption |
| `cognitive_distortion` | Distorted cognition pattern (non-diagnostic framing) |
| `attribution` | Causal attribution |
| `request` | Explicit or implicit request |
| `intervention` | Suggested intervention (non-prescriptive coaching) |
| `uncertainty` | Explicit uncertainty |
| `limitation` | Analysis or evidence limitation |
| `strength` | Relational strength / resource |
| `alternative_explanation` | Competing explanation (may also live on findings) |

## Relationship types (minimum)

| ID | Intent |
|----|--------|
| `supports` | Evidence or construct supports another |
| `contradicts` | Direct conflict |
| `contributes_to` | Causal / contributory link |
| `escalates` | Increases intensity |
| `deescalates` | Decreases intensity |
| `protects` | Protective function |
| `threatens` | Threatens safety/connection |
| `maintains` | Maintains a pattern |
| `repairs` | Repairing link |
| `co_occurs_with` | Co-occurrence without strong causality |
| `alternative_to` | Competing construct/finding |
| `evidence_for` | Quote/evidence supports claim |
| `evidence_against` | Quote/evidence weakens claim |
| `intervention_for` | Intervention targets construct |
| `source_of_uncertainty_for` | Uncertainty source |

## Acceptance

- Canonical types documented here and loadable from config.
- Module specs may reference ontology IDs (`expected_constructs` in v0.7 P4).
- Validation rejects unknown IDs or warns (policy TBD per field).

## Tests

- Ontology YAML/Python model loads.
- Module-declared construct types ⊆ ontology.
- Fixture relationship types ⊆ ontology.
