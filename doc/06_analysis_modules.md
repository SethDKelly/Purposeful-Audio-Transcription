# 06 — Analysis Modules

## Purpose

Analysis modules are the application’s reasoning lenses. Each module should be defined by metadata, required inputs, output schema, and prompt template components.

## Module Registry

Initial modules:

1. Relationship Conversation Analysis
2. Exploratory Psychological Formulation
3. Cognitive Distortions & Core Beliefs
4. Systems & Family Systems Analysis
5. Conflict Resolution & Mediation
6. Gottman Method Analysis
7. Nonviolent Communication Analysis
8. Attachment Interaction Matrix
9. Trauma-Informed Communication Analysis
10. Emotional Needs & Values Analysis
11. Narrative Identity & Meaning-Making Analysis
12. Bias, Reliability & Epistemic Quality Audit
13. Integrative Meta-Synthesis

## Module Metadata Example

```yaml
id: systems_analysis
name: Systems & Family Systems Analysis
version: 1.0.0
primary_lens: Systems Theory
analytical_level: relational
unit_of_analysis: relationship
primary_question: What feedback loops maintain the interaction?
secondary_questions:
  - What roles appear in the system?
  - What balancing loops reduce escalation?
  - What leverage points could change the pattern?
required_constructs:
  - interaction_cycle
  - feedback_loop
  - role
  - boundary
  - leverage_point
output_schema: module_output_v1
recommended_companions:
  - nvc_analysis
  - attachment_interaction_matrix
  - emotional_needs_values
inference_depth: medium
confidence_ceiling: moderate
dependencies:
  - transcript_preprocessing
```

## Module Categories

### Observable Modules

Best first-pass modules:

- Relationship Conversation Analysis
- Mediation Analysis
- Gottman Analysis

These rely primarily on direct transcript evidence.

### Individual/Internal Modules

- Psychological Formulation
- Cognitive Analysis
- Attachment Matrix
- Trauma-Informed Analysis

These produce more tentative hypotheses.

### Relational/Meaning Modules

- Systems Analysis
- NVC Analysis
- Emotional Needs & Values
- Narrative Analysis

These connect behavior, meaning, and relationship dynamics.

### Methodological/Integrative Modules

- Bias & Reliability Audit
- Meta-Synthesis

These calibrate and integrate results.

## Module Output Requirements

Every module should produce:

1. Executive summary
2. Structured findings
3. Evidence links
4. Confidence labels
5. Alternative explanations
6. Limitations
7. Practical recommendations where appropriate
8. Raw readable report

## Module Design Rule

Each module should answer one primary question. If a module starts answering too many questions, split it or move shared content into the synthesis layer.

## Adding New Modules

To add a module:

1. Define metadata
2. Define required constructs
3. Define output schema extensions if needed
4. Write or generate prompt template
5. Add tests with sample transcripts
6. Add to one or more workflows
7. Define companion/overlap metadata

## Overlap Management

Each module should declare expected overlap with others:

```yaml
overlap:
  communication_analysis: low
  psychological_formulation: moderate
  nvc_analysis: low
```

This helps suite design avoid unnecessary redundancy.
