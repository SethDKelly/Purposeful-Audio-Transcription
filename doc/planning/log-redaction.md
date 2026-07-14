# Log redaction design — CloudWatch / structured logs (P1-3c)

| | |
|---|---|
| **Status** | Implemented (P1-3c on `tier-2-p1-trust-workflows`) |
| **Related** | P1-3c in [implementing.md](implementing.md); [aws-operations.md](../developer/aws-operations.md) |
| **Goal** | Operators can debug runs via correlation IDs without transcript or prompt bodies in CloudWatch |

---

## Problem

AWS Logs Insights queries rely on structured JSON (`LOG_JSON=true`). Failure paths may attach or echo:

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
| Audit events | `transcript.ingest` / `.export` / `.delete` / `.purge` — IDs and enums only |

DB remains the store of record for transcript and `raw_output`; logs only point at IDs.

---

## Implementation

1. **`backend/core/log_sanitize.py`** — `redact_text`, `safe_extra` deny-list
2. **`RedactionFilter`** in `logging_config.py` — scrub denied `extra` keys; truncate oversized messages
3. **Settings** — `LOG_REDACT` optional; auto-on when `LLM_PROVIDER=bedrock` or non-SQLite
4. **Tests** — `tests/test_log_sanitize.py`

### Out of scope for P1-3c

- Encrypting RDS at rest beyond current `storage_encrypted` (already on)
- Redacting Streamlit UI display
- Changing DB schema retention (P1-3e — `TRANSCRIPT_RETENTION_DAYS`)

---

## Acceptance

- [x] Central sanitize helper + filter wired in `configure_logging`
- [x] Unit tests for sanitize helper / filter
- [x] Ops doc updated with “what you will / won’t see”
- [ ] Dev deploy spot-check: failed module run line has IDs, not dialogue (when AWS next resumed)

---

## Operator guidance

Treat `/rre/dev/api` as **sensitive**, restrict IAM console access, and prefer Insights queries filtered by `module_run_id` rather than free-text search on message bodies.
