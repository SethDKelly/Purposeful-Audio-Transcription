# Model setup — Bedrock & Transcribe

AWS-only inference for the Relationship Reasoning Engine.

| Service | Role |
|---------|------|
| **Amazon Bedrock** | Module / synthesis LLM (`LLM_PROVIDER=bedrock`) |
| **Amazon Transcribe** | Audio → labeled turns (`TRANSCRIPTION_PROVIDER=transcribe`) |

Historical local stacks (Ollama, Whisper, pyannote) are **removed** from the product. Do not configure them.

## Bedrock

ECS sets `LLM_PROVIDER=bedrock` and `BEDROCK_MODEL_ID` (see `infra/dev/ecs.tf`). Operators need model access in the account/region (`us-east-2`).

Resolution order (first non-empty wins):

| Layer | Location |
|-------|----------|
| Request | API / UI `model` field |
| Module | `model_id` / legacy `ollama_model` alias in module YAML |
| Environment | `BEDROCK_MODEL_ID` / `DEFAULT_OLLAMA_MODEL` (legacy alias if still present in settings) |

Evaluation notes: [../evaluation/llm-evaluation-bedrock.md](../evaluation/llm-evaluation-bedrock.md).

UI model list: `GET /api/models`.

## Amazon Transcribe

Requires `UPLOADS_BUCKET` and IAM for StartTranscriptionJob / S3. Speaker labels become Person A / B turns after ingest.

| Variable | Notes |
|----------|-------|
| `TRANSCRIPTION_PROVIDER` | `transcribe` |
| `UPLOADS_BUCKET` | Temp audio + job output (lifecycle on `temp/`) |
| `TRANSCRIBE_LANGUAGE` | Optional, e.g. `en-US` |

Evaluation notes: [../evaluation/asr-evaluation-transcribe.md](../evaluation/asr-evaluation-transcribe.md).

## Long transcripts

Evidence quotes are summarized in prompts when a transcript exceeds `EVIDENCE_PROMPT_MAX_QUOTES` (default `120`):

```env
EVIDENCE_PROMPT_MAX_QUOTES=120
EVIDENCE_PROMPT_HEAD_QUOTES=80
EVIDENCE_PROMPT_TAIL_QUOTES=40
```

## Related

- [getting-started.md](getting-started.md) · [deployment.md](deployment.md)
- [../developer/aws-operations.md](../developer/aws-operations.md)
