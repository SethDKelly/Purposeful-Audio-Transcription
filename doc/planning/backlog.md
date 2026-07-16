# Backlog — Future & Nice-to-Have

Optional enhancements **not** on the active path in [implementing.md](implementing.md). Completed work: [completed.md](completed.md).

**Scope rule:** Backlog items improve UX, research velocity, or future AWS ops. They do **not** block core workflow value. Local Whisper/Ollama/Compose packaging is **out of scope** (product is AWS-only).

**When to promote:** Move an item to [implementing.md](implementing.md) only when Tier 1–2 work for the current milestone is complete and the item addresses a **validated user need**.

---

## ~~Local development~~ (superseded)

Removed. Laptop work is edit + `pytest` (SQLite) + Deploy to AWS. See [../developer/development.md](../developer/development.md).

---

## UI & frontend

### React frontend (Phase S)

Exploration-first SPA consuming existing APIs only — no duplicated business logic.

| Item | Notes |
|------|-------|
| **Stack** | Vite + React + TypeScript |
| **MVP pages** | Transcript list, workflow run status, report, explore (drill-down + ask) |
| **Auth** | `X-API-Key` header from env |
| **Non-goals (R1)** | Full Streamlit parity (audio ingest, full workflow picker); mobile-native layout |

**Effort:** 2–3 weeks

| Item | Notes | Effort |
|------|-------|--------|
| **Knowledge graph UI richness** | Beyond basic Streamlit Mermaid; interactive layout, filtering | 1–2 weeks |
| **Mobile-native layout** | Responsive Streamlit or React | Medium |
| **Full Streamlit feature parity in React** | Audio ingest, full workflow picker | Large |

*Counterfactual exploration presets may land in Tier 3 (P2-O5) before React.*

---

## ~~Audio & transcription (local / research)~~ (superseded)

Whisper / pyannote local experiments are discontinued. ASR is Amazon Transcribe only. Timing/VAD ideas that need raw audio timing may be revisited against Transcribe output later if needed.

---

## Analysis & ontology (speculative / incremental)

Core ontology work is **P2-O** in [implementing.md](implementing.md).

| Item | Notes | Effort |
|------|-------|--------|
| **Ontology-driven prompt generation** | Generate prompts from constructs + workflow goals instead of static files | Large |
| **Module `inference:` YAML block** | Per-module temperature, `num_predict` without code changes | 1–2 days |
| **Eval script: construct coverage** | `scripts/eval_construct_coverage.py` — % runs with populated constructs | 1 day |
| **Coaching action plan export** | May land in P2-R7 — short actionable markdown distinct from coach summary | 1–2 days |
| **Additional analysis prompts** | Escalation/repair mapping, emotional needs gaps, etc. ([archived/backlog-analysis-suite.md](../archived/backlog-analysis-suite.md)) | Per prompt |
| **Multi-conversation report pack** | A single conversation bounds what analysis can say. Let users export each workflow report, then upload several reports (same partnership / theme over time or across sessions) for a deeper cross-conversation synthesis — patterns, progression, contradictions, and guidance that one run cannot support. **Relates to P2-P** (cases & longitudinal) in [implementing.md](implementing.md): this can be a lighter import path (report artifacts only, without re-ingesting every transcript) or an early slice that feeds case comparison later. Prefer structured exports (JSON/md findings) over raw paste so meta-synthesis stays attributable. | Large |

---

## Professional & collaboration

| Item | Notes | Effort |
|------|-------|--------|
| **Collaborative review** | Multi-participant context, shared agreements, helpful/unhelpful on findings | Large |
| **Professional mode (full)** | Case files, session series, supervision notes, treatment planning — overlaps P2-P | Large |
| **Finding feedback UI (extended)** | Rich notes, tagging — basic version may land in P2-R | 2–3 days |
| **Redaction pass improvements** | PII patterns, configurable rules before export — basic log redaction is P1-3 | 3–5 days |

---

## Platform & deployment

AWS images and Terraform exist. Remaining items:

| Item | Notes | Effort |
|------|-------|--------|
| **HTTPS / TLS on ALB** | Dev ALB is **HTTP :80 only** today (diagram in aws-deployment.md is aspirational). Add ACM cert (custom domain or temporary cert), HTTPS listener, HTTP→HTTPS redirect; keep UI→API on Cloud Map HTTP inside VPC. Pair with enabling `API_KEY` in Secrets Manager + P2-R2 UI header. Optional: IP allowlist / VPN-only. **Promote to implementing before sharing sensitive session audio outside a trusted LAN.** | 2–4 days |
| **Helm chart** | K8s ingress if org move off ECS | Deferred |
| **Production AWS account** | `prod-github-deploy` in aws-backbone | Deferred |
| **Distributed job queue** | Celery/Redis multi-host — prefer single ECS worker service first (above) | Large |
| **Multi-user SaaS** | Accounts, billing, RBAC | Out of product scope unless requirements change |

---

## ~~Secure & air-gapped operation (local / clinic)~~ (superseded)

On-prem Ollama/Whisper air-gap guides are out of scope. AWS VPC Stage B + in-account Bedrock/Transcribe is the data residency model.

---

---

## Analysis performance (speed without raising model spend)

Independent transcript modules already run with **bounded parallelism** (`WORKFLOW_MODULE_CONCURRENCY`, default 3 on AWS; SQLite forces 1). Meta-synthesis stays sequential. **Shipped on branch:** leaner module outputs (`bedrock_max_tokens=8192`, fewer retries, short/empty `raw_markdown_report` guidance) and **Bedrock prompt caching** on shared framework + evidence prefix (`BEDROCK_PROMPT_CACHE`, TTL `1h` for Sonnet 4.5).

If wall-clock timeouts persist after that, prefer these before spending more on larger models:

| Item | Notes | Effort |
|------|-------|--------|
| **Haiku / cheaper model routing for light modules** | Keep Sonnet for hard lenses + meta; A/B first (`llm-evaluation-bedrock.md`). Same or lower $. | 2–4 days + eval |
| **Per-module `max_tokens` / inference YAML** | Smaller modules finish sooner; overlaps backlog `inference:` block. Too low → more retries. | 1–2 days |
| **Meta handoff v2 (findings/constructs only)** | Shrink synthesis prompt beyond dropping `raw_markdown_report`. | 2–3 days |
| **Module duration telemetry / SLOs** | Know which lenses dominate wall clock before further tuning. | 1–2 days |
| **Raise concurrency carefully (4–5)** | Only after health + Bedrock throttle stay green under parallel=3. | Config + soak |

**Avoid:** unbounded parallel Sonnet; Opus-on-everything; raising `bedrock_max_tokens` for “speed.”

---

## Infrastructure & observability (incremental)

Structured logging and CloudWatch are done ([completed.md](completed.md)).

**Already shipped (do not re-backlog):** workflow **background** runs — `background=true` / `default_background` / sync module limit → `WorkflowJobService` ThreadPool on the API task; UI polls run status. Gaps below are durability, cancel, and ASR parity — not “make workflows async.”

### Dependency chain (jobs / long-running work)

```text
1. Async / background Transcribe     (ingest must finish before a workflow starts)
        ↓
2. Basic workflow cancel (P2-R6 in implementing.md) → advanced cancel (below)
        ↓
3. Dedicated ECS worker service      (if API health flaps under Bedrock load)
        ↓
4. Distributed job queue             (only if dedicated worker is not enough)
```

| Item | Notes | Effort |
|------|-------|--------|
| **Async / background Transcribe** | Submit job → poll/status (+ UI progress). Needed so long audio matches workflow submit/poll UX. Poll wait default is already 3600s. **Depends on:** nothing. **Blocks:** clean long-session ingest → analyze UX. | 3–5 days |
| **Workflow run cancellation (advanced)** | Cancel in-flight background workflow with partial cleanup. **Depends on:** P2-R6 basic cancel. Stronger with (3) dedicated worker so cancel is not limited to in-process threads. | 2–3 days |
| **Run telemetry dashboard** | Aggregate module durations, failure rates, model used | 1 week |
| **Prometheus metrics endpoint** | Optional `/metrics` for operators | 2–3 days |

---

## Developer experience

| Item | Notes | Effort |
|------|-------|--------|
| **Module scaffolding CLI** | `scripts/new_module.py` — YAML + prompt stub | 1 day |
| **mypy / typed CI** | Optional strictness beyond ruff F401/E9 | 2–3 days |
| **Dedicated ECS worker service** | Run Bedrock (and eventually Transcribe poll) off the ALB-facing API task if health flaps return under load. **Depends on:** validating need after clear-before-deploy + multi-worker mitigations. **Enables:** stronger cancel + room for durable job handoff. | 1–2 weeks |

*Pre-commit Tier 1–2 + `validate_config` are done on the Tier 2 branch ([implementing.md](implementing.md) P1-5d). Golden LLM fixtures and pinned lockfiles remain P1-5a/b. Distributed queue stays under Platform & deployment and still assumes a worker path first.*

---

## Research & evaluation

| Item | Notes | Effort |
|------|-------|--------|
| **Benchmark suite** | Standard transcripts + expected finding shapes | 1 week |
| **A/B module prompt versions** | Compare module YAML versions on same transcript | 1 week |
| **Human eval rubric** | Structured reviewer scoring for report quality | Docs + tooling |

---

## Superseded local-first priorities

| Item | Notes |
|------|-------|
| Native Windows ML stack as primary path | Demoted — use AWS or local Docker |
| Local Ollama production tuning | Local dev only |
| Local Docker Compose as primary deploy | Optional dev convenience |
| Air-gapped clinic deploy as near-term P0 | AWS VPC no-egress is cloud equivalent |

---

## Long-term vision (strategic, not scheduled)

- Cross-transcript case-level progress and theme evolution over time (→ P2-P when promoted)
- Module customization: include/exclude modules, depth, tone, output format (→ P2-Q)
- Rich knowledge graph UI with construct-driven navigation
- Ontology-driven prompt generation (speculative — static prompts + metadata remain default)

**Enduring assets:** domain model, ontology, evidence model, confidence model, workflow design, structured data, synthesis logic — not any single prompt file.

---

## Explicitly out of scope

- Modifying **MinneAnalytics** in aws-backbone
- Runtime Hugging Face downloads in AWS deploy (target state)
- Hardcoded per-model code branches
- Graph database backend
- Multi-user SaaS unless requirements change

---

## How items graduate

1. **Tier 1–2 work** for the current release milestone is complete.
2. The item addresses a **validated user need** (not speculative scope).
3. **Platform tier** supports it (e.g. do not prioritize GPU-only features before cloud ASR exists).

When promoting: add to [implementing.md](implementing.md) with a tier (1–3) and remove or annotate the item here.
