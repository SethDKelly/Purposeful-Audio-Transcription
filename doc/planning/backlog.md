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
| **Helm chart** | K8s ingress if org move off ECS | Deferred |
| **Production AWS account** | `prod-github-deploy` in aws-backbone | Deferred |
| **Distributed job queue** | Celery/Redis for multi-worker | Large |
| **Multi-user SaaS** | Accounts, billing, RBAC | Out of product scope unless requirements change |

---

## ~~Secure & air-gapped operation (local / clinic)~~ (superseded)

On-prem Ollama/Whisper air-gap guides are out of scope. AWS VPC Stage B + in-account Bedrock/Transcribe is the data residency model.

---

---

## Infrastructure & observability (incremental)

Structured logging and CloudWatch are done ([completed.md](completed.md)).

| Item | Notes | Effort |
|------|-------|--------|
| **Run telemetry dashboard** | Aggregate module durations, failure rates, model used | 1 week |
| **Prometheus metrics endpoint** | Optional `/metrics` for operators | 2–3 days |
| **Workflow run cancellation (advanced)** | Cancel in-flight background workflow with partial cleanup — basic cancel may land in P2-R | 2–3 days |

---

## Developer experience

| Item | Notes | Effort |
|------|-------|--------|
| **Module scaffolding CLI** | `scripts/new_module.py` — YAML + prompt stub | 1 day |
| **Pre-commit hooks** | ruff, mypy optional | 1 day |

*Golden LLM fixtures and pinned lockfiles are in [implementing.md](implementing.md) P1-5.*

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
