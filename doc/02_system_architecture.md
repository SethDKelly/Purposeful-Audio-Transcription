# 02 — System Architecture

## High-Level Architecture

```text
Frontend UI
  ↕
Application API
  ↕
Transcript Processing Service
  ↕
Evidence Index
  ↕
Workflow Engine
  ↕
Analysis Module Runner
  ↕
Prompt Compiler / LLM Adapter
  ↕
Structured Output Parser
  ↕
Synthesis Engine
  ↕
Report Store
```

## Recommended Initial Tech Stack

A practical MVP stack:

- Frontend: Next.js + React + TypeScript
- Backend: Next.js API routes or FastAPI
- Database: PostgreSQL
- ORM: Prisma or SQLAlchemy
- Queue: BullMQ, Celery, or simple job table for MVP
- LLM provider abstraction: service layer, not hardcoded calls in UI
- Validation: Zod or Pydantic
- Storage: local filesystem for MVP, S3-compatible storage later

## Core Services

### 1. Transcript Service

Responsibilities:

- Accept transcript uploads or pasted text
- Normalize transcript format
- Segment into speaker turns
- Assign quote IDs
- Store transcript metadata

### 2. Evidence Index Service

Responsibilities:

- Create canonical quote references
- Track speaker, turn number, timestamp if available
- Store excerpts and surrounding context
- Provide evidence retrieval to modules

### 3. Module Registry

Responsibilities:

- Store module metadata
- Define input requirements
- Define output schema
- Track module versions
- Enable/disable modules per workflow

### 4. Prompt Compiler

Responsibilities:

- Convert module specs into executable prompts
- Inject transcript/evidence context
- Enforce shared rules, confidence labels, and output schema
- Support provider-specific prompt formatting

### 5. Workflow Engine

Responsibilities:

- Select modules based on suite
- Run independent modules in parallel
- Respect dependencies
- Retry failed steps
- Track job state
- Persist outputs

### 6. Structured Output Parser

Responsibilities:

- Parse LLM JSON outputs
- Validate against schemas
- Repair or retry malformed outputs
- Normalize findings across modules

### 7. Synthesis Engine

Responsibilities:

- Merge findings across modules
- Identify convergence/divergence
- Produce confidence-weighted summary
- Generate final report structure

### 8. Report UI

Responsibilities:

- Present dashboard
- Show evidence-linked claims
- Support module tabs
- Display confidence and uncertainty
- Allow export to Markdown/PDF later

## Data Flow

```text
User Upload
  → Transcript Object
  → Turn Objects
  → Evidence Index
  → Workflow Job
  → Module Runs
  → Structured Findings
  → Cross-Module Findings
  → Synthesis Report
  → UI Rendering
```

## Execution Model

For the full suite:

```text
Preprocessing
  → Observable modules in parallel
  → Interpretive modules in parallel
  → Relational modules in parallel
  → Bias audit
  → Meta-synthesis
```

## Important Architecture Decision

Do not embed prompt text directly throughout the codebase.

Instead:

- Keep module definitions in structured files
- Keep shared instructions in framework-level templates
- Compile prompts dynamically
- Store prompt versions used for every module run

This supports reproducibility and future model upgrades.

## Suggested Directory Structure

```text
app/
  frontend/
  api/
  services/
    transcript/
    evidence/
    modules/
    workflows/
    llm/
    synthesis/
  domain/
  schemas/
  module_registry/
  prompt_templates/
  tests/
  docs/
```

## MVP Simplification

For the first version, you can run everything synchronously or with a simple job table. Avoid over-engineering distributed queues until the analysis suite becomes slow or multi-user.
