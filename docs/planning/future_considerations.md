# Future Considerations / Later Backlog

Items valuable for the Relationship Reasoning Engine but **not** part of the active **v0.7–v1.0** stabilization sequence in [roadmap_v0.7_to_v1.0.md](roadmap_v0.7_to_v1.0.md).

### Deferred from active roadmap

This item remains valuable but is not part of the v0.7–v1.0 stabilization sequence. It should be reconsidered after the reasoning engine, ontology, graph persistence, case model, and durable workflow engine are stable.

Active work: [implementing.md](implementing.md). Completed: [completed.md](completed.md). Historical optional backlog snapshot: [backlog.md](backlog.md) (points here for deferred items).

**Scope rule:** Do not distract from: secure → transcript prep → ontology → structured persistence → graph → cases → durable workflows.

---

## Ingest & media (deferred)

| Item | Notes | Why deferred |
|------|-------|--------------|
| **Multi-file audio upload & transcript stitching** | Upload successive clips; Transcribe each; ordered transcript stitch with provenance (was P2-A). Prefer stitch over audio concat. | Valuable UX; not required for ontology/graph/case core path. Revisit after v0.7 transcript prep workspace. |
| **Async / background Transcribe** | Submit job → poll/status + UI progress (poll wait already 3600s). | Improves long-audio UX; schedule after worker/job model (v1.0) or alongside if UAT pain is acute. |
| **Audio diarization research beyond Amazon Transcribe** | Timing/VAD experiments, pyannote, etc. | Product ASR is Transcribe-only. |
| **Alternative local model support / Whisper / Ollama reintroduction** | Local dual-path removed in v0.6. | Explicitly out of AWS-only product strategy. |

---

## Analysis breadth (deferred)

| Item | Notes | Why deferred |
|------|-------|--------------|
| **Additional analysis prompts / modules** | Escalation/repair mapping, emotional needs gaps, etc. ([../archived/backlog-analysis-suite.md](../archived/backlog-analysis-suite.md)) | Enough analytical breadth for now; structure first. |
| **Ontology-driven prompt generation** | Generate prompts from constructs + workflow goals | Speculative; static prompts + metadata remain default through v1.0. |
| **Module `inference:` YAML block** | Per-module temperature / max tokens without code changes | Useful; secondary to construct expectations + telemetry (v0.7). |
| **Haiku / cheaper model routing for light modules** | Keep Sonnet for hard lenses + meta; A/B first | Optimize after v0.7 telemetry. |
| **Meta handoff v2 (findings/constructs only)** | Shrink synthesis prompt further | Partially superseded by v0.8 structured synthesis inputs. |
| **Raise concurrency carefully (4–5)** | After parallel=3 soak | Config tune after telemetry. |
| **Non-relationship domains** | | Out of product focus. |

---

## UI & frontend (deferred)

| Item | Notes | Why deferred |
|------|-------|--------------|
| **React frontend (Phase S)** | Vite + React + TS; transcript list, run status, report, explore; `X-API-Key` from env | Streamlit remains UI through graph/case UX; SPA after API contracts harden (v1.0 P6). |
| **Knowledge graph UI richness** | Interactive layout beyond table/Mermaid | v0.8 ships table-first explorer; advanced viz later. |
| **Mobile-native layout** | Responsive Streamlit or React | After core evidence/graph UX. |
| **Full Streamlit feature parity in React** | Audio ingest, full workflow picker | Large; after SPA MVP. |
| **Real-time collaborative editing** | | After case model + auth posture. |
| **Native mobile app** | | Far future. |
| **UI visual polish beyond evidence/graph usefulness** | | Explicitly deprioritized vs structure. |

---

## Professional, collaboration & SaaS (deferred)

| Item | Notes | Why deferred |
|------|-------|--------------|
| **Collaborative review (full)** | Multi-participant agreements; shared review | Basic finding feedback is **v0.9 P6**; full collab later. |
| **Professional mode (full)** | Supervision notes, treatment planning beyond case dashboard | Case dashboard is v0.9; clinician portal extras later. |
| **Finding feedback UI (extended)** | Rich notes/tagging beyond v0.9 loop | Extend after feedback schema ships. |
| **Multi-conversation report pack** | Upload multiple exported workflow reports for cross-conversation synthesis | Overlaps v0.9 cases; lighter import path may return after case exports. |
| **Multi-user SaaS / billing / RBAC / multi-tenant admin** | Accounts, subscription | Out of scope unless requirements change. |
| **Complex permissions beyond current API key + HTTPS** | | v0.7 P1 covers near-term security needs. |
| **Public template marketplace / extensive plugin system** | | After durable workflow + module metadata. |

---

## Platform & ops (deferred)

| Item | Notes | Why deferred |
|------|-------|--------------|
| **Helm chart** | K8s ingress if org moves off ECS | Not needed on ECS path. |
| **Production AWS account** | `prod-github-deploy` in aws-backbone | After v1.0 readiness docs. |
| **Distributed job queue (Celery/Redis)** | Multi-host | Prefer dedicated worker first (**v1.0 P1**). |
| **Prometheus `/metrics`** | Optional operator metrics | After v0.7 module telemetry. |
| **Run telemetry dashboard (ops UI)** | Aggregate durations/failures | v0.7 P6 is persistence first; dashboards later. |
| **Advanced analytics dashboards beyond operational telemetry** | | Later. |
| **Pinned lockfile (`uv.lock`)** | Was P1-5a | Useful CI harden; not blocking v0.7 P1 security path — schedule opportunistically. |
| **mypy / typed CI** | Beyond ruff | DX later. |
| **Module scaffolding CLI** | `scripts/new_module.py` | After ontology + expected_constructs land. |

---

## Research & evaluation (partially absorbed)

| Item | Notes | Status vs roadmap |
|------|-------|-------------------|
| **Benchmark suite / A/B prompt versions / human eval rubric** | | Core loop → **v0.7 P5**; richer A/B tooling stays here until fixtures exist. |
| **Eval script: construct coverage** | `scripts/eval_construct_coverage.py` | Largely absorbed by v0.7 P4–P5; keep as implementation detail when building eval. |

---

## Explicitly out of scope (unchanged)

- Modifying **MinneAnalytics** IAM/state in aws-backbone
- Runtime Hugging Face / public model downloads in AWS
- Hardcoded per-model code branches
- Graph **database** backend (app-normalized graph tables are in-scope for v0.8; external graph DB is not)
- Tone/emotion inference from audio timing as a product feature

---

## How items return to the active plan

1. Current release milestone priorities in [implementing.md](implementing.md) are complete or blocked on a validated need.
2. The item addresses a **validated user need** (not speculative scope).
3. Platform tier supports it (e.g. do not prioritize GPU-only features).

When promoting: add to [implementing.md](implementing.md) under the correct release priority and annotate or remove the row here.
