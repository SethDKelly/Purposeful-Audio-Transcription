<!-- version: 1.0.0 -->

# Output Schema Instructions

Respond with a single JSON object matching `module_output_v1` only.
Put any human-readable report inside `raw_markdown_report` — do not emit markdown outside the JSON.

## Required JSON Shape

```json
{
  "module_id": "<module_id>",
  "module_version": "<module_version>",
  "executive_summary": "2-4 sentence overview",
  "findings": [
    {
      "id": "F001",
      "module_run_id": "pending",
      "type": "observation",
      "title": "Short finding title",
      "summary": "Clear explanation grounded in evidence",
      "confidence": "moderate",
      "evidence_quote_ids": ["Q001"],
      "alternative_explanations": ["Required when confidence is inferred"],
      "limitations": ["Optional limitation"],
      "construct_ids": []
    }
  ],
  "constructs": [
    {
      "id": "C001",
      "type": "interaction_pattern",
      "label": "Short construct label",
      "description": "Optional description",
      "confidence": "moderate",
      "evidence_quote_ids": ["Q001"]
    }
  ],
  "relationships": [
    {
      "id": "R001",
      "source_construct_id": "C001",
      "target_construct_id": "C002",
      "relationship_type": "contributes_to",
      "confidence": "moderate"
    }
  ],
  "recommendations": ["Practical suggestions when appropriate"],
  "limitations": ["Module-level limitations"],
  "raw_markdown_report": ""
}
```

## Finding Types

Use one of: observation, interaction_cycle, emotion, need, value, belief, narrative, repair_attempt, escalation_point, communication_behavior, hypothesis, intervention, uncertainty.

## Validation Rules

1. `module_id` and `module_version` must match the module you are running.
2. Every finding must include at least one `evidence_quote_ids` entry unless it is a pure methodological limitation.
3. Inferred findings (confidence high, moderate, low, or exploratory) **must** include at least one non-empty `alternative_explanations` entry.
4. Confidence values must not exceed the module confidence ceiling.
5. Only use quote IDs that appear in the provided evidence index.
6. Put the real analysis in structured fields (`findings`, `constructs`, `relationships`, `recommendations`). Prefer `raw_markdown_report` as `""`; if used, keep it under ~150 words. Do not duplicate the full finding list as markdown.

## Response Format

Return **only** a single JSON object (no markdown fences, no prose outside JSON).
