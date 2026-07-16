# Planning

Active planning for the **Relationship Reasoning Engine** after **v0.7.0**.

## Canonical set

| Document | Purpose |
|----------|---------|
| **[implementing.md](implementing.md)** | Active execution tracker (currently **v0.8**) |
| **[roadmap_v0.7_to_v1.0.md](roadmap_v0.7_to_v1.0.md)** | Phased roadmap v0.7 → v1.0 with acceptance criteria |
| **[future_considerations.md](future_considerations.md)** | Deferred / later backlog (do not delete ideas — defer them) |
| **[golden_transcript_fixtures.md](golden_transcript_fixtures.md)** | Golden transcript layout, metadata/assertions, pytest expectations |
| **[completed.md](completed.md)** | Shipped capabilities |
| **[backlog.md](backlog.md)** | Index into future considerations |

**Do not** revive archived MVP plans as the task tracker.

## Architecture / product / evaluation plans

| Document | Purpose |
|----------|---------|
| [../architecture/ontology_v1.md](../architecture/ontology_v1.md) | Canonical construct & relationship vocabulary (**shipped** v0.7) |
| [../architecture/structured_persistence_plan.md](../architecture/structured_persistence_plan.md) | Normalized findings/constructs/graph (**v0.8 active**) |
| [../architecture/workflow_dag_plan.md](../architecture/workflow_dag_plan.md) | DAG workflow engine (v1.0) |
| [../product/transcript_preparation_workspace.md](../product/transcript_preparation_workspace.md) | Transcript review before analysis (**shipped** v0.7) |
| [../product/safety_aware_report_mode.md](../product/safety_aware_report_mode.md) | High-risk report framing (v1.0) |
| [../evaluation/golden_fixture_evaluation_plan.md](../evaluation/golden_fixture_evaluation_plan.md) | Fixtures & eval loop (**shipped** foundation v0.7) |
| [../evaluation/golden_manual_rubric.md](../evaluation/golden_manual_rubric.md) | Human review rubric |

## AWS & evaluations

| Document | Purpose |
|----------|---------|
| **[aws-deployment.md](aws-deployment.md)** | AWS dev architecture, backbone, network, models |
| **[llm-evaluation-bedrock.md](llm-evaluation-bedrock.md)** | Bedrock decision (AWS-1b) |
| **[asr-evaluation-transcribe.md](asr-evaluation-transcribe.md)** | Transcribe decision (AWS-1c) |
| **[log-redaction.md](log-redaction.md)** | CloudWatch redaction (P1-3c) |

Ops: [../developer/aws-operations.md](../developer/aws-operations.md) · Terraform: [../../infra/dev/README.md](../../infra/dev/README.md) · **Pause AWS when idle**

## History

| Path | Purpose |
|------|---------|
| **[archived/](archived/)** | Superseded MVP / post-v0.3 plans (read-only) |

**Design anchors:** [../design/01_product_vision_and_scope.md](../design/01_product_vision_and_scope.md) · [../design/04_knowledge_ontology.md](../design/04_knowledge_ontology.md) · [../design/03_domain_model.md](../design/03_domain_model.md)
