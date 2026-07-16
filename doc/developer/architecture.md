# Architecture overview

High-level map of the RRE codebase. Deep design specs live in [../design/](../design/). Runtime is **AWS only**.

**Roadmap (v0.7→v1.0):** evolve into a structured relationship reasoning engine — [../planning/roadmap_v0.7_to_v1.0.md](../planning/roadmap_v0.7_to_v1.0.md). Near-term plans: [../architecture/ontology_v1.md](../architecture/ontology_v1.md), [structured_persistence_plan.md](structured_persistence_plan.md), [workflow_dag_plan.md](workflow_dag_plan.md).

## System diagram

```text
┌─────────────────────────────────────────────────────────────┐
│  Streamlit UI (ECS)                                          │
│  Ingest · Prepare · Analyze · Report · Explore               │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP (ui/api_client.py → ALB)
┌──────────────────────────▼──────────────────────────────────┐
│  FastAPI (ECS)                                               │
│  /transcripts · /workflows · /modules · /transcribe          │
└──────────────────────────┬──────────────────────────────────┘
                           │
     ┌─────────────────────┼─────────────────────┐
     ▼                     ▼                     ▼
 TranscriptService   WorkflowEngine      ExplorationService
 EvidenceIndex       ModuleRunner        SynthesisEngine
                     PromptCompiler      WorkflowJobService
     ┌─────────────────┴─────────────────┐
     ▼                                     ▼
 AmazonTranscribeProvider              BedrockProvider
   (S3 uploads bucket)                   (Claude)
                           │
                     RDS PostgreSQL (SQLAlchemy + Alembic)
```

## Core services

| Service | Role |
|---------|------|
| `AmazonTranscribeProvider` | Audio → S3 → Transcribe job → labeled turns |
| `TranscriptService` | Parse, ingest, store speakers, turns, quotes |
| `EvidenceIndexService` | Assign `Q001…` quote IDs with context |
| `BedrockProvider` | LLM chat for modules / synthesis / explore |
| `ModuleRegistry` / `WorkflowRegistry` | YAML definitions |
| `PromptCompiler` | Build messages from framework + module + evidence |
| `ModuleRunner` | Run → parse JSON → validate → retry |
| `WorkflowEngine` / `WorkflowJobService` | Sequential + background runs |
| `SynthesisEngine` | Cross-module report |
| `ExplorationService` | Drill-down, compare, follow-up Q&A |

## Domain layer

`backend/domain/` — Pydantic models: `Transcript`, `Finding`, `ModuleRun`, `WorkflowRun`, `SynthesisReport`, etc.

## Persistence

- **RDS PostgreSQL** on AWS
- **SQLite** in pytest only
- **Alembic** migrations in `alembic/versions/`

## Configuration

| Path | Purpose |
|------|---------|
| `config/modules/*.yaml` | Module metadata, prompt file, model override |
| `config/workflows/*.yaml` | Module sequences, tone, `default_background` |
| `config/prompts/*.md` | LLM prompt templates |
| `config/framework/` | Shared instructions and output schema |
| `infra/dev/` | Terraform / ECS env |

## Extension points

### Add a module

1. Prompt in `config/prompts/`
2. YAML in `config/modules/`
3. Add to a workflow YAML or `POST /api/modules/{id}/run`

### Add a workflow

1. `config/workflows/my_workflow.yaml`
2. List modules; set `meta_synthesis: true` when ending with synthesis

## Auth and logging

- `APIKeyMiddleware` — optional `X-API-Key`
- JSON logs + redaction on AWS (`LOG_JSON`, `LOG_REDACT`)

## Related

- [../planning/aws-deployment.md](../planning/aws-deployment.md)
- [../design/02_system_architecture.md](../design/02_system_architecture.md)
- [../design/08_workflow_engine.md](../design/08_workflow_engine.md)
