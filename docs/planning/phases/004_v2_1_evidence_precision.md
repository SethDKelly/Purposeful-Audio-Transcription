# 004 — Evidence Precision

## Phase Goal

Improve evidence traceability by making evidence snippets concise, claim-specific, and easy to inspect.

Earlier versions sometimes produced evidence that was a paragraph or more. That is too broad for good traceability.

**Design:** [../../developer/evidence_precision_design.md](../../developer/evidence_precision_design.md) · [ADR 002](../../developer/architecture_decisions/adr_002_concise_evidence_spans.md)

---

# Principle

Evidence should cite the smallest useful transcript span.

Default evidence should be:

```text
atomic quote
or
short exchange
or
small expandable context window
```

---

# Suggested Config

Add configurable precision settings:

```yaml
evidence_precision:
  atomic_quote_max_chars: 280
  short_exchange_max_turns: 4
  context_window_before_turns: 1
  context_window_after_turns: 1
  max_evidence_items_per_finding: 3
  prefer_sentence_spans: true
  allow_paragraph_evidence: false
  warning_threshold_chars: 360
  hard_max_chars: 600
```

---

# Implementation Tasks

## Config

- [ ] Add evidence precision configuration.
- [ ] Make thresholds environment/configurable.
- [ ] Document defaults.

## Prompting

- [ ] Update shared prompt instructions to request concise evidence.
- [ ] Tell modules to cite the smallest useful span.
- [ ] Tell modules to avoid paragraph evidence.
- [ ] Tell modules to use short exchanges only when needed.

## Evidence Index

- [ ] Support concise evidence text separate from context.
- [ ] Consider sentence-level extraction.
- [ ] Preserve speaker and turn identity.
- [ ] Add evidence type: `atomic_quote`, `short_exchange`, `context_window`.

## Validation

- [ ] Warn when evidence exceeds threshold.
- [ ] Fail or repair when evidence exceeds hard max.
- [ ] Check findings do not cite too many evidence items.
- [ ] Check evidence exists in transcript/version.

## React UI

- [ ] Show concise evidence by default.
- [ ] Add “show context” expansion.
- [ ] Avoid showing full paragraph evidence inline.
- [ ] Display speaker and quote ID clearly.

## Evaluation

- [ ] Add evidence length metrics.
- [ ] Add golden fixture evidence precision checks.
- [ ] Add release gate warning/failure thresholds.

---

# Acceptance Criteria

- Most evidence snippets are under the configured warning threshold.
- Paragraph evidence is not used by default.
- Users can expand to context when needed.
- Reports are easier to skim.
- Evidence precision metrics are included in evaluation.
- The app still preserves enough context for fair interpretation.
