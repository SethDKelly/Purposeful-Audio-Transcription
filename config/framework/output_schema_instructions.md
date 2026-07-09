<!-- version: 1.0.0 -->

# Output Schema Instructions

Respond with a single JSON object matching `module_output_v1`, then a human-readable markdown report.

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
      "alternative_explanations": ["Optional alternative if inferred"],
      "limitations": ["Optional limitation"],
      "construct_ids": []
    }
  ],
  "constructs": [],
  "relationships": [],
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
3. Inferred findings (confidence other than observed) should include `alternative_explanations` when plausible alternatives exist.
4. Confidence values must not exceed the module confidence ceiling.
5. Only use quote IDs that appear in the provided evidence index.
6. Keep `raw_markdown_report` as a readable summary for humans; it may expand on the JSON findings.

## Response Format

Return the JSON object first, wrapped in a fenced code block labeled `json`, followed by the markdown report.
