# 14 — Testing, Evaluation, and Safety

## Testing Philosophy

The application must be tested at three levels:

1. Software correctness
2. LLM output validity
3. Analytical quality and safety

## Unit Tests

Test:

- transcript parsing
- speaker detection
- evidence ID generation
- schema validation
- module registry loading
- prompt compiler output
- workflow state transitions

## Integration Tests

Test:

- transcript → evidence index
- evidence index → module prompt
- module output → parsed findings
- multiple module outputs → synthesis
- finding card → evidence quote viewer

## Golden Transcript Tests

Create a small set of sample transcripts.

For each, define expected properties:

- number of speakers
- number of turns
- expected evidence quote IDs
- at least one expected finding type
- no unsupported diagnosis
- confidence labels present

## LLM Output Validation

Every module response must pass schema validation.

Required checks:

- valid JSON
- required fields present
- confidence labels valid
- evidence quote IDs exist
- no forbidden diagnostic claims
- alternatives included for inferred findings

## Safety Checks

Flag or block outputs that:

- diagnose a participant
- claim someone is abusive based on insufficient evidence
- infer intent as fact
- predict relationship outcome
- provide legal/medical determinations
- make coercive recommendations

## Safety Language

Reports should include:

```text
This analysis is based only on the transcript provided. It is not a diagnosis, legal assessment, or substitute for professional support. Important context such as tone, body language, history, and safety factors may be missing.
```

## Evaluation Metrics

### Structural Metrics

- JSON validity rate
- evidence citation coverage
- module completion rate
- retry rate

### Analytical Metrics

- unsupported inference rate
- confidence calibration quality
- balance across participants
- alternative explanation coverage
- practical recommendation quality

### User Experience Metrics

- report clarity
- evidence traceability
- usefulness of recommendations
- perceived neutrality
- cognitive load

## Human Review

For early versions, manually review outputs for:

- overconfidence
- subtle blame
- excessive speculation
- missed evidence
- repetitive module content
- confusing synthesis

## Red-Team Scenarios

Test transcripts involving:

- highly emotional arguments
- missing speaker labels
- sarcasm
- accusations of abuse
- one-sided accounts
- very short excerpts
- long multi-topic conflicts
- workplace conflict
- family conflict

## Privacy and Data Handling

Consider early:

- whether transcripts are stored
- deletion controls
- encryption
- logging policy
- whether raw prompts are stored
- whether outputs are used for model improvement

Privacy choices affect architecture.
