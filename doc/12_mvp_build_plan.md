# 12 — MVP Build Plan

## MVP Goal

Build a working application that can analyze a transcript using a small but representative subset of the framework.

## MVP Modules

Start with 4 modules:

1. Relationship Conversation Analysis
2. NVC Analysis
3. Systems Analysis
4. Bias & Reliability Audit

Then add Meta-Synthesis.

This provides:

- observable analysis
- practical communication coaching
- relational pattern detection
- confidence calibration
- integrated report

## Phase 0 — Project Setup

Tasks:

- Create repository
- Set up Next.js or chosen stack
- Add database
- Add schema validation
- Add environment configuration
- Add LLM provider abstraction

Deliverable:

Basic app shell and backend health check.

## Phase 1 — Transcript Ingestion

Tasks:

- Paste transcript UI
- Upload text file
- Speaker turn parser
- Manual speaker correction
- Evidence quote generator

Deliverable:

Stored transcript with speakers, turns, and quote IDs.

## Phase 2 — Module Registry

Tasks:

- Define module metadata schema
- Create first 4 module definitions
- Store module versions
- Add module output schema

Deliverable:

Registry can list modules and validate definitions.

## Phase 3 — Prompt Compiler MVP

Tasks:

- Create shared instruction template
- Create module-specific templates
- Inject transcript evidence
- Request JSON output
- Validate output

Deliverable:

One module can run and return structured findings.

## Phase 4 — Workflow Runner

Tasks:

- Define Quick Review workflow
- Define Full MVP workflow
- Run modules sequentially
- Persist module outputs
- Retry validation failures

Deliverable:

A transcript can produce multiple module outputs.

## Phase 5 — Report UI

Tasks:

- Executive summary page
- Finding cards
- Evidence quote viewer
- Module tabs
- Confidence labels

Deliverable:

User can explore results interactively.

## Phase 6 — Synthesis

Tasks:

- Feed module outputs into synthesis module
- Generate integrated summary
- Identify convergence/divergence
- Rank interventions

Deliverable:

Integrated report generated from module outputs.

## Phase 7 — Testing and Refinement

Tasks:

- Add sample transcripts
- Validate JSON reliability
- Check evidence links
- Test long transcript behavior
- Review safety language

Deliverable:

MVP ready for private use.

## Suggested MVP Milestones

### Milestone 1

Transcript ingestion and evidence indexing complete.

### Milestone 2

Single module analysis working.

### Milestone 3

Multi-module workflow working.

### Milestone 4

Interactive report UI working.

### Milestone 5

Synthesis and confidence calibration working.

## What Not To Build First

Avoid initially building:

- full graph database
- every module
- audio analysis
- user accounts
- billing
- complex permissions
- PDF export
- advanced visualizations

Focus on reasoning quality and evidence traceability first.
