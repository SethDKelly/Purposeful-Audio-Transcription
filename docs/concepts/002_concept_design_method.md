# 002 — Concept Design Method

## Purpose

Define how concept design will be applied to this application.

This is not a requirements document. It is a design method for discovering and refining the core concepts that should govern the application.

## Method Summary

The application should be described as a collection of concepts.

Each concept should have:

- name
- purpose
- operational principle
- state
- actions
- invariants
- failure modes
- composition with other concepts
- misfits or risks

## Concept Template

```text
Concept:
Purpose:
Operational principle:
Primary actors:
State:
Actions:
Invariants:
Failure modes:
Composes with:
Misfits:
Open questions:
```

## Key Criteria

### 1. Singular

A concept should have one primary purpose. If it has multiple unrelated purposes, split it.

For example, Recording should not also mean Transcript, Evidence, long-term memory, and analysis report.

### 2. Familiar

A concept should feel understandable to users.

Examples:

- Recording
- Transcript
- Case
- Reflection
- Evidence
- Report

### 3. Operational

A concept should have a clear story for how it works.

Example:

```text
The user uploads a recording. The system stages it, transcribes it, then deletes the audio after the retention window unless the user explicitly saves it.
```

### 4. Composable

Concepts should combine without surprising behavior.

Example:

```text
Transcript Version + Evidence Quote + Report
```

should compose so that reports always point to the exact evidence used at analysis time.

### 5. Protective

For this application, a concept must respect privacy, safety, and non-diagnostic boundaries.

## Concept Design Before Implementation

Do not begin refactoring by changing services, tables, routes, or screens.

First answer:

- What concept does this implementation serve?
- Is the concept valid?
- Is the concept named correctly?
- Does it compose with other concepts?
- Does it violate privacy or safety?
- Does it support personal use first?
- Does it preserve enterprise optionality later?

## Design Layers

Recommended order:

```text
Product premise
→ Concept catalog
→ Concept composition
→ Security/privacy concepts
→ Cost/availability concepts
→ Analysis philosophy
→ Future enterprise transition
→ Implementation mapping
```

## Important Distinction

Concepts are not the same as code modules.

Evidence Quote is a concept. It may involve a database table, parser, validator, UI component, export renderer, and evaluation metric. Those are implementation details.
