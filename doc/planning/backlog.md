# Backlog — Nice-to-have & deferred enhancements

Items here are **not** on the critical or important path in [implementation_plan.md](implementation_plan.md). They remain valuable but should not block platform stabilization (Windows/local deployment, Ollama tuning, containers, workflow completeness).

**Priority within this backlog:** ordered roughly by value vs effort. Pull items into the implementation plan only when P0–P2 work is stable.

---

## UI & frontend

| Item | Notes | Effort |
|------|-------|--------|
| **React frontend (Phase S)** | Vite + React + TypeScript SPA; API-only; explore-first MVP | 2–3 weeks |
| **Knowledge graph UI richness** | Beyond basic Streamlit Mermaid; interactive layout, filtering | 1–2 weeks |
| **Mobile-native layout** | Responsive Streamlit or React | Medium |
| **Full Streamlit feature parity in React** | Audio ingest, diarization progress, full workflow picker | Large |

---

## Audio & transcription

| Item | Notes | Effort |
|------|-------|--------|
| **M2.5 — Word-level alignment** | `word_timestamps=True` + per-word speaker assignment for boundary precision | 3–5 days |
| **Timing analysis** | Pauses, interruptions, overlap duration metrics | 1 week |
| **Interruption detection** | Heuristic or model-based; caution on tone/emotion inference | 1 week |
| **Channel-based speaker split** | Stereo recordings with one speaker per channel (no diarization) | 2–3 days |
| **VAD preprocessing** | Voice activity detection before diarization on noisy audio | 3–5 days |

---

## Analysis & ontology

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
| **Professional mode (full)** | Case files, session series, supervision notes, treatment planning | Large |
| **Finding feedback UI** | Helpful/unhelpful + notes (API may land in Phase R first) | 2–3 days |
| **Redaction pass improvements** | PII patterns, configurable redaction rules before export | 3–5 days |

---

## Platform & deployment

| Item | Notes | Effort |
|------|-------|--------|
| **Helm chart** | K8s ingress, secrets, PVC for clinic/org deploys | 1 week |
| **Offline model bake in CI** | Image with pre-accepted HF models; no runtime download | 1 week |
| **Pinned lockfiles in CI** | `uv.lock` / requirements lock for reproducible transitive deps | 2–3 days |
| **SQLCipher / TDE options** | Encrypted SQLite or PostgreSQL TDE for regulated environments | 1 week |
| **Distributed job queue** | Celery/Redis for multi-worker deployments | Large |
| **Multi-user SaaS** | Accounts, billing, RBAC | Out of product scope unless requirements change |

---

## Infrastructure & observability

| Item | Notes | Effort |
|------|-------|--------|
| **Run telemetry dashboard** | Aggregate module durations, failure rates, model used | 1 week |
| **Prometheus metrics endpoint** | Optional `/metrics` for operators | 2–3 days |
| **Workflow run cancellation** | Cancel in-flight background workflow | 2–3 days |

---

## Developer experience

| Item | Notes | Effort |
|------|-------|--------|
| **Module scaffolding CLI** | `scripts/new_module.py` — YAML + prompt stub | 1 day |
| **Golden LLM output fixtures** | Record/replay for integration tests without Ollama | 3–5 days |
| **Pre-commit hooks** | ruff, mypy optional | 1 day |

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
3. **Platform tier** supports it (e.g. do not prioritize GPU-only features before Docker GPU docs exist).

When promoting an item, add it to [implementation_plan.md](implementation_plan.md) with a priority level (P1/P2) and remove or mark it done here.
