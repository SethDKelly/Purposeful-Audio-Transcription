# Executive Roadmap — Relationship Reasoning Engine

Historical executive view of the RRE program through **v1.0.0** (July 2026). Detailed phase records: [phases.md](phases.md). Active planning lives under [`../../planning/`](../../planning/) (`deferred_backlog` · `general_backlog`).

| | |
|---|---|
| **Product** | Relationship Reasoning Engine (RRE) |
| **Baseline release** | **v1.0.0** on `main` |
| **Runtime** | AWS only — Bedrock + Transcribe + ECS + RDS (`521018312783`, `us-east-2`) |
| **Phase log** | [phases.md](phases.md) (Phases **1–49** complete) |
| **Next phase number** | **50** (v1.1 operational hardening — active plan in [`../../planning/phases/`](../../planning/phases/)) |
| **Active plan** | [phases/](../../planning/phases/) · [deferred_backlog](../../planning/deferred_backlog.md) · [general_backlog](../../planning/general_backlog.md) |

---

## Strategic outcomes

The program evolved a paste-and-prompt prototype into a durable, evidence-linked reasoning product:

1. **Evidence-first analysis** — Quote IDs, structured module JSON, confidence ceilings, and safety validation so claims stay inspectable.
2. **Replaceable prompts, durable structure** — Schemas, ontology, workflows, and normalized findings/constructs/relationships outlive any single prompt wording.
3. **Trustworthy handling of sensitive dialogue** — API key, optional HTTPS, generic errors + request IDs, log redaction, retention/privacy framing, export redaction.
4. **AWS-native operations** — One product path (no local Whisper/Ollama runtime); deploy on minor-version tags; pause ECS/RDS when idle.
5. **Structured relationship reasoning** — Ontology → persisted graph → case/longitudinal insight → hardened workflow execution.
6. **External-ready execution** — Dedicated worker, DAG workflows, custom suites, honest long-transcript sampling, safety-aware report mode.

**North star (unchanged):**

```text
Domain Model → Ontology → Module Definitions → Workflow Engine → Prompt Compiler
  → Structured Findings → Synthesis Engine → Interactive UI
```

---

## Guiding principles

| Principle | Meaning |
|-----------|---------|
| **Breadth pause** | Enough analysis modules; prefer structure, trust, and evidence quality over new lenses |
| **Prompts are replaceable** | Durable assets are schemas, ontology, workflows, graph objects, fixtures, and UX patterns |
| **Evidence before polish** | Traceability and confidence beat visual chrome |
| **AWS-only product** | Bedrock + Transcribe + ECS + RDS; pytest uses mocks/SQLite |
| **Deploy on minor versions** | Tag `vX.Y.Z` or manual deploy; ordinary `main` pushes do not wake AWS |
| **Pause when idle** | Scale ECS (API/UI/worker) to 0 and stop RDS between sessions |
| **Table-first graph UI** | Ship queryable inventory before fancy visualization |
| **Normalized app tables** | Not an external graph database |
| **Defer deliberately** | Blocked or dependency-gated work goes to `deferred_backlog`; unprioritized ideas to `general_backlog` |

---

## Phase completion summary

| Band | Phases | Theme | Culminating release |
|------|--------|-------|---------------------|
| **Foundation** | 1–8 | MVP shell: ingest, registry, compiler, core modules, workflow, synthesis, Streamlit | **v0.2.0** |
| **Expansion** | 9–13 | Full module library, workflows, exports, Postgres/jobs, exploration | **v0.3.0** |
| **Audio & docs** | 14–16 | Doc layout; diarization/sliced ASR; local LLM reliability | **v0.4.x** |
| **Cloud pivot** | 17–24 | Backbone OIDC, observability, containers, Terraform, CI/CD, Bedrock, Transcribe, AWS-only prune | **v0.5.1 → v0.6.0** |
| **Trust & ontology** | 25–30 | Secure UAT, transcript prep, ontology, construct expectations, golden eval, telemetry | **v0.7.0** |
| **Structured graph** | 31–37 | Normalized findings/constructs/relationships, merge, convergence, inventory UI, structured synthesis | **v0.8.0** |
| **Cases** | 38–43 | Case model/dashboard, longitudinal compare/synthesis, report package, finding feedback | **v0.9.0** |
| **Hardening** | 44–49 | Worker, DAG, custom workflows, long-transcript strategy, safety mode, production docs | **v1.0.0** |

**Status:** Phases **1–49** are **complete**. New planned work, once finished, continues at Phase **50** in [phases.md](phases.md).

---

## Guiding sequence (completed)

```text
security → transcript quality → ontology → structured persistence
  → graph reasoning → cases → workflow hardening ✓
```

---

## Where to look next

| Need | Document |
|------|----------|
| Full phase detail | [phases.md](phases.md) |
| Priority future work (was phased, deferred) | [../../planning/deferred_backlog.md](../../planning/deferred_backlog.md) |
| Unprioritized ideas | [../../planning/general_backlog.md](../../planning/general_backlog.md) |
| Release notes | [../../releases/](../../releases/) |
| Design package | [../../design/](../../design/) |
| AWS ops | [../../developer/aws-operations.md](../../developer/aws-operations.md) · [../../developer/aws-deployment.md](../../developer/aws-deployment.md) |
