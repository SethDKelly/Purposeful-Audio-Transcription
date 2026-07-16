# Architecture overview

High-level map of the RRE codebase. Deep design specs live in [../design/](../design/). Runtime is **AWS only**.

**Current release:** **v0.7.0**. Roadmap: [../planning/roadmap_v0.7_to_v1.0.md](../planning/roadmap_v0.7_to_v1.0.md). Next: [../architecture/structured_persistence_plan.md](structured_persistence_plan.md) (v0.8).

## System diagram

```text
┌─────────────────────────────────────────────────────────────┐
│  Streamlit UI (ECS)                                          │
│  Ingest · Prepare (Ready) · Analyze · Report · Explore       │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP + optional X-API-Key
┌──────────────────────────▼──────────────────────────────────┐
│  FastAPI (ECS)                                               │
│  /transcripts · /workflows · /modules · /transcribe          │
│  Generic errors + request_id · /api/live + /api/health       │
└──────────────────────────┬──────────────────────────────────┘
                           │
     ┌─────────────────────┼─────────────────────┐
     ▼                     ▼                     ▼
 TranscriptService   WorkflowEngine      ExplorationService
 EvidenceIndex       ModuleRunner        SynthesisEngine
 OntologyRegistry    PromptCompiler      WorkflowJobService
     ┌─────────────────┴─────────────────┐
     ▼                                     ▼
 AmazonTranscribeProvider              BedrockProvider
   (S3 uploads bucket)                   (Claude + usage)
                           │
                     RDS PostgreSQL (SQLAlchemy + Alembic)
```

## Core services

| Service | Role |
|---------|------|
| `AmazonTranscribeProvider` | Audio → S3 → Transcribe job → labeled turns |
| `TranscriptService` | Parse, ingest, prepare (edit/exclude/ready), store quotes |
| `EvidenceIndexService` | Assign `Q001…` quote IDs; rebuild after turn edits |
| `OntologyRegistry` | Canonical construct/relationship vocabulary + aliases |
| `BedrockProvider` | LLM chat; records token/cache usage for telemetry |
| `ModuleRegistry` / `WorkflowRegistry` | YAML definitions; ontology validation on load |
| `PromptCompiler` | Build messages from framework + module + evidence |
| `ModuleRunner` | Run → parse JSON → validate → soft coverage warnings → retry |
| `ModuleOutputValidator` | Hard schema/evidence rules + soft `expected_constructs` coverage |
| `WorkflowEngine` / `WorkflowJobService` | Parallel transcript modules + background runs |
| `SynthesisEngine` | Cross-module report |
| `ExplorationService` | Drill-down, compare, follow-up Q&A |

## Domain layer

`backend/domain/` — Pydantic models: `Transcript`, `Finding`, `ModuleRun` (with `validation_warnings`, `telemetry`), `WorkflowRun` (with `telemetry_summary`), `SynthesisReport`, etc.

## Persistence

- **RDS PostgreSQL** on AWS
- **SQLite** in pytest only
- **Alembic** migrations in `alembic/versions/` (through `004_run_telemetry`)

## Configuration

| Path | Purpose |
|------|---------|
| `config/modules/*.yaml` | Module metadata, `expected_constructs`, prompt file |
| `config/workflows/*.yaml` | Module sequences, tone, `default_background` |
| `config/ontology/` | Construct + relationship vocabulary |
| `config/prompts/*.md` | LLM prompt templates |
| `config/framework/` | Shared instructions and output schema |
| `infra/dev/` | Terraform / ECS env |

## Extension points

### Add a module

1. Prompt in `config/prompts/`
2. YAML in `config/modules/` with `expected_constructs` from the ontology
3. Add to a workflow YAML or `POST /api/modules/{id}/run`

### Add a workflow

1. `config/workflows/my_workflow.yaml`
2. List modules; set `meta_synthesis: true` when ending with synthesis

### Add a golden fixture

1. `tests/fixtures/golden_transcripts/<ID>_<slug>/` with required files
2. See [../planning/golden_transcript_fixtures.md](../planning/golden_transcript_fixtures.md)

## Auth, errors, logging

- `APIKeyMiddleware` — shared `API_KEY` (Secrets Manager on ECS); UI sends `X-API-Key`
- Generic user-facing API errors + `request_id` (JSON body and header)
- JSON logs + redaction on AWS (`LOG_JSON`, `LOG_REDACT`)
- Module/workflow telemetry events for cost and latency

## Related

- [../planning/aws-deployment.md](../planning/aws-deployment.md)
- [../architecture/ontology_v1.md](../architecture/ontology_v1.md)
- [../product/transcript_preparation_workspace.md](../product/transcript_preparation_workspace.md)
- [../design/02_system_architecture.md](../design/02_system_architecture.md)
- [../design/08_workflow_engine.md](../design/08_workflow_engine.md)
