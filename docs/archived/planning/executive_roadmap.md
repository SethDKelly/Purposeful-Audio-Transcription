# Executive Roadmap — Relationship Reasoning Engine

Historical executive view of the RRE program. Detailed phase records: [phases.md](phases.md). Active planning: [`../../planning/`](../../planning/).

| | |
|---|---|
| **Product** | Relationship Reasoning Engine (RRE) |
| **Baseline release** | **v1.0.0** on `main` |
| **Post-v1.0 bands** | v1.1–v1.4 + v2.0 foundation **complete** (Phases **50–54**) |
| **Runtime** | AWS only — Bedrock + Transcribe + ECS + RDS (`521018312783`, `us-east-2`) |
| **Phase log** | [phases.md](phases.md) (Phases **1–54** complete) |
| **Next phase number** | **55** (v2.1 cutover / auth / graph — [phases/10](../../planning/phases/10_v2_1_cutover_auth_and_graph_depth.md)) |
| **Active plan** | [phases/](../../planning/phases/) · [deferred_backlog](../../planning/deferred_backlog.md) · [general_backlog](../../planning/general_backlog.md) |

---

## Strategic outcomes

The program evolved a paste-and-prompt prototype into a durable, evidence-linked reasoning product:

1. **Evidence-first analysis** — Quote IDs, structured module JSON, confidence ceilings, and safety validation so claims stay inspectable.
2. **Replaceable prompts, durable structure** — Schemas, ontology, workflows, and normalized findings/constructs/relationships outlive any single prompt wording.
3. **Trustworthy handling of sensitive dialogue** — API key, optional HTTPS, generic errors + request IDs, log redaction, retention/privacy framing, export redaction; SafetyEvent audit trail (v2 foundation).
4. **AWS-native operations** — One product path (no local Whisper/Ollama runtime); deploy on minor-version tags; pause ECS/RDS when idle.
5. **Structured relationship reasoning** — Ontology → persisted graph → case/longitudinal insight → hardened workflow execution.
6. **External-ready execution** — Dedicated worker, DAG workflows, custom suites, honest long-transcript sampling, safety-aware report mode.
7. **React product shell** — Primary UX in `frontend-react/` via `/api/v1`; Streamlit demoted to admin/eval (ALB cutover still ops).

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
| **Pause when idle** | Scale ECS (API/UI/worker/web) to 0 and stop RDS between sessions |
| **Table-first graph UI** | Ship queryable inventory before fancy visualization |
| **Normalized app tables** | Not an external graph database |
| **Defer deliberately** | Blocked or dependency-gated work goes to `deferred_backlog`; unprioritized ideas to `general_backlog` |

---

## Phase completion summary

| Band | Phases | Theme | Culminating release / note |
|------|--------|-------|----------------------------|
| **Foundation** | 1–8 | MVP shell: ingest, registry, compiler, core modules, workflow, synthesis, Streamlit | **v0.2.0** |
| **Expansion** | 9–13 | Full module library, workflows, exports, Postgres/jobs, exploration | **v0.3.0** |
| **Audio & docs** | 14–16 | Doc layout; diarization/sliced ASR; local LLM reliability | **v0.4.x** |
| **Cloud pivot** | 17–24 | Backbone OIDC, observability, containers, Terraform, CI/CD, Bedrock, Transcribe, AWS-only prune | **v0.5.1 → v0.6.0** |
| **Trust & ontology** | 25–30 | Secure UAT, transcript prep, ontology, construct expectations, golden eval, telemetry | **v0.7.0** |
| **Structured graph** | 31–37 | Normalized findings/constructs/relationships, merge, convergence, inventory UI, structured synthesis | **v0.8.0** |
| **Cases** | 38–43 | Case model/dashboard, longitudinal compare/synthesis, report package, finding feedback | **v0.9.0** |
| **Hardening** | 44–49 | Worker, DAG, custom workflows, long-transcript strategy, safety mode, production docs | **v1.0.0** |
| **Post-v1 ops** | 50 | v1.1 operational hardening (IAM, worker ops, Streamlit boundary, observability) | on `post-v1.0/backlog` |
| **Eval + API** | 51 | v1.2 golden/safety harness, `/api/v1`, React readiness | on `post-v1.0/backlog` |
| **React MVP** | 52 | v1.3 `frontend-react` vertical slice | on `post-v1.0/backlog` |
| **Platform UI** | 53 | v1.4 graph/cases/modules/governance/Streamlit decision | on `post-v1.0/backlog` |
| **v2 foundation** | 54 | Safety events, eval release gates, server report packages | on `post-v1.0/backlog` |

**Status:** Phases **1–54** are **complete**. Active next work: Phase **55** / [v2.1](../../planning/phases/10_v2_1_cutover_auth_and_graph_depth.md).

---

## Guiding sequence

```text
security → transcript quality → ontology → structured persistence
  → graph reasoning → cases → workflow hardening ✓
  → ops harden → eval/API → React MVP → platform UI → v2 foundation ✓
  → ALB cutover + auth + graph depth (next)
```

---

## Where to look next

| Need | Document |
|------|----------|
| Full phase detail | [phases.md](phases.md) |
| Active execution band | [../../planning/phases/10_v2_1_cutover_auth_and_graph_depth.md](../../planning/phases/10_v2_1_cutover_auth_and_graph_depth.md) |
| v2 vision | [../../planning/phases/05_v2_0_future_state_architecture.md](../../planning/phases/05_v2_0_future_state_architecture.md) |
| Priority deferred work | [../../planning/deferred_backlog.md](../../planning/deferred_backlog.md) |
| Unprioritized ideas | [../../planning/general_backlog.md](../../planning/general_backlog.md) |
| Release notes | [../../releases/](../../releases/) |
| Design package | [../../design/](../../design/) |
| AWS ops | [../../developer/aws-operations.md](../../developer/aws-operations.md) · [../../developer/aws-deployment.md](../../developer/aws-deployment.md) |
