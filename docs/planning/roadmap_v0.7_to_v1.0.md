# Roadmap v0.7 → v1.0 — Relationship Reasoning Engine

Canonical phased roadmap after **v0.6.0**. Active execution tracker: [implementing.md](implementing.md). Deferred ideas: [future_considerations.md](future_considerations.md). Completed: [completed.md](completed.md).

## Guiding principle

The app already has enough **analytical breadth**. Do **not** prioritize more analysis modules yet.

```text
security
→ transcript quality
→ ontology population
→ structured persistence
→ graph reasoning
→ cases
→ workflow hardening
```

Evolve from a prompt-orchestration app into a structured **relationship reasoning engine** where claims, evidence, confidence, constructs, and relationships are first-class product objects.

**Durable assets:** schemas · module specs · workflow definitions · ontology · knowledge graph · structured findings · evidence links · evaluation fixtures · UI exploration patterns.  
**Prompts** remain important but are replaceable implementation artifacts.

## Near-term product priorities

| Prioritize | Avoid for now |
|------------|---------------|
| Trust and safety | More prompts before structure is ready |
| Transcript preparation quality | More report prose before structured findings are robust |
| Evidence traceability | UI visual polish before evidence/graph UX works |
| Ontology and structured reasoning | Advanced customization before workflow execution is durable |
| Graph persistence | |
| Case-level longitudinal insight | |
| Durable workflow execution | |
| Evaluation and reliability | |

## Release sequence

| Release | Theme |
|---------|--------|
| **[v0.7](#v07--trust-transcript-preparation-and-ontology-foundation)** | Trust, transcript preparation, ontology foundation |
| **[v0.8](#v08--structured-persistence-and-graph-reasoning)** | Normalized findings/constructs/relationships + graph reasoning |
| **[v0.9](#v09--cases-and-longitudinal-analysis)** | Cases, longitudinal analysis, feedback loops |
| **[v1.0](#v10--workflow-hardening-and-external-readiness)** | Durable workers, DAG, custom workflows, safety-aware mode |

Supporting plans: [../architecture/ontology_v1.md](../architecture/ontology_v1.md) · [../architecture/structured_persistence_plan.md](../architecture/structured_persistence_plan.md) · [../architecture/workflow_dag_plan.md](../architecture/workflow_dag_plan.md) · [../product/transcript_preparation_workspace.md](../product/transcript_preparation_workspace.md) · [../product/safety_aware_report_mode.md](../product/safety_aware_report_mode.md) · [../evaluation/golden_fixture_evaluation_plan.md](../evaluation/golden_fixture_evaluation_plan.md)

---

## v0.7 — Trust, Transcript Preparation, and Ontology Foundation

**Strategic goal:** Safer, more trustworthy system prepared for structured reasoning — not more analytical lenses.

### Priority 1 — Secure External UAT Readiness

**Rationale:** Sensitive relationship transcripts/audio make security and privacy product-critical.

| Task | Links / notes |
|------|----------------|
| HTTPS/TLS on ALB + HTTP→HTTPS redirect | [aws-deployment.md](aws-deployment.md), `infra/dev/alb.tf` |
| Streamlit sends configured `X-API-Key` | `ui/api_client.py`, Secrets Manager `API_KEY` |
| Generic user-facing errors (no raw stack traces) | API exception handlers in `backend/main.py` |
| Backend request / correlation IDs | `backend/core/logging_config.py`; surface in UI errors |
| Privacy and retention notice (user-facing) | Streamlit + [log-redaction.md](log-redaction.md) |
| Transcript/audio deletion controls | Existing cascade DELETE — expose clearly in UI |
| Export redaction option (default-on for sensitive exports) | Export paths in API/UI |

**Acceptance:** External traffic can use HTTPS; UI→API auth header present when configured; errors are generic + request ID; users understand retention and can delete supported artifacts.

**Tests:** API auth integration; error response contract; HTTPS deploy checklist; manual UAT upload→workflow→export→delete.

### Priority 2 — Transcript Preparation Workspace

**Rationale:** Analysis quality depends on transcript quality.

| Task | Links / notes |
|------|----------------|
| Review screen before workflow execution | `ui/streamlit_app.py` prepare step |
| Edit speaker labels and turn text | Transcript APIs / `transcript_service` |
| Split/merge turns if feasible; delete irrelevant turns | |
| Mark sections excluded from analysis | Evidence index must honor exclusions |
| Regenerate quote IDs / evidence index after edits | `evidence` / parser services |
| Transcript quality warnings | |
| Explicit **Ready to Analyze** confirmation | |

**Acceptance:** User reviews before analysis; edited transcript feeds evidence index + workflow; quote IDs stable within approved version; analysis does not run on unapproved generated transcript unless user intentionally skips review.

**Tests:** Edit operation unit tests; evidence index regeneration; quote ID consistency; UI approval flow.

**Product note:** [../product/transcript_preparation_workspace.md](../product/transcript_preparation_workspace.md)

### Priority 3 — Ontology Vocabulary v1

**Rationale:** Shared vocabulary before graph persistence.

| Task | Links / notes |
|------|----------------|
| Ontology definition file | Prefer `config/ontology/` + [../architecture/ontology_v1.md](../architecture/ontology_v1.md); complements [../design/04_knowledge_ontology.md](../design/04_knowledge_ontology.md) |
| Canonical construct types (stable IDs + descriptions) | See ontology_v1.md minimum set |
| Canonical relationship types | See ontology_v1.md minimum set |
| Module specs can reference ontology types | `config/modules/*.yaml` |

**Acceptance:** Construct/relationship types documented with stable IDs; modules can reference them; ontology loads cleanly.

**Tests:** Ontology load; module-declared types exist; fixture relationship types exist in ontology.

### Priority 4 — Module Construct Expectations

**Rationale:** Graph depends on modules emitting structured constructs.

| Task | Links / notes |
|------|----------------|
| Extend module metadata (`expected_constructs`, minimums) | Module registry + YAML schema |
| Soft validation warnings for weak construct coverage | `module_output_validator` — warn, not hard-fail by default |
| Record coverage in logs / module run metadata | |

**Acceptance:** Specs declare expected constructs where applicable; weak coverage is a warning visible in metadata/logs.

**Tests:** Spec validation; missing required constructs; regression fixture.

### Priority 5 — Golden Fixture and Evaluation Foundation

**Rationale:** Regression protection before the module set grows.

| Task | Links / notes |
|------|----------------|
| 5–10 golden / synthetic transcripts | `tests/fixtures/transcripts/` |
| Automated checks (JSON, evidence, confidence ceilings, safety language, construct count/coverage, completion) | [../evaluation/golden_fixture_evaluation_plan.md](../evaluation/golden_fixture_evaluation_plan.md) |
| Manual review rubric | |

**Acceptance:** Fixtures run locally; failures easy to inspect; each module evaluable on ≥1 fixture; prompt/compiler changes comparable to prior results.

**Tests:** Fixture validity pytest; snapshot/contract tests; safety-language lint.

### Priority 6 — Cost, Latency, and Module Telemetry

**Rationale:** Telemetry before optimization.

| Task | Links / notes |
|------|----------------|
| Per-module: model, tokens, cache tokens, latency, retries, validation failures, estimated cost, finding/construct/quote counts | Module run persistence |
| Workflow summary: total estimated cost + duration | API + UI |

**Acceptance:** Metadata includes cost/latency fields; workflow summary aggregates; failures include validation reasons.

**Tests:** Metadata persistence; summary aggregation.

---

## v0.8 — Structured Persistence and Graph Reasoning

**Status:** **Released** as [v0.8.0](../releases/v0.8.0.md) (July 2026).

**Strategic goal:** Promote findings, constructs, evidence, confidence, and relationships from JSON blobs into first-class persistent objects.

Plan detail: [../architecture/structured_persistence_plan.md](../architecture/structured_persistence_plan.md)

| Priority | Focus |
|----------|--------|
| **1** | Normalized findings persistence |
| **2** | Normalized constructs persistence |
| **3** | Construct relationship persistence |
| **4** | Graph merge / deduplication |
| **5** | Deterministic convergence and confidence scoring |
| **6** | Graph exploration UI (table-first OK) |
| **7** | Synthesis over structured objects |

---

## v0.9 — Cases and Longitudinal Analysis

**Status:** **Released** as [v0.9.0](../releases/v0.9.0.md) (July 2026).

**Strategic goal:** Multiple transcripts over time; longitudinal reasoning (high product differentiation after graph persistence).

| Priority | Focus |
|----------|--------|
| **1** | Case data model |
| **2** | Case dashboard |
| **3** | Longitudinal comparison |
| **4** | Longitudinal synthesis module |
| **5** | Report package export (manifest + evidence appendix) |
| **6** | User feedback / analyst review loop |

---

## v1.0 — Workflow Hardening and External Readiness

**Status:** **Active** — tracker [implementing.md](implementing.md).

**Strategic goal:** Reliable enough for external users, longer workflows, custom suites, production-like operation.

Plan detail: [../architecture/workflow_dag_plan.md](../architecture/workflow_dag_plan.md) · [../product/safety_aware_report_mode.md](../product/safety_aware_report_mode.md)

| Priority | Focus |
|----------|--------|
| **1** | Dedicated worker service (jobs survive API; cancel; timeout; retries) |
| **2** | Workflow DAG engine (dependencies, parallel groups, synthesis gates) |
| **3** | Custom workflow builder |
| **4** | Long transcript strategy (chunk-aware; no silent head/tail-only) |
| **5** | Safety-aware report mode |
| **6** | Production-grade API and documentation |

---

## Mapping from prior plan IDs

| Prior ID / theme | Where now |
|------------------|-----------|
| HTTPS / TLS, P2-R2 API key UI | **v0.7 P1** |
| P2-O ontology / construct population | **v0.7 P3–P4** (foundation) → **v0.8** (persistence) |
| P1-5 golden fixtures / P1-6 burn-in fixtures | **v0.7 P5** |
| Module duration / cost telemetry | **v0.7 P6** |
| P2-P cases / longitudinal | **v0.9** |
| P2-R finding feedback / supervision export | **v0.9 P5–P6** (aligned) |
| P2-Q custom workflows | **v1.0 P3** |
| Dedicated worker / advanced cancel / DAG | **v1.0 P1–P2** |
| P2-A multi-file audio stitch | [future_considerations.md](future_considerations.md) |
| React SPA, extra analysis prompts, Haiku routing, etc. | [future_considerations.md](future_considerations.md) |
