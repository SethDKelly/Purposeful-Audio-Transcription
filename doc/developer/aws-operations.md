# AWS operations — RRE dev

CloudWatch log groups for the dev stack:

| Service | Log group |
|---------|-----------|
| API | `/rre/dev/api` |
| UI | `/rre/dev/ui` |

Structured JSON logs (`LOG_JSON=true`) include correlation fields:

| Field | Source |
|-------|--------|
| `request_id` | `X-Request-ID` header or generated per HTTP request |
| `workflow_run_id` | Active workflow run context |
| `module_run_id` | Active module run context |
| `module_id` | Module being executed |
| `error_type` | Exception class or failure category |
| `event` | Semantic event name (e.g. `module.run.failed`) |

## CloudWatch Logs Insights queries

Run in **Logs Insights** against `/rre/dev/api`.

### Failed module runs (last hour)

```text
fields @timestamp, module_id, error_type, workflow_run_id, module_run_id, message
| filter event = "module.run.failed"
| sort @timestamp desc
| limit 50
```

### JSON parse failures

```text
fields @timestamp, module_id, module_run_id, workflow_run_id, retry_count, message
| filter event = "module.run.parse_error"
| sort @timestamp desc
| limit 50
```

### Trace a request by ID

```text
fields @timestamp, event, module_id, workflow_run_id, module_run_id, error_type, message
| filter request_id = "YOUR-REQUEST-UUID"
| sort @timestamp asc
```

### Failed workflows

```text
fields @timestamp, workflow_id, run_id, error_type, message
| filter event = "workflow.run.failed"
| sort @timestamp desc
| limit 50
```

### LLM errors

```text
fields @timestamp, module_id, module_run_id, model_id, message
| filter error_type = "LLMError"
| sort @timestamp desc
| limit 50
```

## Bedrock dev settings

| Variable | ECS value (dev) |
|----------|-----------------|
| `LLM_PROVIDER` | `bedrock` |
| `BEDROCK_MODEL_ID` | e.g. `anthropic.claude-3-5-sonnet-20241022-v2:0` |

Ensure the ECS task role includes `bedrock:InvokeModel` and `bedrock:GetFoundationModel` (see `infra/dev/iam.tf`).

## Pause / resume

See [infra/dev/README.md](../../infra/dev/README.md).
