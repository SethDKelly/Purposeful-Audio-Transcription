# Log redaction design — CloudWatch / structured logs (P1-3c)

Design only. **Do not change logging code until this note is accepted and a follow-up implementation PR is opened.**

| | |
|---|---|
| **Status** | Draft |
| **Related** | P1-3c in [implementing.md](implementing.md); [aws-operations.md](../developer/aws-operations.md) |
| **Goal** | Operators can debug runs via correlation IDs without transcript or prompt bodies in CloudWatch |

---

## Problem

AWS Logs Insights queries rely on structured JSON (`LOG_JSON=true`). Today, failure paths may still attach or echo:

- Raw LLM output (`raw_output` on module runs — also stored in DB)
- Prompt / evidence index snippets in debug contexts
- Pasted transcript text if ever logged at INFO/ERROR

CloudWatch retention (`log_retention_days`) does not equal “safe for sensitive dialogue.” Redaction must be **default-on** for AWS and available locally.

---

## What must never appear in CloudWatch

| Class | Examples |
|-------|----------|
| Transcript body | `raw_text`, turn text, uploaded file contents |
| Evidence quotes | Full `Q00n` quote strings in log `message` or `extra` |
| Prompt payloads | Compiled system/user messages, prior module JSON dumps |
| LLM raw responses | Full model completion text |
| Secrets | `DATABASE_URL`, `HF_TOKEN`, API keys, connection strings |

## What may appear

| Field | Notes |
|-------|--------|
| `request_id`, `workflow_run_id`, `module_run_id` | Correlation |
| `module_id`, `workflow_id`, `model_id` | Diagnostics |
| `error_type`, `event` | Already used |
| Counts / lengths | e.g. `quote_count=12`, `raw_output_chars=4096` |
| Truncated hashes | e.g. `prompt_template_hash` (already stored) |
| Validation issue **codes** | e.g. “missing evidence_quote_ids” — not the quote text |

DB remains the store of record for transcript and `raw_output`; logs only point at IDs.

---

## Implementation sketch (future PR)

1. **Central helper** — e.g. `backend/core/log_sanitize.py`:
   - `redact_text(value, *, max_len=0) -> str` → `"[redacted len=N]"` or empty
   - `safe_extra(**kwargs)` — drop/deny known keys (`raw_text`, `raw_output`, `messages`, `prompt`, `content`)
2. **Logger adapter / filter** — optional `logging.Filter` that scrubs `record.msg` / `record.__dict__` keys on AWS (`LLM_PROVIDER=bedrock` or `LOG_REDACT=true`).
3. **Explicit allowlist for `extra=`** — module_runner / workflow_engine only pass correlation + enums.
4. **Settings** — `log_redact: bool = True` when not sqlite-local-dev; override with `LOG_REDACT=false` for local debugging.
5. **Tests** — assert a deliberate `logger.error(..., extra={"raw_output": "SECRET"})` path never emits `SECRET` when redaction on.

### Out of scope for P1-3c

- Encrypting RDS at rest beyond current `storage_encrypted` (already on)
- Redacting Streamlit UI display
- Changing DB schema retention (P1-3e)

---

## Acceptance

- [ ] Grep of `backend/` logging calls: no transcript/prompt bodies at INFO+
- [ ] Unit tests for sanitize helper
- [ ] Dev deploy: failed module run log line contains `module_run_id` and error type, not dialogue text
- [ ] Ops doc updated with “what you will / won’t see”

---

## Interim operator guidance

Until implemented: treat `/rre/dev/api` as **sensitive**, restrict IAM console access, and prefer Insights queries filtered by `module_run_id` rather than free-text search on message bodies.
