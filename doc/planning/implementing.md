# Implementing — Active Priorities

Material work in flight for the **Relationship Reasoning Engine (RRE)** after **v0.6.0**.

| | |
|---|---|
| **Status** | **v0.7 in progress** — Trust, transcript preparation, ontology foundation |
| **Canonical roadmap** | [roadmap_v0.7_to_v1.0.md](roadmap_v0.7_to_v1.0.md) |
| **Deferred ideas** | [future_considerations.md](future_considerations.md) |
| **Completed** | [completed.md](completed.md) |
| **Branch** | `main` @ v0.6.0 (phase branches per priority) |
| **Strategy** | **AWS only** — Bedrock + Transcribe + ECS + RDS (`521018312783`, `us-east-2`) |
| **Cost control** | **Pause AWS when idle** — [../developer/aws-operations.md](../developer/aws-operations.md) |
| **Deploy policy** | Deploy on **minor-version completion** (tag / manual), not every main push |
| **Architecture** | [aws-deployment.md](aws-deployment.md) |

**Scope rule:** Follow the roadmap sequence. Do **not** add analysis modules for breadth. Prefer structure, trust, and evidence quality.

**North star:**

```text
Domain Model → Ontology → Module Definitions → Workflow Engine → Prompt Compiler
  → Structured Findings → Synthesis Engine → Interactive UI
```

Prompts are replaceable; enduring assets are schemas, ontology, evidence/confidence, workflow design, structured data, and evaluation fixtures.

---

## Guiding sequence

```text
security → transcript quality → ontology → structured persistence
  → graph reasoning → cases → workflow hardening
```

| Release | Theme | Status |
|---------|--------|--------|
| **v0.6.0** | Trust controls + full/research workflows + AWS-only | **Released** |
| **v0.7** | Secure UAT + transcript prep + ontology foundation | **Active** |
| **v0.8** | Normalized findings/constructs/relationships + graph | Pending |
| **v0.9** | Cases + longitudinal + feedback | Pending |
| **v1.0** | Workers + DAG + custom workflows + safety mode | Pending |

---

## Immediate next steps

```text
[x] v0.7 Priority 1 — Secure external UAT readiness (HTTPS, API key UI, safe errors, request IDs, privacy/deletion/redaction)
[x] v0.7 Priority 2 — Transcript preparation workspace
[x] v0.7 Priority 3 — Ontology vocabulary v1
[x] v0.7 Priority 4 — Module construct expectations
[x] v0.7 Priority 5 — Golden fixtures + evaluation foundation (GT001/GT002 + rubric; expand count later)
[x] v0.7 Priority 6 — Cost / latency / module telemetry
[ ] Release v0.7.0 · Deploy once · Pause AWS when idle · then v0.8
```

**Standing ops:** Pause when idle. **Deploy only on minor-version completion** (tag `vX.Y.Z` or manual **Deploy to AWS dev**). Intra-v0.7 commits do not auto-deploy. Full product UAT after security + prep land.

---

## v0.7 — Active work

Detail and acceptance criteria: [roadmap_v0.7_to_v1.0.md](roadmap_v0.7_to_v1.0.md#v07--trust-transcript-preparation-and-ontology-foundation).

### Priority 1 — Secure External UAT Readiness

| # | Task | Status | Links |
|---|------|--------|-------|
| V07-1a | HTTPS/TLS on ALB + HTTP→HTTPS redirect | Pending — Terraform ready when `acm_certificate_arn` set; HTTP-only until ACM/domain available | `infra/dev/alb.tf`, ACM |
| V07-1b | UI sends `X-API-Key` when configured | Done (code) — ECS injects shared secret | `ui/api_client.py`, Secrets Manager |
| V07-1c | Generic user-facing API/UI errors (no stack traces) | Done | `backend/main.py` |
| V07-1d | Request / correlation IDs in API + UI errors | Done | logging middleware + error payload |
| V07-1e | Privacy & retention notice (user-facing) | Done | Streamlit captions |
| V07-1f | Transcript/audio deletion controls in UI | Done (clarify caption) | cascade DELETE exists |
| V07-1g | Export redaction option (default-on) | Done | export checkbox default True |

**Acceptance / tests:** see roadmap Priority 1.

### Priority 2 — Transcript Preparation Workspace

| # | Task | Status | Links |
|---|------|--------|-------|
| V07-2a–g | Review, edit speakers/turns, exclude sections, regen evidence, quality warnings, Ready to Analyze | Done (split/merge deferred) | [../product/transcript_preparation_workspace.md](../product/transcript_preparation_workspace.md) |

### Priority 3 — Ontology Vocabulary v1

| # | Task | Status | Links |
|---|------|--------|-------|
| V07-3a–d | Config ontology + construct/relationship types + module references | Done | [../architecture/ontology_v1.md](../architecture/ontology_v1.md), `config/ontology/` |

### Priority 4 — Module Construct Expectations

| # | Task | Status | Links |
|---|------|--------|-------|
| V07-4a–c | `expected_constructs` metadata + soft coverage warnings + metadata visibility | Done | module YAML, `module_output_validator`, `validation_warnings` on module runs |

### Priority 5 — Golden Fixture & Evaluation Foundation

| # | Task | Status | Links |
|---|------|--------|-------|
| V07-5a–c | 5–10 fixtures, automated checks, manual rubric | **Foundation done** — GT001/GT002 + signal tests + [../evaluation/golden_manual_rubric.md](../evaluation/golden_manual_rubric.md); expand fixture count opportunistically | [../evaluation/golden_fixture_evaluation_plan.md](../evaluation/golden_fixture_evaluation_plan.md) |

### Priority 6 — Cost, Latency & Module Telemetry

| # | Task | Status | Links |
|---|------|--------|-------|
| V07-6a–b | Per-module telemetry fields + workflow cost/duration summary | Done | `ModuleRun.telemetry`, `WorkflowRun.telemetry_summary` |

---

## Later releases (summary only)

Do not start these until the prior release priorities are done unless a validated UAT blocker forces a carve-out.

| Release | Priorities | Plan docs |
|---------|------------|-----------|
| **v0.8** | Findings → constructs → relationships → merge → scoring → graph UI → structured synthesis | [../architecture/structured_persistence_plan.md](../architecture/structured_persistence_plan.md) |
| **v0.9** | Case model → dashboard → longitudinal compare/synthesis → export package → feedback loop | roadmap §v0.9 |
| **v1.0** | Worker → DAG → custom builder → long transcript → safety mode → prod docs | [../architecture/workflow_dag_plan.md](../architecture/workflow_dag_plan.md), [../product/safety_aware_report_mode.md](../product/safety_aware_report_mode.md) |

---

## Product vision gaps (updated)

| Vision item | Gap | Disposition |
|-------------|-----|-------------|
| Secure client connection | HTTP-only ALB; API key unused in UI | **v0.7 P1** |
| Transcript quality before analysis | Limited prepare UX | **v0.7 P2** |
| Knowledge graph / constructs | Rarely populated; JSON blobs | **v0.7 P3–P4** → **v0.8** |
| Interactive exploration depth | No counterfactual presets | Deferred → [future_considerations.md](future_considerations.md) (after graph) |
| Longitudinal / cases | Same-transcript compare only | **v0.9** |
| Module customization | Fixed YAML workflows | **v1.0 P3** |
| Professional mode | No case files / feedback | **v0.9** |
| Multi-part recordings | No ordered stitch | Deferred → future considerations (was P2-A) |
| Durable long workflows | In-process jobs | **v1.0 P1–P2** |

---

## Quality review carry-forward (Jul 2026)

| Gap | Disposition |
|-----|-------------|
| Separate compute worker | **v1.0 P1** (was backlog) |
| Workflow cancel mid-run | **v1.0 P1** (+ basic cancel may land earlier if UAT requires) |
| Pin deps / golden fixtures | **v0.7 P5** (+ lockfile opportunistically in future considerations) |
| Construct / relationship population | **v0.7–v0.8** |
| Deploy smoke `/api/health` timeouts | Fix under **v0.7 P1** hardening / ops (prefer `/api/live` + longer health wait) |

---

## Prior tiers (v0.5–v0.6) — complete

Tier 1–2 AWS pivot, Transcribe, trust (P1-3), workflows (P1-4), AWS-only prune (P1-7), and reliability mitigations are **done**. See [completed.md](completed.md) and [../releases/v0.6.0.md](../releases/v0.6.0.md). Do not re-open unless a second-stage improvement is listed above.

---

## Decision log (active)

| Decision | Rationale |
|----------|-----------|
| **Breadth pause** | Enough modules; structure and trust next |
| **v0.7 before cases** | Secure + ontology foundation before longitudinal claims |
| **Table-first graph UI** | v0.8 explorer before fancy viz |
| **Transcript stitch deferred** | Prep workspace first; multi-file stitch later |
| **Pause AWS when idle** | Cost control |
| **AWS-only product** | No Whisper/Ollama runtime |
| **Bounded parallel modules** | Shipped v0.6; DAG makes deps explicit in v1.0 |

---

## Explicitly out of scope

- Modifying **MinneAnalytics** in aws-backbone
- Multi-user SaaS / billing / RBAC beyond API key (+ HTTPS in v0.7)
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
