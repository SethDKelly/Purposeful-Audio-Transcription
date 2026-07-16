# Implementing — Active Priorities

Material work in flight for the **Relationship Reasoning Engine (RRE)** after **v0.8.0**.

| | |
|---|---|
| **Status** | **v0.9 in progress** — Cases + longitudinal analysis |
| **Canonical roadmap** | [roadmap_v0.7_to_v1.0.md](roadmap_v0.7_to_v1.0.md) |
| **Deferred ideas** | [future_considerations.md](future_considerations.md) |
| **Completed** | [completed.md](completed.md) · [../releases/v0.8.0.md](../releases/v0.8.0.md) |
| **Branch** | `v0.9/cases-longitudinal` |
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
| **v0.8.0** | Normalized findings/constructs/relationships + graph | **Released** |
| **v0.9** | Cases + longitudinal + feedback | **Active** |
| **v1.0** | Workers + DAG + custom workflows + safety mode | Pending |

---

## Immediate next steps

```text
[x] Release v0.8.0 · Deploy once · Pause AWS when idle
[x] v0.9 Priority 1 — Case data model
[x] v0.9 Priority 2 — Case dashboard
[x] v0.9 Priority 3 — Longitudinal comparison
[x] v0.9 Priority 4 — Longitudinal synthesis module
[ ] v0.9 Priority 5 — Report package export
[ ] v0.9 Priority 6 — User feedback / analyst review loop
[ ] Release v0.9.0 · Deploy once · Pause · then v1.0
```

**Standing ops:** Pause when idle. Deploy only on minor-version completion.

---

## v0.8 — Complete (summary)

Detail: [../releases/v0.8.0.md](../releases/v0.8.0.md) · plan: [../architecture/structured_persistence_plan.md](../architecture/structured_persistence_plan.md).

| Priority | Status |
|----------|--------|
| P1 Normalized findings | Done |
| P2 Normalized constructs | Done |
| P3 Construct relationships | Done |
| P4 Graph merge / dedup | Done |
| P5 Convergence scoring | Done |
| P6 Table-first exploration UI | Done |
| P7 Synthesis over structured objects | Done |

---

## v0.9 — Active work

Roadmap: [roadmap_v0.7_to_v1.0.md](roadmap_v0.7_to_v1.0.md#v09--cases-and-longitudinal-analysis).

Multiple transcripts over time; longitudinal reasoning and feedback loops.

| Priority | Status | Notes |
|----------|--------|-------|
| P1 Case data model | **Done** | `cases` table; transcript `case_id` / session fields; CRUD + assign API |
| P2 Case dashboard | **Done** | Streamlit Cases expander: create/assign/list sessions |
| P3 Longitudinal comparison | **Done** | `POST /api/exploration/compare-transcripts` + UI |
| P4 Longitudinal synthesis | **Done** | `longitudinal_synthesis` module + case handoff API |
| P5 Report package export | Pending | |
| P6 Feedback loop | Pending | |

---

## Later releases (summary only)

| Release | Priorities | Plan docs |
|---------|------------|-----------|
| **v1.0** | Worker → DAG → custom builder → long transcript → safety mode | [../architecture/workflow_dag_plan.md](../architecture/workflow_dag_plan.md), [../product/safety_aware_report_mode.md](../product/safety_aware_report_mode.md) |

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
