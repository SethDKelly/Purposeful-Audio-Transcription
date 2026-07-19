# Evidence Precision Design

## Purpose

This document defines how the application should produce, store, display, and evaluate concise evidence snippets.

Evidence traceability is one of the application's core tenets. However, evidence that is too long becomes less useful. If every claim cites a paragraph, the user cannot tell exactly which phrase supports the finding.

The goal is:

> Cite the smallest useful transcript span that supports the claim, while allowing users to expand context when needed.

---

# Evidence Granularity Model

## 1. Atomic Quote

A single sentence, clause, or short turn that directly supports a claim.

Example:

```text
"I should have texted."
```

Best for:

- accountability
- explicit feelings
- concrete agreements
- direct requests
- specific observations

## 2. Short Exchange

A compact two-to-four-turn exchange that demonstrates an interaction pattern.

Example:

```text
Maya: "You always have a reason."
Leo: "That is not fair."
```

Best for:

- escalation cycles
- criticism/defensiveness
- repair attempts and responses
- misunderstanding sequences

## 3. Context Window

A limited surrounding window used only when a claim cannot be understood from a single quote.

Context windows should be expandable in the UI, not the default evidence display.

---

# Default Limits

Recommended initial configuration:

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

# Evidence Storage Requirements

Evidence should store:

```text
id
transcript_version_id
quote_id
speaker
text
turn_id
start_char
end_char
evidence_type
context_before
context_after
created_at
```

If exact character offsets are not feasible initially, use turn-level references first and add offsets later.

---

# Prompting Requirements

Module prompts should instruct models to cite concise evidence.

Recommended instruction:

```text
Cite the smallest useful evidence span. Prefer a single sentence or short exchange.
Do not cite full paragraphs unless absolutely necessary.
If context is needed, cite the key sentence and explain that surrounding context may be relevant.
```

---

# Parser / Validator Requirements

The output parser or validator should flag:

- evidence text above warning threshold
- evidence text above hard max
- findings with too many evidence items
- evidence that cites a whole paragraph when a sentence would suffice
- evidence that does not match a known quote/span

---

# UI Requirements

Show concise evidence by default.

When user clicks “Show context,” display:

```text
Previous turn
Cited evidence
Next turn
```

Reports should include concise inline evidence and optional evidence appendix context.

---

# Acceptance Criteria

- Evidence snippets are concise by default.
- Users can expand to context when needed.
- Evaluations flag overly long evidence.
- Reports are easier to skim.
- Evidence remains traceable to transcript version and location.
