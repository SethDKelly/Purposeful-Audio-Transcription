# Implementing — Active Priorities

Material work in flight for the **Relationship Reasoning Engine (RRE)** after **v1.0.0**.

| | |
|---|---|
| **Status** | **Post-v1.0** — roadmap complete through external readiness; backlog-driven |
| **Canonical roadmap** | [roadmap_v0.7_to_v1.0.md](roadmap_v0.7_to_v1.0.md) (**complete**) |
| **Deferred ideas** | [future_considerations.md](future_considerations.md) |
| **Completed** | [completed.md](completed.md) · [../releases/v1.0.0.md](../releases/v1.0.0.md) |
| **Branch** | `post-v1.0/backlog` |
| **Strategy** | **AWS only** — Bedrock + Transcribe + ECS + RDS (`521018312783`, `us-east-2`) |
| **Cost control** | **Pause AWS when idle** — [../developer/aws-operations.md](../developer/aws-operations.md) |
| **Deploy policy** | Deploy on **minor-version completion** (tag `vX.Y.Z` or manual), not every main push |
| **Architecture** | [aws-deployment.md](aws-deployment.md) |

**Scope rule:** Prefer reliability, evidence quality, and operator trust. Pull from [future_considerations.md](future_considerations.md) deliberately — do not expand analysis modules for breadth.

**North star:**

```text
Domain Model → Ontology → Module Definitions → Workflow Engine → Prompt Compiler
  → Structured Findings → Synthesis Engine → Interactive UI
```

---

## Guiding sequence (complete through v1.0)

```text
security → transcript quality → ontology → structured persistence
  → graph reasoning → cases → workflow hardening ✓
```

| Release | Theme | Status |
|---------|--------|--------|
| **v0.6.0** | Trust controls + full/research workflows + AWS-only | **Released** |
| **v0.7.0** | Secure UAT + transcript prep + ontology foundation | **Released** |
| **v0.8.0** | Normalized findings/constructs/relationships + graph | **Released** |
| **v0.9.0** | Cases + longitudinal + feedback | **Released** |
| **v1.0.0** | Workers + DAG + custom workflows + safety mode | **Released** |

---

## Immediate next steps

```text
[x] Release v1.0.0 · Deploy once · Pause AWS when idle
[ ] Pick next work from future_considerations (stitch, richer graph UI, multi-user, etc.)
```

**Standing ops:** Pause when idle. Deploy only on minor-version completion.

---

## v1.0 — Complete (summary)

Detail: [../releases/v1.0.0.md](../releases/v1.0.0.md).

| Priority | Status |
|----------|--------|
| P1 Dedicated worker | Done |
| P2 Workflow DAG | Done |
| P3 Custom workflow builder | Done |
| P4 Long transcript strategy | Done |
| P5 Safety-aware report mode | Done |
| P6 Production API/docs | Done |

---

## Post-v1.0 — Active work

Select from [future_considerations.md](future_considerations.md). Suggested themes:

| Theme | Notes |
|-------|-------|
| Multi-file audio stitch | Deferred from prep workspace |
| Richer knowledge-graph UI | Beyond table-first |
| Production account / HTTPS hardening | When external users need it |
| Collaborative review | Beyond finding feedback |

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
| **Dedicated worker on ECS** | Jobs survive API task recycle |

---

## Explicitly out of scope

- Modifying **MinneAnalytics** in aws-backbone
- Multi-user SaaS / billing / RBAC beyond API key (+ HTTPS optional) until explicitly pulled in
- Runtime Hugging Face downloads
- Graph database backend (normalized app tables shipped in v0.8)
- Reintroducing local Whisper/Ollama

---

## Supporting documents

| Document | Purpose |
|----------|---------|
| [roadmap_v0.7_to_v1.0.md](roadmap_v0.7_to_v1.0.md) | Phased roadmap (complete) |
| [future_considerations.md](future_considerations.md) | Deferred backlog |
| [aws-deployment.md](aws-deployment.md) | AWS architecture |
| [../developer/aws-operations.md](../developer/aws-operations.md) | Deploy / pause / smoke |
| [../developer/architecture.md](../developer/architecture.md) | Code architecture |
| **aws-backbone** | IAM / OIDC only |
