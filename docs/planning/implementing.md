# Implementing — Active Priorities

Material work in flight for the **Relationship Reasoning Engine (RRE)** after **v0.7.0**.

| | |
|---|---|
| **Status** | **v0.8 in progress** — Structured persistence + graph reasoning |
| **Canonical roadmap** | [roadmap_v0.7_to_v1.0.md](roadmap_v0.7_to_v1.0.md) |
| **Deferred ideas** | [future_considerations.md](future_considerations.md) |
| **Completed** | [completed.md](completed.md) · [../releases/v0.7.0.md](../releases/v0.7.0.md) |
| **Branch** | `v0.8/structured-persistence` |
| **Strategy** | **AWS only** — Bedrock + Transcribe + ECS + RDS (`521018312783`, `us-east-2`) |
| **Cost control** | **Pause AWS when idle** — [../developer/aws-operations.md](../developer/aws-operations.md) |
| **Deploy policy** | Deploy on **minor-version completion** (tag `vX.Y.Z` or manual), not every main push |
| **Architecture** | [aws-deployment.md](aws-deployment.md) |

**Scope rule:** Follow the roadmap sequence. Do **not** add analysis modules for breadth. Prefer structure, trust, and evidence quality.

**North star:**

```text
Domain Model → Ontology → Module Definitions → Workflow Engine → Prompt Compiler
  → Structured Findings → Synthesis Engine → Interactive UI
```

---

## Guiding sequence

```text
security → transcript quality → ontology → structured persistence
  → graph reasoning → cases → workflow hardening
```

| Release | Theme | Status |
|---------|--------|--------|
| **v0.6.0** | Trust controls + full/research workflows + AWS-only | **Released** |
| **v0.7.0** | Secure UAT + transcript prep + ontology foundation | **Released** |
| **v0.8** | Normalized findings/constructs/relationships + graph | **Active** |
| **v0.9** | Cases + longitudinal + feedback | Pending |
| **v1.0** | Workers + DAG + custom workflows + safety mode | Pending |

---

## Immediate next steps

```text
[x] Release v0.7.0 · Deploy once · Pause AWS when idle
[x] v0.8 Priority 1 — Normalized findings persistence
[x] v0.8 Priority 2 — Normalized constructs persistence
[ ] v0.8 Priority 3 — Construct relationship persistence
[ ] v0.8 Priority 4 — Graph merge / deduplication
[ ] v0.8 Priority 5 — Deterministic convergence and confidence scoring
[ ] v0.8 Priority 6 — Graph exploration UI (table-first)
[ ] v0.8 Priority 7 — Synthesis over structured objects
[ ] Release v0.8.0 · Deploy once · Pause · then v0.9
```

**Standing ops:** Pause when idle. Deploy only on minor-version completion.

---

## v0.7 — Complete (summary)

Detail: [../releases/v0.7.0.md](../releases/v0.7.0.md) · acceptance: [roadmap_v0.7_to_v1.0.md](roadmap_v0.7_to_v1.0.md#v07--trust-transcript-preparation-and-ontology-foundation).

| Priority | Status |
|----------|--------|
| P1 Secure external UAT | Done |
| P2 Transcript preparation workspace | Done |
| P3 Ontology vocabulary v1 | Done |
| P4 Module construct expectations | Done |
| P5 Golden fixtures + evaluation foundation | Done (GT001/GT002; expand count later) |
| P6 Cost / latency / module telemetry | Done |

---

## v0.8 — Active work

Plan: [../architecture/structured_persistence_plan.md](../architecture/structured_persistence_plan.md).

Promote findings, constructs, evidence, confidence, and relationships from JSON blobs into first-class persistent objects; enable table-first graph exploration and structured synthesis.

| Priority | Status | Notes |
|----------|--------|-------|
| P1 Findings | **Done** | `findings` + evidence/alternatives tables; write on module complete; exploration prefers DB |
| P2 Constructs | **Done** | `constructs` + evidence/sources; ontology resolve/warn; knowledge graph prefers DB |
| P3 Relationships | Pending | |
| P4 Merge / dedup | Pending | |
| P5 Convergence scoring | Pending | |
| P6 Exploration UI | Pending | |
| P7 Structured synthesis | Pending | |

---

## Later releases (summary only)

| Release | Priorities | Plan docs |
|---------|------------|-----------|
| **v0.9** | Case model → dashboard → longitudinal → export → feedback | roadmap §v0.9 |
| **v1.0** | Worker → DAG → custom builder → long transcript → safety mode | [../architecture/workflow_dag_plan.md](../architecture/workflow_dag_plan.md), [../product/safety_aware_report_mode.md](../product/safety_aware_report_mode.md) |

---

## Decision log (active)

| Decision | Rationale |
|----------|-----------|
| **Breadth pause** | Enough modules; structure and trust next |
| **Deploy on minor versions only** | Cost control; pause between releases |
| **Table-first graph UI** | v0.8 explorer before fancy viz |
| **Transcript stitch deferred** | Prep workspace first; multi-file stitch later |
| **Pause AWS when idle** | Cost control |
| **AWS-only product** | No Whisper/Ollama runtime |
| **docs/ folder** | Renamed from `doc/` in v0.7.0 |

---

## Explicitly out of scope

- Modifying **MinneAnalytics** in aws-backbone
- Multi-user SaaS / billing / RBAC beyond API key (+ HTTPS optional)
- Production AWS account until v1.0 docs readiness
- Runtime Hugging Face downloads
- Graph database backend (normalized app tables are in-scope for v0.8)
- Reintroducing local Whisper/Ollama

---

## Supporting documents

| Document | Purpose |
|----------|---------|
| [roadmap_v0.7_to_v1.0.md](roadmap_v0.7_to_v1.0.md) | Full phased roadmap + acceptance |
| [future_considerations.md](future_considerations.md) | Deferred backlog |
| [aws-deployment.md](aws-deployment.md) | AWS architecture |
| [../developer/aws-operations.md](../developer/aws-operations.md) | Deploy / pause / smoke |
| [../developer/architecture.md](../developer/architecture.md) | Code architecture |
| **aws-backbone** | IAM / OIDC only |
