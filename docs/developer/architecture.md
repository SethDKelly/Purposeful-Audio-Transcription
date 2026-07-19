# Architecture overview

High-level map of the RRE codebase. Deep design specs live in [../design/](../design/). Runtime is **AWS only**.

**Current release:** **v1.0.0**. Completed history: [../archived/planning/phases.md](../archived/planning/phases.md). Active: [../planning/phases/](../planning/phases/) (v1.1 operational hardening).

## System diagram

```text
┌─────────────────────────────────────────────────────────────┐
│  Streamlit UI (ECS)                                          │
│  Ingest · Prepare · Cases · Analyze · Custom · Report · Explore │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP + optional X-API-Key
┌──────────────────────────▼──────────────────────────────────┐
│  FastAPI (ECS) — queues workflow jobs when worker enabled    │
│  /transcripts · /cases · /workflows · /modules · /transcribe │
└──────────────────────────┬──────────────────────────────────┘
                           │
     ┌─────────────────────┼─────────────────────┐
     ▼                     ▼                     ▼
 TranscriptService   WorkflowEngine      ExplorationService
 CaseService         ModuleRunner        SynthesisEngine
 EvidenceIndex       PromptCompiler      LongitudinalSynthesis
 OntologyRegistry    WorkflowJobService  FindingFeedback
 SafetyRiskScanner   CustomWorkflow      TranscriptLength
     ┌─────────────────┴─────────────────┐
     ▼                                     ▼
 AmazonTranscribeProvider              BedrockProvider
                           │
                     RDS PostgreSQL
                           │
              ECS Worker (RRE_PROCESS=worker)
              polls CREATED → runs modules
```

## Core services

| Service | Role |
|---------|------|
| `AmazonTranscribeProvider` | Audio → S3 → Transcribe job → labeled turns |
| `TranscriptService` | Parse, ingest, prepare (edit/exclude/ready), store quotes |
| `CaseService` | Cases CRUD; assign transcripts with session label/date |
| `EvidenceIndexService` | Quote IDs; balanced sampling when over prompt budget |
| `TranscriptLengthService` | Length assessment / truncation strategy |
| `SafetyRiskScanner` | High-risk cue scan for safety mode |
| `OntologyRegistry` | Canonical construct/relationship vocabulary + aliases |
| `BedrockProvider` | LLM chat; records token/cache usage for telemetry |
| `ModuleRegistry` / `WorkflowRegistry` | YAML definitions; DAG steps; ephemeral custom workflows |
| `PromptCompiler` | Build messages; safety framing when `safety_mode` |
| `ModuleRunner` | Run → parse → validate → persist normalized rows |
| `WorkflowEngine` / `WorkflowJobService` | Linear or DAG waves; cancel/timeout; queue for worker |
| `CustomWorkflowService` | Validate and register ephemeral suites |
| `GraphMergeService` | Cross-module construct deduplication |
| `ConvergenceScoringService` | Deterministic construct convergence scores |
| `StructuredGraphService` | Normalized inventory + synthesis handoff |
| `LongitudinalSynthesisService` | Cross-session synthesis for a case |
| `SynthesisEngine` | Cross-module report (structured inventory when available) |
| `ExplorationService` | Drill-down, compare runs/transcripts, follow-up Q&A |

## Domain layer

`backend/domain/` — Pydantic models: `Transcript`, `Finding`, `Construct`, `ConstructRelationship`, `ModuleRun` (with `validation_warnings`, `telemetry`), `WorkflowRun` (with `telemetry_summary`, `cancel_requested`, `attempt_count`, `safety_mode`), `SynthesisReport`, etc.

## Persistence

- **RDS PostgreSQL** on AWS
- **SQLite** in pytest only
- **Alembic** migrations in `alembic/versions/` (through `011_safety_mode`)
- **Normalized tables:** `findings`, `constructs`, `construct_relationships` (+ evidence/source junctions)
- **Cases / feedback / jobs:** `cases`; `finding_feedback`; workflow job control + `safety_mode`
- Repositories: `FindingRepository`, `ConstructRepository`, `ConstructRelationshipRepository`, `CaseRepository`, `FindingFeedbackRepository`, `WorkflowRunRepository`


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
2. See [../evaluation/golden_transcript_fixtures.md](../evaluation/golden_transcript_fixtures.md)

## Auth, errors, logging

- `APIKeyMiddleware` — shared `API_KEY` (Secrets Manager on ECS); UI sends `X-API-Key`
- Generic user-facing API errors + `request_id` (JSON body and header)
- JSON logs + redaction on AWS (`LOG_JSON`, `LOG_REDACT`)
- Module/workflow telemetry events for cost and latency

## Related

- [aws-deployment.md](aws-deployment.md)
- [../architecture/ontology_v1.md](../architecture/ontology_v1.md)
- [../product/transcript_preparation_workspace.md](../product/transcript_preparation_workspace.md)
- [../design/02_system_architecture.md](../design/02_system_architecture.md)
- [../design/08_workflow_engine.md](../design/08_workflow_engine.md)
