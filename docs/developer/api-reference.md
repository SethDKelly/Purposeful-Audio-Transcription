# API reference

Base URL: ALB DNS (AWS) or `http://127.0.0.1:8000` (local tooling). Interactive OpenAPI: `/docs`.

When `API_KEY` is set, send header `X-API-Key: <value>` on protected routes. Public: `/`, `/api/live`, `/api/health`, `/docs`, `/openapi.json`.

Errors return a generic message plus `request_id` (also echoed as `X-Request-ID`).

## Health and models

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/live` | Liveness (ECS/ALB) — prefer this for probes |
| `GET` | `/api/health` | Bedrock, Transcribe, database status |
| `GET` | `/api/models` | List configured Bedrock model IDs |
| `GET` | `/api/models/ollama` | Deprecated alias of `/api/models` |

## Transcripts

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/transcripts` | Ingest transcript JSON body |
| `POST` | `/api/transcripts/upload` | Upload `.txt` file |
| `GET` | `/api/transcripts/{id}` | Full bundle (speakers, turns, quotes) |
| `DELETE` | `/api/transcripts/{id}` | Cascade delete transcript + runs |
| `PATCH` | `/api/transcripts/{id}/speakers` | Update display names |
| `PATCH` | `/api/transcripts/{id}/turns` | Edit/exclude turns for analysis |
| `POST` | `/api/transcripts/{id}/evidence/rebuild` | Regenerate quote IDs from current turns |
| `POST` | `/api/transcripts/{id}/ready` | Mark `analysis_ready` (or `skip_review`) |
| `GET` | `/api/transcripts/{id}/workflow-runs` | Runs for transcript |

Workflows require `analysis_ready` unless `AUTO_MARK_TRANSCRIPT_READY` is set (pytest only).

### Ready body

```json
{ "skip_review": false }
```

## Modules

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/modules` | List modules (includes `expected_constructs`) |
| `POST` | `/api/modules/{id}/run` | Run single module |
| `GET` | `/api/module-runs/{id}` | Module run status + telemetry / warnings |
| `POST` | `/api/modules/{id}/stream` | Stream raw LLM output |
| `GET` | `/api/purposes` | Deprecated alias for modules |

Module run responses may include:

- `validation_warnings` — soft construct coverage (does not fail the run)
- `telemetry` — latency, tokens, estimated cost, finding/construct counts
- `parsed_output.construct_coverage` — expected / found / missing / rate

## Workflows

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/workflows` | List workflows |
| `POST` | `/api/workflows/{id}/run` | Run workflow (`background` optional) |
| `GET` | `/api/workflow-runs/{id}` | Run status + module runs + `telemetry_summary` |
| `GET` | `/api/workflow-runs/{id}/synthesis` | Synthesis report |

### Run workflow body

```json
{
  "transcript_id": "uuid",
  "model": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
  "background": false
}
```

`background` is optional. When omitted, the API uses the workflow’s `default_background`, then `WORKFLOW_BACKGROUND_DEFAULT`. If the workflow still would run synchronously with more modules than `WORKFLOW_SYNC_MODULE_LIMIT` (default 6), it is forced to background; an explicit `"background": false` over that limit returns **400**.

## Exploration

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/workflow-runs/{id}/exploration/findings` | Indexed findings |
| `GET` | `/api/workflow-runs/{id}/exploration/findings/{key}` | Drill-down (`module_id:F001`) |
| `GET` | `/api/workflow-runs/{id}/exploration/cross-module` | Agreement / tension |
| `GET` | `/api/workflow-runs/{id}/exploration/knowledge-graph` | Constructs graph |
| `POST` | `/api/workflow-runs/{id}/exploration/ask` | Follow-up Q&A |
| `POST` | `/api/exploration/compare` | Compare run IDs |

### Ask body

```json
{
  "question": "Why was repair identified?",
  "model": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
  "finding_key": "relationship_conversation_analysis:F001"
}
```

## Audio

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/transcribe` | Audio → labeled transcript (Amazon Transcribe) |
| `POST` | `/api/process` | Audio + workflow → full pipeline |

Optional form field `num_speakers` (1–10) hints diarization when the speaker count is known. Omit for auto-detect.

## Examples

```powershell
# Liveness
curl http://<alb>/api/live

# Ingest (with API key when configured)
curl -X POST http://<alb>/api/transcripts `
  -H "Content-Type: application/json" `
  -H "X-API-Key: $env:API_KEY" `
  -d '{"raw_text":"Person A: Hi\nPerson B: Hello","source_type":"paste"}'

# Mark ready
curl -X POST http://<alb>/api/transcripts/<id>/ready `
  -H "Content-Type: application/json" `
  -H "X-API-Key: $env:API_KEY" `
  -d '{"skip_review": true}'

# Run quick_review
curl -X POST http://<alb>/api/workflows/quick_review/run `
  -H "Content-Type: application/json" `
  -H "X-API-Key: $env:API_KEY" `
  -d '{"transcript_id":"<id>"}'
```

## Schemas

Response models in `backend/api/schemas.py`. Module output schema: `backend/schemas/module_output_v1.py`. Ontology: `config/ontology/`.

See also [../design/05_data_model_and_schemas.md](../design/05_data_model_and_schemas.md) · [../architecture/ontology_v1.md](../architecture/ontology_v1.md).
