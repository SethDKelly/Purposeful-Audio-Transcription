# 03 — Domain Model

## Purpose

The domain model defines the core concepts the application reasons about. This is more important than the prompts because prompts can evolve while the domain model remains stable.

## Core Entities

### Transcript

Represents the entire conversation provided by the user.

Fields:

- id
- title
- raw_text
- created_at
- source_type
- language
- metadata

### Speaker

Represents a participant in the transcript.

Fields:

- id
- transcript_id
- label
- display_name
- role_optional

### Turn

Represents one speaker contribution.

Fields:

- id
- transcript_id
- speaker_id
- turn_index
- text
- start_time_optional
- end_time_optional

### Evidence Quote

A canonical reference to a specific transcript excerpt.

Fields:

- id
- transcript_id
- turn_id
- quote_text
- speaker_id
- quote_index
- surrounding_context

### Finding

A structured analytical claim produced by a module.

Fields:

- id
- module_run_id
- finding_type
- title
- summary
- confidence
- evidence_quote_ids
- alternative_explanations
- limitations

### Construct

A conceptual object identified in analysis.

Examples:

- need
- value
- emotion
- belief
- repair attempt
- escalation point
- interaction cycle
- narrative
- assumption
- attribution
- leverage point

### Analysis Module

A registered analytical lens.

Fields:

- id
- name
- version
- primary_lens
- analytical_level
- unit_of_analysis
- input_requirements
- output_schema

### Module Run

One execution of one module against one transcript.

Fields:

- id
- module_id
- transcript_id
- workflow_run_id
- status
- model_used
- prompt_version
- raw_output
- parsed_output
- created_at

### Workflow

A defined suite of modules and dependencies.

Fields:

- id
- name
- version
- module_sequence
- dependency_graph
- description

### Workflow Run

One execution of a workflow.

Fields:

- id
- workflow_id
- transcript_id
- status
- started_at
- completed_at
- error_log

### Synthesis Report

Integrated output across module runs.

Fields:

- id
- workflow_run_id
- executive_summary
- high_confidence_findings
- moderate_confidence_findings
- exploratory_hypotheses
- integrated_model
- recommendations
- limitations

## Core Construct Types

### Observation

A direct, evidence-linked fact from the transcript.

### Interpretation

Meaning assigned to an observation.

### Emotion

An observable or inferred emotional state.

### Need

A possible underlying relational or psychological need.

### Value

A principle or priority shaping preferences.

### Belief

A possible assumption or cognitive model.

### Narrative

A meaning-making story about self, partner, or relationship.

### Repair Attempt

A behavior that may restore connection or reduce conflict.

### Escalation Point

A moment where conflict intensity increases.

### Interaction Cycle

A recurring sequence of actions and responses.

### Feedback Loop

A self-reinforcing relational process.

### Intervention

A suggested behavioral or communication change.

### Uncertainty

A limitation or unresolved interpretive question.

## Relationship Between Entities

```text
Transcript has many Turns
Turn has many Evidence Quotes
Workflow Run has many Module Runs
Module Run produces many Findings
Finding references many Evidence Quotes
Finding may instantiate many Constructs
Synthesis Report aggregates Findings
```

## Design Rule

Every non-obvious conclusion should be represented as a Finding with:

- evidence
- confidence
- source module
- alternative explanations
- limitations

This makes the application auditable.
