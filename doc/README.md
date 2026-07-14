# Documentation index

**Relationship Reasoning Engine (RRE)** — local analysis + **v0.5.1** AWS cloud cutover on `main`.

| Audience | Start here |
|----------|------------|
| **Users (local)** | [user/getting-started.md](user/getting-started.md) → [user/user-guide.md](user/user-guide.md) |
| **Developers** | [developer/development.md](developer/development.md) → [developer/architecture.md](developer/architecture.md) |
| **AWS operators** | [developer/aws-operations.md](developer/aws-operations.md) · [planning/aws-deployment.md](planning/aws-deployment.md) · [../infra/dev/README.md](../infra/dev/README.md) |
| **Active plan** | [planning/implementing.md](planning/implementing.md) |

---

## User documentation

| Document | Description |
|----------|-------------|
| [user/getting-started.md](user/getting-started.md) | Install, configure, first local run |
| [user/user-guide.md](user/user-guide.md) | Streamlit workflow, exploration, exports |
| [user/deployment.md](user/deployment.md) | Local private-use deploy, backup, upgrade |
| [user/model-setup.md](user/model-setup.md) | Ollama models and per-module overrides |

## Developer documentation

| Document | Description |
|----------|-------------|
| [developer/development.md](developer/development.md) | Local setup, tests, project layout |
| [developer/architecture.md](developer/architecture.md) | Services, data flow, extension points |
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

Canonical task tracking is three documents. Everything else is architecture, evaluation notes, or history.

| Document | Description |
|----------|-------------|
| [planning/README.md](planning/README.md) | Planning index |
| [planning/completed.md](planning/completed.md) | Shipped capabilities |
| [planning/implementing.md](planning/implementing.md) | Active priorities (Tier 1 → 3) |
| [planning/backlog.md](planning/backlog.md) | Future / deferred |
| [planning/aws-deployment.md](planning/aws-deployment.md) | AWS architecture and backbone integration |
| [planning/llm-evaluation-bedrock.md](planning/llm-evaluation-bedrock.md) | Bedrock LLM decision (AWS-1b) |
| [planning/asr-evaluation-transcribe.md](planning/asr-evaluation-transcribe.md) | Whisper vs Transcribe (AWS-1c) |
| [planning/log-redaction.md](planning/log-redaction.md) | CloudWatch redaction design (P1-3c) |
| [planning/archived/](planning/archived/) | Superseded planning docs |

## Releases

| Document | Description |
|----------|-------------|
| [releases/v0.5.1.md](releases/v0.5.1.md) | **Canonical** — AWS cloud cutover |
| [releases/v0.3.0.md](releases/v0.3.0.md) | Post-MVP release |
| [releases/v0.2.0.md](releases/v0.2.0.md) | MVP release |

## History

| Path | Role |
|------|------|
| [archived/](archived/) | Pre-RRE / early backlog history |
| [planning/archived/](planning/archived/) | Superseded planning docs |

**Do not** add new tasks to archived files — use [planning/implementing.md](planning/implementing.md) or [planning/backlog.md](planning/backlog.md).
