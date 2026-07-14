# Backlog — Future & Nice-to-Have

Optional enhancements **not** on the active path in [implementing.md](implementing.md). Completed work: [completed.md](completed.md).

**Scope rule:** Backlog items improve UX, local dev comfort, research velocity, or alternate deployment targets. They do **not** block AWS dev, Bedrock/Transcribe migration, or core workflow value.

**When to promote:** Move an item to [implementing.md](implementing.md) only when Tier 1–2 work for the current milestone is complete and the item addresses a **validated user need**.

---

## Local development (optional)

| Item | Notes | Effort |
|------|-------|--------|
| **Local Docker Compose** | `api`, `streamlit`, optional Ollama/postgres profiles — laptop dev only; Dockerfiles exist for AWS | 1 week |
| **Windows troubleshooting guide** | DLL, WinError 10055, diarization skip reasons | 1–2 days |
| **Ollama `num_ctx` / temperature tuning** | Local Ollama only; AWS uses Bedrock | 1 day |
| **Model volume mounts** | `HF_HOME`, `WHISPER_CACHE`, Ollama `~/.ollama` for Compose | 2–3 days |
| **Offline model bundle script** | Export/import models on connected machine for air-gapped host | 3–5 days |

---

## UI & frontend

### React frontend (Phase S)

Exploration-first SPA consuming existing APIs only — no duplicated business logic.

| Item | Notes |
|------|-------|
| **Stack** | Vite + React + TypeScript |
| **MVP pages** | Transcript list, workflow run status, report, explore (drill-down + ask) |
| **Auth** | `X-API-Key` header from env |
| **Non-goals (R1)** | Full Streamlit parity (audio ingest, diarization progress, full workflow picker); mobile-native layout |

**Effort:** 2–3 weeks

| Item | Notes | Effort |
|------|-------|--------|
| **Knowledge graph UI richness** | Beyond basic Streamlit Mermaid; interactive layout, filtering | 1–2 weeks |
| **Mobile-native layout** | Responsive Streamlit or React | Medium |
| **Full Streamlit feature parity in React** | Audio ingest, diarization progress, full workflow picker | Large |

*Counterfactual exploration presets may land in Tier 3 (P2-O5) before React.*

---

## Audio & transcription (local / research)

Superseded in **cloud** by Amazon Transcribe ([implementing.md](implementing.md) P1-1). Useful for local quality experiments.

| Item | Notes | Effort |
|------|-------|--------|
| **M2 UI polish** | Streamlit progress: `Diarizing…` → `Transcribing N speaker segments…` | 2–3 days |
| **M2.5 — Word-level alignment** | `word_timestamps=True` + per-word speaker assignment | 3–5 days |
| **Timing analysis** | Pauses, interruptions, overlap duration metrics | 1 week |
| **Interruption detection** | Heuristic or model-based | 1 week |
| **Pause detection** | From audio timing; caution on tone/emotion inference | 3–5 days |
| **Channel-based speaker split** | Stereo with one speaker per channel (no diarization) | 2–3 days |
| **VAD preprocessing** | Voice activity detection before diarization on noisy audio | 3–5 days |
| **torchcodec experiment** | In-process decode with ffmpeg CLI fallback — Linux only | 2–3 days |

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

## Platform & deployment (non-AWS)

Docker images for AWS exist ([completed.md](completed.md)). Remaining local/K8s packaging:

| Item | Notes | Effort |
|------|-------|--------|
| **Compose stack** | `docker-compose.yml`: api, ui, ollama (profile), postgres (profile); startup order docs | 3–5 days |
| **Docker smoke script** | `scripts/docker-smoke.sh` / PowerShell — health + fixture transcribe | 1 day |
| **Build args** | `TORCH_VARIANT=cpu\|cuda`, `INCLUDE_DIARIZATION=true\|false` | 1–2 days |
| **Helm chart** | K8s ingress, secrets, PVC for clinic/org deploys | 1 week |
| **Offline model bake in CI** | Image with pre-accepted HF models; less relevant once Transcribe/Bedrock | 1 week |
| **SQLCipher / TDE options** | Encrypted SQLite or PostgreSQL TDE for regulated environments | 1 week |
| **Distributed job queue** | Celery/Redis for multi-worker deployments | Large |
| **Multi-user SaaS** | Accounts, billing, RBAC | Out of product scope unless requirements change |
| **Production AWS account** | `prod-github-deploy` in aws-backbone | Deferred |

---

## Secure & air-gapped operation (local / clinic)

AWS VPC no-egress is the **cloud** equivalent ([implementing.md](implementing.md) Tier 1). For offline/on-prem hosts:

| Item | Notes | Effort |
|------|-------|--------|
| **Air-gapped install guide** | Staged Ollama blobs, Whisper weights, pyannote pipeline via removable media or internal registry | 3–5 days |
| **No-egress mode** | `ALLOW_OUTBOUND_HTTP=false` — fail/warn if HF/telemetry attempted; require pre-staged models | 2–3 days |
| **Bind-local defaults** | API/UI on `127.0.0.1` unless configured; warn on public exposure | 1 day |
| **Secrets management** | Docker/K8s secrets instead of plain `.env` in production | 2–3 days |
| **Data at rest encryption** | LUKS, BitLocker, cloud disk encryption; optional SQLCipher | 1 week |
| **Secure temp delete** | `DELETE_TEMP_ON_COMPLETE=true` with optional secure overwrite | 1–2 days |
| **Privacy messaging** | Ingest-step copy: processed locally; clarify Ollama/HF touch when not air-gapped | 1 day |
| **Threat model one-pager** | Local trust boundary, API key scope, multi-user gaps, backup exposure | 1–2 days |

**Acceptance:** Operator deploys on internet-disconnected host with pre-staged models; no audio/transcript leaves machine during normal operation.

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
