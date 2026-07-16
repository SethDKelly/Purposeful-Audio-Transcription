# Documentation index

**Relationship Reasoning Engine (RRE)** — AWS-only (Bedrock + Transcribe + ECS + RDS). Canonical release **v0.8.0** on `main`.

| Audience | Start here |
|----------|------------|
| **Operators / users** | [user/getting-started.md](user/getting-started.md) → [user/user-guide.md](user/user-guide.md) |
| **Developers** | [developer/development.md](developer/development.md) → [developer/architecture.md](developer/architecture.md) |
| **AWS ops** | [developer/aws-operations.md](developer/aws-operations.md) · [planning/aws-deployment.md](planning/aws-deployment.md) · [../infra/dev/README.md](../infra/dev/README.md) |
| **Active plan** | [planning/implementing.md](planning/implementing.md) · [planning/roadmap_v0.7_to_v1.0.md](planning/roadmap_v0.7_to_v1.0.md) |

> Documentation lives under **`docs/`** (renamed from `doc/` in v0.7.0).

---

## User documentation

| Document | Description |
|----------|-------------|
| [user/getting-started.md](user/getting-started.md) | Deploy, prepare transcript, first AWS workflow |
| [user/user-guide.md](user/user-guide.md) | Streamlit workflow, preparation, exploration, exports |
| [user/deployment.md](user/deployment.md) | AWS-only deployment pointers |
| [user/model-setup.md](user/model-setup.md) | Bedrock + Transcribe |

## Developer documentation

| Document | Description |
|----------|-------------|
| [developer/development.md](developer/development.md) | pytest / tooling setup, project layout |
| [developer/architecture.md](developer/architecture.md) | Services, data flow, ontology, telemetry |
| [developer/api-reference.md](developer/api-reference.md) | REST API summary |
| [developer/contributing.md](developer/contributing.md) | Conventions, PRs, adding modules |
| [developer/aws-operations.md](developer/aws-operations.md) | CloudWatch Insights, deploy smoke, pause/resume |
| [developer/cursor-workflow.md](developer/cursor-workflow.md) | AI-assisted development notes |

## Design package

Stable product/technical design (not a task tracker):

| Doc | Topic |
|-----|-------|
| [design/01_product_vision_and_scope.md](design/01_product_vision_and_scope.md) | Vision, users, use cases |
| [design/02_system_architecture.md](design/02_system_architecture.md) | System boundaries |
| [design/03_domain_model.md](design/03_domain_model.md) | Core entities |
| [design/04_knowledge_ontology.md](design/04_knowledge_ontology.md) | Constructs and relationships |
| [design/05_data_model_and_schemas.md](design/05_data_model_and_schemas.md) | JSON and DB schemas |
| [design/06_analysis_modules.md](design/06_analysis_modules.md) | Module definitions |
| [design/07_prompt_compiler.md](design/07_prompt_compiler.md) | Prompt compilation |
| [design/08_workflow_engine.md](design/08_workflow_engine.md) | Workflow orchestration |
| [design/09_evidence_confidence_and_citations.md](design/09_evidence_confidence_and_citations.md) | Evidence model |
| [design/10_synthesis_engine.md](design/10_synthesis_engine.md) | Cross-module synthesis |
| [design/11_ui_ux_design.md](design/11_ui_ux_design.md) | UI patterns |
| [design/14_testing_evaluation_and_safety.md](design/14_testing_evaluation_and_safety.md) | Testing and safety |
| [design/16_additional_thoughts.md](design/16_additional_thoughts.md) | Design principles |

## Planning

| Document | Description |
|----------|-------------|
| [planning/README.md](planning/README.md) | Planning index |
| [planning/implementing.md](planning/implementing.md) | Active priorities (**v0.8** after v0.7.0) |
| [planning/roadmap_v0.7_to_v1.0.md](planning/roadmap_v0.7_to_v1.0.md) | Phased roadmap + acceptance criteria |
| [planning/future_considerations.md](planning/future_considerations.md) | Deferred / later backlog |
| [planning/completed.md](planning/completed.md) | Shipped capabilities |
| [planning/backlog.md](planning/backlog.md) | Backlog index → future considerations |
| [planning/aws-deployment.md](planning/aws-deployment.md) | AWS architecture and backbone integration |
| [planning/golden_transcript_fixtures.md](planning/golden_transcript_fixtures.md) | Golden fixture layout |
| [planning/llm-evaluation-bedrock.md](planning/llm-evaluation-bedrock.md) | Bedrock LLM decision |
| [planning/asr-evaluation-transcribe.md](planning/asr-evaluation-transcribe.md) | Whisper vs Transcribe |
| [planning/log-redaction.md](planning/log-redaction.md) | CloudWatch redaction design |
| [planning/archived/](planning/archived/) | Superseded planning docs |

## Architecture / product / evaluation

| Document | Description |
|----------|-------------|
| [architecture/ontology_v1.md](architecture/ontology_v1.md) | Ontology vocabulary v1 (**shipped** in v0.7) |
| [architecture/structured_persistence_plan.md](architecture/structured_persistence_plan.md) | v0.8 persistence |
| [architecture/workflow_dag_plan.md](architecture/workflow_dag_plan.md) | v1.0 DAG workflows |
| [product/transcript_preparation_workspace.md](product/transcript_preparation_workspace.md) | Transcript prep (**shipped** in v0.7) |
| [product/safety_aware_report_mode.md](product/safety_aware_report_mode.md) | v1.0 safety-aware reports |
| [evaluation/golden_fixture_evaluation_plan.md](evaluation/golden_fixture_evaluation_plan.md) | Golden fixtures |
| [evaluation/golden_manual_rubric.md](evaluation/golden_manual_rubric.md) | Human review rubric |

## Releases

| Document | Description |
|----------|-------------|
| [releases/v0.7.0.md](releases/v0.7.0.md) | **Canonical** — trust UAT, transcript prep, ontology, telemetry |
| [releases/v0.6.0.md](releases/v0.6.0.md) | Trust + workflows + AWS-only |
| [releases/v0.5.1.md](releases/v0.5.1.md) | AWS cloud cutover |
| [releases/v0.3.0.md](releases/v0.3.0.md) | Post-MVP release |
| [releases/v0.2.0.md](releases/v0.2.0.md) | MVP release |

## History

| Path | Role |
|------|------|
| [archived/](archived/) | Pre-RRE / early backlog history |
| [planning/archived/](planning/archived/) | Superseded planning docs |

**Do not** add new tasks to archived files — use [planning/implementing.md](planning/implementing.md) or [planning/backlog.md](planning/backlog.md).
