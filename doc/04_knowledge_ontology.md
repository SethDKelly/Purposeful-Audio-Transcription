# 04 — Knowledge Ontology

## Purpose

The ontology defines how analytical constructs relate to each other. It allows the application to reason across modules instead of simply displaying separate reports.

## Core Ontological Pattern

Most findings can be represented as:

```text
Evidence
  supports
Construct
  relates_to
Other Construct
  contributes_to
Outcome or Intervention
```

Example:

```text
Quote Q12
  supports
Criticism
  increases likelihood of
Defensiveness
  contributes to
Escalation Cycle
  suggests intervention
Softened Startup
```

## Construct Categories

### Behavioral Constructs

- criticism
- defensiveness
- interruption
- withdrawal
- validation
- apology
- repair attempt
- question
- clarification
- escalation

### Emotional Constructs

- frustration
- sadness
- anger
- anxiety
- confusion
- disappointment
- affection
- shame sensitivity
- fear

### Cognitive Constructs

- automatic thought
- assumption
- attribution
- mind reading
- catastrophizing
- all-or-nothing thinking
- confirmation bias
- core belief

### Relational Constructs

- interaction cycle
- feedback loop
- pursuit-withdrawal
- role
- boundary
- homeostasis
- polarization
- co-regulation

### Needs and Values Constructs

- autonomy
- closeness
- respect
- fairness
- reliability
- predictability
- trust
- appreciation
- emotional safety

### Narrative Constructs

- self-narrative
- partner narrative
- relationship narrative
- identity threat
- preferred identity
- alternative narrative

### Methodological Constructs

- confidence
- evidence quality
- missing context
- competing hypothesis
- unsupported assumption
- fragile finding
- robust finding

## Relationship Types

Use consistent relationship types across the graph.

### supports

Evidence supports a construct or finding.

### contradicts

Evidence weakens a construct or finding.

### contributes_to

One construct helps produce another.

### escalates

One behavior or construct increases conflict intensity.

### deescalates

One behavior or construct reduces conflict intensity.

### protects

A behavior may protect a need or value.

### threatens

A behavior may threaten a need, value, or identity.

### co_occurs_with

Two constructs appear near each other without proven causality.

### alternative_to

One interpretation is an alternative explanation for another.

### intervention_for

A suggested behavior may improve a pattern.

## Example Knowledge Graph Fragment

```text
Q17: "You never listen"
  supports
Globalizing Language
  supports
Criticism
  may threaten
Need for Competence
  may contribute_to
Defensiveness
  escalates
Conflict Cycle

Alternative Interpretation:
  Expression of unmet need for understanding

Intervention:
  Convert criticism into specific observation + feeling + need
```

## Why Ontology Matters

Without an ontology, the app produces disconnected text reports.

With an ontology, the app can:

- merge findings across modules
- detect convergence
- detect contradictions
- rank confidence
- generate interactive maps
- explain why a synthesis conclusion was reached
- support future modules without redesign

## MVP Ontology Scope

For MVP, keep ontology simple:

- Store constructs as typed objects
- Store relationships as edges
- Link findings to evidence
- Link findings to modules
- Link interventions to constructs

A full graph database is optional. PostgreSQL tables can represent nodes and edges initially.
