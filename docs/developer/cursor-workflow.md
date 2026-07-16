# 13 — Cursor Development Workflow

## Purpose

This document describes how to use Cursor IDE effectively to build the application from the design package.

## Recommended Cursor Strategy

Do not ask Cursor to build the whole app at once.

Use small implementation tasks with clear acceptance criteria.

## Suggested Repository Setup Prompt

```text
Create a TypeScript Next.js application for a Relationship Reasoning Engine. Set up folders for domain models, schemas, services, module registry, workflows, prompt compiler, and UI components. Do not implement LLM calls yet. Create placeholder interfaces and tests.
```

## Cursor Task Sequence

### Task 1 — Domain Types

Ask Cursor:

```text
Using docs/03_domain_model.md and docs/05_data_model_and_schemas.md, implement TypeScript domain types and Zod schemas for Transcript, Speaker, Turn, EvidenceQuote, ModuleDefinition, Finding, Construct, ModuleRun, WorkflowRun, and SynthesisReport.
```

Acceptance criteria:

- Types compile
- Zod schemas validate sample objects
- Tests exist

### Task 2 — Transcript Parser

```text
Implement a transcript parser that accepts plain text with speaker labels like "Person A:" and returns speakers, turns, and quote IDs. Include tests for two-speaker and multi-speaker transcripts.
```

### Task 3 — Evidence Index

```text
Implement an evidence index service that creates stable quote IDs for each turn and supports lookup by quote ID, speaker, and turn index.
```

### Task 4 — Module Registry

```text
Implement a module registry that loads module definitions from YAML or JSON files and validates them against the ModuleDefinition schema.
```

### Task 5 — Prompt Compiler

```text
Implement a prompt compiler that combines shared RAF instructions, a module definition, a transcript evidence index, and an output schema into a final prompt string.
```

### Task 6 — LLM Adapter

```text
Create an LLM provider interface with a mock provider implementation. The interface should accept prompt input and return raw text. Do not hardcode any provider-specific logic into services.
```

### Task 7 — Module Runner

```text
Implement a module runner that takes a module definition and transcript, compiles a prompt, calls the LLM adapter, validates JSON output, and stores a ModuleRun result.
```

### Task 8 — Workflow Runner

```text
Implement a workflow runner that executes a list of module runs sequentially for MVP and stores workflow state.
```

### Task 9 — Report UI

```text
Build React components for FindingCard, EvidenceQuoteViewer, ConfidenceBadge, ModuleTabs, and ExecutiveSummaryPanel using mock data.
```

### Task 10 — End-to-End MVP

```text
Connect transcript input, parser, workflow runner, mock module outputs, and report UI into one end-to-end local flow.
```

## Cursor Best Practices

- Keep docs in `/docs`
- Keep prompts/templates in `/prompt_templates`
- Keep module definitions in `/module_registry`
- Ask Cursor for tests with every service
- Use mock LLM responses before connecting real APIs
- Use schema validation aggressively
- Commit after each working milestone

## Avoid These Cursor Prompts

Avoid:

```text
Build the whole app.
```

Prefer:

```text
Implement the evidence index service described in docs/09 with tests. Do not modify unrelated files.
```

## Useful Cursor Rule File Ideas

Add project rules:

```text
- All LLM outputs must be validated with schemas.
- No module should call an LLM directly; use the LLM adapter.
- Every finding must include confidence and evidence quote IDs unless explicitly marked as a limitation.
- Keep domain logic separate from UI components.
- Do not embed giant prompts in application code; load templates or compile prompts.
```
