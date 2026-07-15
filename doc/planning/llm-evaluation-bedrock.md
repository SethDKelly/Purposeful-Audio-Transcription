# LLM evaluation note — Amazon Bedrock (AWS-1b)

Formal record of the LLM approach chosen for RRE AWS dev after the P0-AWS-7e Quick Review burn-in.

| | |
|---|---|
| **Status** | Accepted for v0.5.0 AWS pivot |
| **Date** | 2026-07-12 |
| **Environment** | Account `521018312783`, `us-east-2` |
| **Provider** | `LLM_PROVIDER=bedrock` via `BedrockProvider` (Converse API) |

---

## Decision

Use **Amazon Bedrock Converse** with an **Anthropic Claude Sonnet** inference profile as the AWS default LLM. Keep **Ollama** for local development only.

| Choice | Value |
|--------|-------|
| Default model | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` (US inference profile) |
| API | `bedrock-runtime` `Converse` (non-streaming for module runs) |
| Structured output | Converse `outputConfig` JSON schema (`module_output_v1`) + prompt/repair fallback |
| Max tokens (dev) | `16384` (`bedrock_max_tokens`) |
| Client read timeout | 600s (module JSON can be slow on first invoke) |

---

## Why Converse + Sonnet

1. **Same product contract** — modules already expect `module_output_v1` JSON; Converse returns text that `OutputParser` already handles (fences, aliases, enum coercion).
2. **No host model ops** — no Ollama sidecar, GPU, or model volume on ECS.
3. **Cost / quality balance** — Sonnet is the middle tier; adequate for interpersonal structured analysis without Opus cost on every module.
4. **Inference profile** — Claude 4.x on Bedrock requires an inference profile ID (`us.…`), not a raw foundation-model ID alone.
5. **Data path** — inference stays in the AWS boundary for this model class (no Anthropic public API). Account still needs Anthropic FTU form + Marketplace enablement once per account.

---

## Burn-in evidence (Quick Review)

| Check | Result |
|-------|--------|
| Health | `llm_provider=bedrock`, `llm_available=true` |
| Workflow | `quick_review` |
| Modules | `relationship_conversation_analysis`, `nvc_analysis`, `bias_epistemic_quality` — all **completed** |
| Model | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` |

### Issues found and mitigated in product code

| Issue | Mitigation |
|-------|------------|
| Marketplace subscribe on first invoke | ECS task role `aws-marketplace:Subscribe` / `ViewSubscriptions` (via Bedrock) |
| Converse read timeout (~60s default) | Botocore `read_timeout=600` |
| Sparse constructs / `source_id` aliases | `_coerce_raw_module_payload` before Pydantic validate |
| Unknown `relationship_type` (e.g. `reinforces`) | Alias map + default `co_occurs_with` |
| Prose outside JSON / markdown-after-JSON instructions | Framework prompts + compiler require JSON-only; markdown only in `raw_markdown_report`; Bedrock structured output when available |

---

## Structured JSON approach

**Chosen:** Bedrock Converse structured JSON schema (`outputConfig`) for Claude Sonnet 4.5+,
with prompt-constrained JSON + repair loop as fallback when schema mode is unavailable.

Rationale:

- Constrained decoding removes prose-only / markdown-outside-JSON failures that break workflows.
- Repair loop already exists in `module_runner` (`module_run_max_retries`) for coercion/validation misses.
- Prompt + parser still required for field aliases and business-rule validation.

---

## IAM (task role)

Required for invoke path:

- `bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream`
- Foundation model + inference profile ARNs
- `bedrock:GetFoundationModel`, `GetInferenceProfile`, list APIs (health)
- Marketplace subscribe actions when called via Bedrock (first enablement)

See `infra/dev/iam.tf`.

---

## Latency / cost (qualitative)

| Workflow | Modules | Expectation |
|----------|---------|-------------|
| Quick Review | 3 | Minutes, not seconds; first module often longest |
| Full MVP | 4 + meta | Longer; prefer `background=true` |
| Full multidisciplinary | 12 + meta | Batch / background only |

Track CloudWatch `module.run.*` durations before publishing SLOs.

---

## Local vs AWS

| | Local | AWS |
|--|-------|-----|
| Provider | Ollama | Bedrock |
| Model config | `DEFAULT_OLLAMA_MODEL` / module `ollama_model` | `BEDROCK_MODEL_ID` |
| Same | Prompt compiler, validators, workflows, UI |

---

## Open items

- [ ] Haiku A/B for cheaper modules after quality bar is set
- [ ] Formal token/cost sampling from CloudWatch + Billing (include cacheRead/Write tokens)
- [x] Meta-synthesis / long suites: compact prior outputs + structured JSON
- [x] JSON-only prompts (no markdown-after-JSON) after parse failures in burn-in
- [x] Leaner generation: `bedrock_max_tokens=8192`, fewer retries, short/empty `raw_markdown_report`
- [x] Bedrock prompt caching on shared framework + evidence prefix (TTL 1h on Sonnet 4.5)
