# Workflow DAG Plan (v1.0) — **Shipped in v1.0**

Replace or extend linear workflow execution with explicit DAG support. Roadmap: [../planning/roadmap_v0.7_to_v1.0.md](../planning/roadmap_v0.7_to_v1.0.md). Engine: `backend/services/workflow_engine.py`, DAG helpers: `backend/core/workflow_dag.py`.

## Goals

- Explicit step dependencies
- Parallel execution groups
- Synthesis gates
- Optional modules
- Retry policies
- Per-step status in UI
- Partial reruns (or planned path)

## Example shape

```yaml
steps:
  - id: observable_wave
    parallel:
      - relationship_conversation_analysis
      - gottman_analysis
      - mediation_analysis

  - id: interpretive_wave
    depends_on:
      - observable_wave
    parallel:
      - cognitive_analysis
      - attachment_interaction_matrix
      - trauma_informed_communication

  - id: synthesis
    depends_on:
      - interpretive_wave
    module: meta_synthesis
```

Linear `modules:` lists remain supported. When `steps` are present, the engine executes topological waves; `modules` may still be listed for API clients.

## Related v1.0 work

| Priority | Note |
|----------|------|
| Dedicated worker | Jobs outlive API request lifecycle |
| Custom workflow builder | Consumes module metadata + DAG validation |
| Bounded parallel modules (v0.6) | Precursor; DAG makes dependencies explicit |

## Acceptance

Dependencies explicit; parallelizable modules concurrent; invalid graphs rejected at validation time (`validate_config` + registry load).
