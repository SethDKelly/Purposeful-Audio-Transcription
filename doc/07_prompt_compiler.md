# 07 — Prompt Compiler

## Purpose

The prompt compiler converts module definitions, framework-level rules, transcript evidence, and output schemas into executable prompts for an LLM.

## Why Compile Prompts?

Static prompts are hard to maintain. A compiler allows:

- consistent evidence standards
- consistent confidence language
- schema enforcement
- module versioning
- provider-specific formatting
- reusable shared instructions

## Compiler Inputs

```text
Framework rules
  + Module definition
  + Output schema
  + Transcript/evidence index
  + Workflow context
  + Model/provider constraints
  = Executable prompt
```

## Prompt Components

### 1. Shared System Rules

Reusable across all modules:

- evidence-first
- distinguish observation from interpretation
- use confidence labels
- avoid diagnosis unless module explicitly permits exploratory discussion
- avoid unsupported intent inference
- cite transcript quote IDs

### 2. Module Role

Defines the analytical lens.

Example:

```text
You are analyzing through a systems theory lens. Your primary question is: What feedback loops maintain the interaction?
```

### 3. Module-Specific Framework

The analytical sections required for the module.

### 4. Transcript Context

Include transcript turns or a compressed evidence index.

For long transcripts, use chunking and retrieval.

### 5. Output Schema Instructions

Require JSON plus optional Markdown.

### 6. Validation Rules

Examples:

- Every finding must include at least one evidence_quote_id unless marked as general limitation.
- Any inferred finding must include alternative explanations.
- Confidence cannot exceed module confidence ceiling.

## Example Compiled Prompt Skeleton

```text
[Shared RAF Rules]

[Module Role]

[Primary Question]

[Analytical Framework]

[Transcript Evidence Index]

[Output Schema]

[Validation Requirements]
```

## JSON-First Output

Prefer structured output first:

```json
{
  "executive_summary": "...",
  "findings": [
    {
      "type": "interaction_cycle",
      "title": "Criticism-defensiveness loop",
      "summary": "...",
      "confidence": "moderate",
      "evidence_quote_ids": ["Q12", "Q19"],
      "alternative_explanations": ["stress", "missing context"],
      "limitations": ["tone unavailable"]
    }
  ],
  "raw_markdown_report": "..."
}
```

## Prompt Versioning

Every module run should store:

- module version
- compiler version
- shared instruction version
- prompt template hash
- model name
- raw prompt optionally, if privacy policy allows

## Error Handling

If output fails validation:

1. Attempt structured repair
2. Ask model to reformat only
3. Retry module with stricter instructions
4. Mark module run as failed if still invalid

## MVP Approach

For MVP, you can start with hand-authored prompt templates. But place them behind a compiler interface so they can later become generated from module metadata.
