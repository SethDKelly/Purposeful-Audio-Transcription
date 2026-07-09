# 09 — Evidence, Confidence, and Citations

## Purpose

The application must make evidence and uncertainty visible. This is central to product trust.

## Evidence Indexing

Each transcript quote should receive a stable ID:

```text
Q001, Q002, Q003...
```

Each quote should map to:

- transcript
- speaker
- turn
- exact text
- surrounding context

## Evidence Use Rules

Every significant finding should include evidence IDs.

Exceptions:

- general limitations
- module-level methodological cautions
- synthesis-level uncertainty statements

## Evidence Quality Levels

### Direct Evidence

Quote directly supports claim.

### Indirect Evidence

Claim is inferred from multiple quotes.

### Contextual Evidence

Claim depends on conversation structure.

### Insufficient Evidence

No reliable support.

## Confidence Model

Use one shared confidence model across all modules.

```ts
type Confidence =
  | 'observed'
  | 'high'
  | 'moderate'
  | 'low'
  | 'exploratory'
  | 'insufficient_evidence';
```

## Confidence Definitions

### Observed

Directly stated or structurally visible.

### High

Supported by multiple direct observations.

### Moderate

Reasonable inference based on evidence.

### Low

Possible but several alternatives remain.

### Exploratory

Useful hypothesis for reflection, not a conclusion.

### Insufficient Evidence

The transcript cannot support the claim.

## Confidence Ceiling

Modules should have confidence ceilings.

Examples:

- Communication Analysis: High
- Mediation Analysis: Moderate/High
- Systems Analysis: Moderate
- Cognitive Analysis: Moderate
- Attachment Matrix: Low/Moderate
- Psychological Formulation: Low/Moderate
- Narrative Analysis: Moderate
- Bias Audit: High for evidence quality, low for relationship conclusions

## UI Confidence Display

Use plain language:

- Directly observed
- Strongly supported
- Reasonable interpretation
- Tentative possibility
- Exploratory hypothesis
- Not enough evidence

## Evidence-Linked UI Pattern

Every finding card should show:

- Claim
- Confidence
- Supporting quotes
- Alternative explanations
- Source modules
- Limitations

## Example Finding Card

```text
Claim: A criticism-defensiveness loop appears in the conversation.
Confidence: Moderate
Evidence: Q012, Q019, Q027
Alternative explanations: stress, missing context, unclear tone
Source modules: Communication Analysis, Systems Analysis, Gottman Analysis
```

## Anti-Overclaiming Rules

The system should flag claims that:

- infer diagnosis
- infer intent without evidence
- make relationship predictions
- lack evidence IDs
- exceed module confidence ceiling
- ignore alternative explanations
