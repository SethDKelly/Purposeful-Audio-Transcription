# Documentation index

**Relationship Reasoning Engine (RRE)** — AWS-only (Bedrock + Transcribe + ECS + RDS). Canonical release **v1.0.0** on `main`.

| Audience | Start here |
|----------|------------|
| **Operators / users** | [user/getting-started.md](user/getting-started.md) → [user/user-guide.md](user/user-guide.md) |
| **Developers** | [developer/development.md](developer/development.md) → [developer/architecture.md](developer/architecture.md) |
| **AWS ops** | [developer/aws-operations.md](developer/aws-operations.md) · [developer/aws-deployment.md](developer/aws-deployment.md) · [../infra/dev/README.md](../infra/dev/README.md) |
| **Active plan** | [planning/phases/10](planning/phases/10_v2_1_cutover_auth_and_graph_depth.md) (**v2.1**) · [planning/deferred_backlog.md](planning/deferred_backlog.md) |

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
| [developer/aws-deployment.md](developer/aws-deployment.md) | AWS architecture and backbone integration |
| [developer/log-redaction.md](developer/log-redaction.md) | CloudWatch redaction design |

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
| [planning/phases/](planning/phases/) | **Active roadmap** (current: v2.1) |
| [planning/deferred_backlog.md](planning/deferred_backlog.md) | Prioritized deferred / dependency-gated work |
| [planning/general_backlog.md](planning/general_backlog.md) | Unprioritized ideas (no commitment) |
| [archived/planning/](archived/planning/) | Completed Phases 1–54 + executive summary |

## Architecture / product / evaluation

| Document | Description |
|----------|-------------|
| [architecture/ontology_v1.md](architecture/ontology_v1.md) | Ontology vocabulary v1 (**shipped** in v0.7) |
| [architecture/structured_persistence_plan.md](architecture/structured_persistence_plan.md) | v0.8 persistence |
| [architecture/workflow_dag_plan.md](architecture/workflow_dag_plan.md) | v1.0 DAG workflows |
| [product/transcript_preparation_workspace.md](product/transcript_preparation_workspace.md) | Transcript prep (**shipped** in v0.7) |
| [product/safety_aware_report_mode.md](product/safety_aware_report_mode.md) | v1.0 safety-aware reports |
| [evaluation/golden_fixture_evaluation_plan.md](evaluation/golden_fixture_evaluation_plan.md) | Golden fixtures |
| [evaluation/golden_transcript_fixtures.md](evaluation/golden_transcript_fixtures.md) | Golden fixture layout |
| [evaluation/golden_manual_rubric.md](evaluation/golden_manual_rubric.md) | Human review rubric |
| [evaluation/llm-evaluation-bedrock.md](evaluation/llm-evaluation-bedrock.md) | Bedrock LLM decision |
| [evaluation/asr-evaluation-transcribe.md](evaluation/asr-evaluation-transcribe.md) | Whisper vs Transcribe |

## Releases

| Document | Description |
|----------|-------------|
| [releases/v1.0.0.md](releases/v1.0.0.md) | **Canonical** — worker, DAG, custom workflows, safety mode |
| [releases/v0.9.0.md](releases/v0.9.0.md) | Cases, longitudinal, feedback, report package |
| [releases/v0.8.0.md](releases/v0.8.0.md) | Structured persistence + graph |
| [releases/v0.7.0.md](releases/v0.7.0.md) | Trust UAT, transcript prep, ontology, telemetry |
| [releases/v0.6.0.md](releases/v0.6.0.md) | Trust + workflows + AWS-only |
| [releases/v0.5.1.md](releases/v0.5.1.md) | AWS cloud cutover |
| [releases/v0.3.0.md](releases/v0.3.0.md) | Post-MVP release |
| [releases/v0.2.0.md](releases/v0.2.0.md) | MVP release |

## History

| Path | Role |
|------|------|
| [archived/](archived/) | Pre-RRE / early backlog history |
| [archived/planning/](archived/planning/) | Executive roadmap + completed phases 1–49 |

**Do not** add new tasks to archived files — use [planning/deferred_backlog.md](planning/deferred_backlog.md) or [planning/general_backlog.md](planning/general_backlog.md).
