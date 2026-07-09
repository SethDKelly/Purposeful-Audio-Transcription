# 08 — Workflow Engine

## Purpose

The workflow engine orchestrates analysis suites. It decides which modules run, in what order, what dependencies exist, and how outputs are passed into synthesis.

## Workflows vs Modules

A module is one analytical lens.

A workflow is a sequence or graph of modules.

## Initial Workflows

### Quick Review

Modules:

- Relationship Conversation Analysis
- NVC Analysis
- Bias Mini-Audit

Goal:

Fast, practical communication insight.

### Mediation Workflow

Modules:

- Relationship Conversation Analysis
- Mediation Analysis
- Emotional Needs & Values
- Synthesis

Goal:

Clarify issues, interests, and possible agreements.

### Clinical Exploration Workflow

Modules:

- Relationship Conversation Analysis
- Cognitive Analysis
- Psychological Formulation
- Attachment Matrix
- Trauma-Informed Analysis
- Bias Audit
- Synthesis

Goal:

Generate careful exploratory hypotheses.

### Full Multidisciplinary Suite

Modules:

- Relationship Conversation Analysis
- Psychological Formulation
- Cognitive Analysis
- Systems Analysis
- Mediation Analysis
- Gottman Analysis
- NVC Analysis
- Attachment Matrix
- Trauma-Informed Analysis
- Emotional Needs & Values
- Narrative Analysis
- Bias & Reliability Audit
- Meta-Synthesis

Goal:

Comprehensive evidence-weighted multidisciplinary report.

## Full Suite Dependency Graph

```text
Transcript Preprocessing
  ↓
Evidence Index
  ↓
Observable Modules
  ├─ Relationship Conversation Analysis
  ├─ Mediation Analysis
  └─ Gottman Analysis
  ↓
Interpretive Modules
  ├─ Cognitive Analysis
  ├─ Psychological Formulation
  ├─ Attachment Matrix
  └─ Trauma-Informed Analysis
  ↓
Relational / Meaning Modules
  ├─ Systems Analysis
  ├─ NVC Analysis
  ├─ Emotional Needs & Values
  └─ Narrative Analysis
  ↓
Bias & Reliability Audit
  ↓
Meta-Synthesis
```

## Parallelization

Many modules can run in parallel once the evidence index is available.

For MVP:

- Run observable modules first
- Run remaining modules in parallel
- Run bias audit and meta-synthesis last

## Workflow Run States

```ts
type WorkflowRunStatus =
  | 'created'
  | 'preprocessing'
  | 'running_modules'
  | 'synthesizing'
  | 'completed'
  | 'failed'
  | 'cancelled';
```

## Module Run States

```ts
type ModuleRunStatus =
  | 'queued'
  | 'running'
  | 'validating'
  | 'completed'
  | 'failed'
  | 'retrying';
```

## Synthesis Inputs

Meta-synthesis should receive:

- all module summaries
- structured findings
- evidence links
- confidence labels
- bias audit output

It should not reanalyze the transcript from scratch unless explicitly allowed.

## MVP Implementation

Use a simple workflow runner:

1. Create workflow run
2. Create module run records
3. Execute modules sequentially or with limited parallelism
4. Validate outputs
5. Run synthesis
6. Mark workflow complete

Add queues later.
