# API reference

Base URL: `http://127.0.0.1:8000` (default). Interactive docs: `/docs`.

When `API_KEY` is set in `.env`, send header `X-API-Key: <value>` on protected routes. Public: `/`, `/api/health`, `/docs`, `/openapi.json`.

## Health and models

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Bedrock, Transcribe, database status |
| `GET` | `/api/live` | Liveness (ECS/ALB) |
| `GET` | `/api/models` | List configured Bedrock model IDs |
| `GET` | `/api/models/ollama` | Deprecated alias of `/api/models` |

## Transcripts

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/transcripts` | Ingest transcript JSON body |
| `POST` | `/api/transcripts/upload` | Upload `.txt` file |
| `GET` | `/api/transcripts/{id}` | Full bundle (speakers, turns, quotes) |
| `PATCH` | `/api/transcripts/{id}/speakers` | Update display names |
| `GET` | `/api/transcripts/{id}/workflow-runs` | Completed runs for transcript |

## Modules

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/modules` | List modules |
| `POST` | `/api/modules/{id}/run` | Run single module |
| `GET` | `/api/module-runs/{id}` | Module run status |
| `POST` | `/api/modules/{id}/stream` | Stream raw LLM output |
| `GET` | `/api/purposes` | Deprecated alias for modules |

## Workflows

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/workflows` | List workflows |
| `POST` | `/api/workflows/{id}/run` | Run workflow (`background` optional) |
| `GET` | `/api/workflow-runs/{id}` | Run status + module runs |
| `GET` | `/api/workflow-runs/{id}/synthesis` | Synthesis report |

### Run workflow body

```json
{
  "transcript_id": "uuid",
  "model": "llama3.2",
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
  "model": "llama3.2",
  "finding_key": "relationship_conversation_analysis:F001"
}
```

## Audio

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/transcribe` | Audio → labeled transcript (Amazon Transcribe) |
| `POST` | `/api/process` | Audio + workflow → full pipeline |

Optional form field `num_speakers` (1–10) hints diarization when the speaker count is known. Omit for auto-detect.

`TranscribeResponse` includes `speaker_count`, `speaker_labels`, and `diarization_applied` when diarization runs.

## Examples

```powershell
# Health
curl http://127.0.0.1:8000/api/health

# Ingest
curl -X POST http://127.0.0.1:8000/api/transcripts `
  -H "Content-Type: application/json" `
  -d '{"raw_text":"Person A: Hi\nPerson B: Hello","source_type":"paste"}'

# Run quick_review
curl -X POST http://127.0.0.1:8000/api/workflows/quick_review/run `
  -H "Content-Type: application/json" `
  -d '{"transcript_id":"<id>","model":"llama3.2"}'
```

## Schemas

Response models in `backend/api/schemas.py`. Module output schema: `backend/schemas/module_output_v1.py`.

See also [../design/05_data_model_and_schemas.md](../design/05_data_model_and_schemas.md).
