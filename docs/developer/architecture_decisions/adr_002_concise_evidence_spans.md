# ADR 002 — Concise Evidence Spans Instead of Paragraph Evidence

## Status

Accepted (v2.1 near-term)

## Context

The application's evidence traceability depends on linking every claim to transcript evidence.

Earlier versions sometimes produced evidence snippets that were a paragraph or more. While technically traceable, this is not ideal. Long evidence makes it harder to see which phrase supports the claim.

## Decision

Evidence should cite the smallest useful transcript span.

Default evidence should be:

- atomic quote
- short exchange
- small context window only when necessary

Paragraph-length evidence should not be used by default.

## Consequences

### Positive

- Better claim-to-evidence clarity.
- Easier reports.
- Stronger evidence discipline.
- Less unnecessary sensitive text exposure.
- Easier evaluation.

### Negative

- Requires better sentence/span extraction.
- Some interaction patterns need short exchanges.
- UI must support expandable context.
- Existing prompts/validators may need updates.

## Implementation

Add configurable evidence precision settings.

Update:

- prompt instructions
- evidence index service
- output validator
- React report UI
- export rendering
- golden evaluation metrics

## Future Direction

Eventually support exact character offsets and sentence-level evidence spans.
