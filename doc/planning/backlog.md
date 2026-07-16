# Backlog — Index

Optional and deferred work that is **not** on the active **v0.7–v1.0** path.

| | |
|---|---|
| **Active plan** | [implementing.md](implementing.md) |
| **Roadmap** | [roadmap_v0.7_to_v1.0.md](roadmap_v0.7_to_v1.0.md) |
| **Deferred catalog** | **[future_considerations.md](future_considerations.md)** — preserve wording for items moved off the active path |
| **Completed** | [completed.md](completed.md) |

**When to promote:** Only when the current release priorities are complete (or blocked) and the item addresses a **validated user need**. Add it to [implementing.md](implementing.md) under the correct release priority.

### Deferred from active roadmap

Items below historically lived in this file. They remain valuable but are **not** part of the v0.7–v1.0 stabilization sequence. Full tables (original wording preserved where possible) live in [future_considerations.md](future_considerations.md).

Reconsider after the reasoning engine, ontology, graph persistence, case model, and durable workflow engine are stable.

## Quick pointers (see future_considerations for detail)

| Theme | Examples |
|-------|----------|
| Ingest | Multi-file audio stitch (was P2-A), async Transcribe, local ASR research |
| Analysis breadth | Additional prompts/modules, ontology-driven prompt gen, Haiku routing |
| UI | React SPA, rich graph viz, mobile-native |
| Collab / SaaS | Full professional portal, multi-tenant, billing |
| Platform | Helm, prod account, Celery queue, Prometheus |

## Explicitly out of scope

- Modifying **MinneAnalytics** in aws-backbone
- Runtime Hugging Face downloads in AWS
- Hardcoded per-model code branches
- Graph database backend
- Multi-user SaaS unless requirements change
- Local Whisper/Ollama product runtime

## Superseded notes

- Local dual-path / Compose-as-primary / air-gapped clinic P0 — superseded by AWS-only + VPC Stage B (see [completed.md](completed.md)).
- Analysis performance items already shipped in v0.6 (bounded parallel modules, lean outputs, Bedrock prompt cache) stay in [completed.md](completed.md); further speed work waits on **v0.7 P6** telemetry.
