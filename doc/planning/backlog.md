# Backlog — Nice-to-have & deferred enhancements

Items here are **not** on the critical or important path in [implementation_plan.md](implementation_plan.md). The project has **pivoted to AWS dev deployment** — see [aws-deployment.md](aws-deployment.md).

**Scope rule:** Backlog items are **optional** — they improve UX, local dev comfort, research velocity, or alternate deployment targets but do not block AWS dev, Bedrock/Transcribe migration, or core workflow value.

**Priority within this backlog:** ordered roughly by value vs effort. Pull items into the implementation plan only when they address a **validated need** and P0–P1 for the current milestone is complete.

---

## Local development (optional)

| Item | Notes | Effort |
|------|-------|--------|
| **Local Docker Compose** | `api`, `streamlit`, optional Ollama profile — laptop dev only | 1 week |
| **Windows troubleshooting guide** | DLL, WinError 10055, diarization skip reasons | 1–2 days |
| **Ollama `num_ctx` / temperature tuning** | Local Ollama only; AWS uses Bedrock | 1 day |
| **Air-gapped local deployment** | Superseded by AWS VPC no-egress for cloud; optional for offline clinics | 3–5 days |

---

## UI & frontend

| Item | Notes | Effort |
|------|-------|--------|
| **React frontend (Phase S)** | Vite + React + TypeScript SPA; API-only; explore-first MVP | 2–3 weeks |
| **Knowledge graph UI richness** | Beyond basic Streamlit Mermaid; interactive layout, filtering | 1–2 weeks |
| **Mobile-native layout** | Responsive Streamlit or React | Medium |
| **Full Streamlit feature parity in React** | Audio ingest, diarization progress, full workflow picker | Large |

---

## Audio & transcription (local / research)

Superseded in **cloud** by Amazon Transcribe (see implementation plan P1-1). Worthwhile for local quality experiments or research, not deploy blockers.

| Item | Notes | Effort |
|------|-------|--------|
| **M2 UI polish** | Streamlit progress for diarize → transcribe; fixture audio validation | 2–3 days |
| **M2.5 — Word-level alignment** | `word_timestamps=True` + per-word speaker assignment | 3–5 days |
| **Timing analysis** | Pauses, interruptions, overlap duration metrics | 1 week |
| **Interruption detection** | Heuristic or model-based; caution on tone/emotion inference | 1 week |
| **Channel-based speaker split** | Stereo with one speaker per channel (no diarization) | 2–3 days |
| **VAD preprocessing** | Voice activity detection before diarization on noisy audio | 3–5 days |
| **torchcodec experiment** | In-process decode with ffmpeg CLI fallback — Linux only; not recommended as primary | 2–3 days |

---

## Analysis & ontology (speculative / incremental)

Core ontology work is **P2-O** in the implementation plan. Items below are incremental or research-oriented.

| Item | Notes | Effort |
|------|-------|--------|
| **Ontology-driven prompt generation** | Generate prompts from constructs + workflow goals instead of static files | Large |
| **Module `inference:` YAML block** | Per-module temperature, `num_predict` without code changes | 1–2 days |
| **Eval script: construct coverage** | `scripts/eval_construct_coverage.py` — % runs with populated constructs | 1 day |
| **Coaching action plan export** | Short actionable markdown distinct from coach summary | 1–2 days |
| **Additional analysis prompts** | Escalation/repair mapping, emotional needs gaps, etc. (see [archived/backlog-analysis-suite.md](../archived/backlog-analysis-suite.md)) | Per prompt |

---

## Professional & collaboration

| Item | Notes | Effort |
|------|-------|--------|
| **Collaborative review** | Multi-participant context, shared agreements, helpful/unhelpful on findings | Large |
| **Professional mode (full)** | Case files, session series, supervision notes, treatment planning — overlaps P2-P | Large |
| **Finding feedback UI (extended)** | Rich notes, tagging — basic version may land in P2-R | 2–3 days |
| **Redaction pass improvements** | PII patterns, configurable rules before export — basic log redaction is P1-3 | 3–5 days |

---

## Platform & deployment (non-AWS)

| Item | Notes | Effort |
|------|-------|--------|
| **Helm chart** | K8s ingress, secrets, PVC for clinic/org deploys | 1 week |
| **Offline model bake in CI** | Image with pre-accepted HF models; no runtime download — less relevant once Transcribe/Bedrock | 1 week |
| **SQLCipher / TDE options** | Encrypted SQLite or PostgreSQL TDE for regulated environments | 1 week |
| **Distributed job queue** | Celery/Redis for multi-worker deployments | Large |
| **Multi-user SaaS** | Accounts, billing, RBAC | Out of product scope unless requirements change |

---

## Infrastructure & observability (incremental)

Structured logging and CloudWatch are **P0-AWS-3** in the implementation plan. Below are operator extras.

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

*Golden LLM fixtures and pinned lockfiles moved to implementation plan **P1-5**.*

---

## Research & evaluation

| Item | Notes | Effort |
|------|-------|--------|
| **Benchmark suite** | Standard transcripts + expected finding shapes | 1 week |
| **A/B module prompt versions** | Compare module YAML versions on same transcript | 1 week |
| **Human eval rubric** | Structured reviewer scoring for report quality | Docs + tooling |

---

## How items graduate to the implementation plan

Move an item from this backlog when:

1. **P0–P1 work** for the current release milestone is complete, and
2. The item addresses a **validated user need** (not speculative scope), and
3. **Platform tier** supports it (e.g. do not prioritize GPU-only features before cloud ASR path exists).

When promoting an item, add it to [implementation_plan.md](implementation_plan.md) with a priority level (P1/P2) and remove or annotate it here.
