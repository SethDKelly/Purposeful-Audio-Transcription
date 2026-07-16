# Implementing — Active Priorities

Material work in flight for the **Relationship Reasoning Engine (RRE)** after **v0.9.0**.

| | |
|---|---|
| **Status** | **v1.0 in progress** — Workflow hardening + external readiness |
| **Canonical roadmap** | [roadmap_v0.7_to_v1.0.md](roadmap_v0.7_to_v1.0.md) |
| **Deferred ideas** | [future_considerations.md](future_considerations.md) |
| **Completed** | [completed.md](completed.md) · [../releases/v0.9.0.md](../releases/v0.9.0.md) |
| **Branch** | `v1.0/workflow-hardening` |
| **Strategy** | **AWS only** — Bedrock + Transcribe + ECS + RDS (`521018312783`, `us-east-2`) |
| **Cost control** | **Pause AWS when idle** — [../developer/aws-operations.md](../developer/aws-operations.md) |
| **Deploy policy** | Deploy on **minor-version completion** (tag `vX.Y.Z` or manual), not every main push |
| **Architecture** | [aws-deployment.md](aws-deployment.md) |

**Scope rule:** Follow the roadmap sequence. Do **not** add analysis modules for breadth. Prefer durable execution, safety, and evidence quality.

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
| **v0.8.0** | Normalized findings/constructs/relationships + graph | **Released** |
| **v0.9.0** | Cases + longitudinal + feedback | **Released** |
| **v1.0** | Workers + DAG + custom workflows + safety mode | **Active** |

---

## Immediate next steps

```text
[x] Release v0.9.0 · Deploy once · Pause AWS when idle
[x] v1.0 Priority 1 — Dedicated worker service
[x] v1.0 Priority 2 — Workflow DAG engine
[x] v1.0 Priority 3 — Custom workflow builder
[x] v1.0 Priority 4 — Long transcript strategy
[x] v1.0 Priority 5 — Safety-aware report mode
[ ] v1.0 Priority 6 — Production-grade API and documentation
[ ] Release v1.0.0 · Deploy once · Pause
```

**Standing ops:** Pause when idle. Deploy only on minor-version completion.

---

## v0.9 — Complete (summary)

Detail: [../releases/v0.9.0.md](../releases/v0.9.0.md). Roadmap: [roadmap_v0.7_to_v1.0.md](roadmap_v0.7_to_v1.0.md#v09--cases-and-longitudinal-analysis).

| Priority | Status |
|----------|--------|
| P1 Case data model | Done |
| P2 Case dashboard | Done |
| P3 Longitudinal comparison | Done |
| P4 Longitudinal synthesis | Done |
| P5 Report package export | Done |
| P6 Feedback loop | Done |

---

## v1.0 — Active work

Roadmap: [roadmap_v0.7_to_v1.0.md](roadmap_v0.7_to_v1.0.md#v10--workflow-hardening-and-external-readiness).

Plan detail: [../architecture/workflow_dag_plan.md](../architecture/workflow_dag_plan.md) · [../product/safety_aware_report_mode.md](../product/safety_aware_report_mode.md).

Reliable enough for external users, longer workflows, custom suites, production-like operation.

| Priority | Status | Notes |
|----------|--------|-------|
| P1 Dedicated worker | **Done** | ECS worker + cancel/timeout/retries; `python -m backend.worker` |
| P2 Workflow DAG | **Done** | `steps` / `depends_on` / parallel waves; `full_mvp` migrated |
| P3 Custom workflow builder | **Done** | User-defined module suites |
| P4 Long transcript strategy | **Done** | Chunk-aware; no silent head/tail-only |
| P5 Safety-aware report mode | **Done** | [../product/safety_aware_report_mode.md](../product/safety_aware_report_mode.md) |
| P6 Production API/docs | Pending | External-readiness polish |

---

## Decision log (active)

| Decision | Rationale |
|----------|-----------|
| **Breadth pause** | Enough modules; structure and trust next |
| **Deploy on minor versions only** | Cost control; pause between releases |
| **Table-first graph UI** | Shipped in v0.8 before fancy viz |
| **Transcript stitch deferred** | Prep workspace first; multi-file stitch later |
| **Pause AWS when idle** | Cost control |
| **AWS-only product** | No Whisper/Ollama runtime |
| **docs/ folder** | Renamed from `doc/` in v0.7.0 |
| **Normalized app tables (not a graph DB)** | v0.8 persistence choice |
| **Cases optional on transcripts** | Delete case unlinks; does not delete transcripts |

---

## Explicitly out of scope

- Modifying **MinneAnalytics** in aws-backbone
- Multi-user SaaS / billing / RBAC beyond API key (+ HTTPS optional)
- Production AWS account until v1.0 docs readiness
- Runtime Hugging Face downloads
- Graph database backend (normalized app tables shipped in v0.8)
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
