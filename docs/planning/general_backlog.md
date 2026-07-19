# General backlog

General application ideas with **no implementation priority**. Capture here so ideas are not lost; do **not** treat this list as a commitment or sequenced phase plan.

**Contrast:** [deferred_backlog.md](deferred_backlog.md) holds items that *were* phased and still have priority when dependencies clear. This file is for speculative, out-of-focus, or nice-to-have concepts.

Historical phases: [../archived/planning/phases.md](../archived/planning/phases.md).

---

## Ingest & media

| Idea | Notes |
|------|-------|
| Audio diarization research beyond Amazon Transcribe | Timing/VAD experiments, pyannote, etc. Product ASR is Transcribe-only. |
| Alternative local model support / Whisper / Ollama reintroduction | Explicitly outside AWS-only product strategy. |
| Tone/emotion inference from audio timing as a product feature | Not in product scope. |

---

## Analysis breadth

| Idea | Notes |
|------|-------|
| Additional analysis prompts / modules (escalation/repair mapping, emotional needs gaps, etc.) | Enough analytical breadth; structure-first stance remains. |
| Ontology-driven prompt generation | Speculative; static prompts + metadata are the default. |
| Meta handoff v2 (findings/constructs only) as a separate project | Largely superseded by structured synthesis inputs (Phase 37). |
| Non-relationship domains | Out of product focus. |

---

## UI & clients

| Idea | Notes |
|------|-------|
| Mobile-native layout | Responsive Streamlit or React — no schedule. |
| Native mobile app | Far future. |
| UI visual polish beyond evidence/graph usefulness | Explicitly deprioritized vs structure. |

---

## SaaS & marketplace

| Idea | Notes |
|------|-------|
| Multi-user SaaS / billing / RBAC / multi-tenant admin | Out of scope unless requirements change. |
| Complex permissions beyond API key + optional HTTPS | Near-term security needs already covered. |
| Public template marketplace / extensive plugin system | After durable workflow + module metadata — still unprioritized. |

---

## Platform curiosities

| Idea | Notes |
|------|-------|
| Helm chart / Kubernetes ingress | Not needed on ECS path. |
| Advanced analytics dashboards beyond operational telemetry | No priority. |
| mypy / typed CI beyond ruff | DX curiosity only. |
| Graph **database** backend | App-normalized tables are the persistence choice; external graph DB is not. |
| Runtime Hugging Face / public model downloads in AWS | Explicitly out of scope. |
| Hardcoded per-model code branches | Explicitly out of scope. |
| Modifying **MinneAnalytics** IAM/state in aws-backbone | Explicitly out of scope. |

---

## How ideas move

- If an idea becomes a **validated need** with a clear dependency gate, move it to [deferred_backlog.md](deferred_backlog.md) (or straight into a new phase plan).
- If an idea is rejected permanently, leave it here under notes or delete the row; do not revive it in archived phase docs.
