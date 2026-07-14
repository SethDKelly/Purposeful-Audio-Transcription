# Planning

Active planning uses three documents. Architecture, evaluation notes, and history are separate.

## Canonical trio

| Document | Purpose |
|----------|---------|
| **[completed.md](completed.md)** | Shipped capabilities through the current milestone |
| **[implementing.md](implementing.md)** | Active work — Tier 1 → 2 → 3; **quality gaps + post-burn-in sequence** |
| **[backlog.md](backlog.md)** | Future, nice-to-have, and deferred items |

Use **implementing.md** as the plan to follow after P1-4f burn-in. Do not revive archived MVP plans as the task tracker.

## Architecture and evaluations

| Document | Purpose |
|----------|---------|
| **[aws-deployment.md](aws-deployment.md)** | AWS dev architecture, backbone, network stages, model strategy |
| **[llm-evaluation-bedrock.md](llm-evaluation-bedrock.md)** | Bedrock Converse + Sonnet decision (AWS-1b) |
| **[asr-evaluation-transcribe.md](asr-evaluation-transcribe.md)** | Whisper vs Amazon Transcribe criteria (AWS-1c) |
| **[log-redaction.md](log-redaction.md)** | CloudWatch redaction design (P1-3c) |

Ops runbook: [../developer/aws-operations.md](../developer/aws-operations.md) · Terraform: [../../infra/dev/README.md](../../infra/dev/README.md) · **Pause AWS when idle** (ECS→0, stop RDS)

## History

| Path | Purpose |
|------|---------|
| **[archived/](archived/)** | Superseded MVP / post-v0.3 plans (read-only) |

**Design anchors:** [../design/01_product_vision_and_scope.md](../design/01_product_vision_and_scope.md) · [../design/04_knowledge_ontology.md](../design/04_knowledge_ontology.md) · [../design/11_ui_ux_design.md](../design/11_ui_ux_design.md)
