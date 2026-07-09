# 05 — Data Model and Schemas

## Purpose

This document describes practical schemas for implementation. These can be translated into TypeScript types, Zod schemas, Prisma models, or Pydantic models.

## Transcript Schema

```ts
interface Transcript {
  id: string;
  title: string;
  rawText: string;
  sourceType: 'paste' | 'file' | 'import';
  language?: string;
  createdAt: string;
}
```

## Speaker Schema

```ts
interface Speaker {
  id: string;
  transcriptId: string;
  label: string;
  displayName?: string;
}
```

## Turn Schema

```ts
interface Turn {
  id: string;
  transcriptId: string;
  speakerId: string;
  turnIndex: number;
  text: string;
  startTime?: string;
  endTime?: string;
}
```

## Evidence Quote Schema

```ts
interface EvidenceQuote {
  id: string;
  transcriptId: string;
  turnId: string;
  speakerId: string;
  quoteIndex: number;
  text: string;
  contextBefore?: string;
  contextAfter?: string;
}
```

## Confidence Schema

```ts
type Confidence =
  | 'observed'
  | 'high'
  | 'moderate'
  | 'low'
  | 'exploratory'
  | 'insufficient_evidence';
```

## Finding Schema

```ts
interface Finding {
  id: string;
  moduleRunId: string;
  type: FindingType;
  title: string;
  summary: string;
  confidence: Confidence;
  evidenceQuoteIds: string[];
  alternativeExplanations: string[];
  limitations: string[];
  constructIds?: string[];
}
```

## Finding Types

```ts
type FindingType =
  | 'observation'
  | 'interaction_cycle'
  | 'emotion'
  | 'need'
  | 'value'
  | 'belief'
  | 'narrative'
  | 'repair_attempt'
  | 'escalation_point'
  | 'communication_behavior'
  | 'hypothesis'
  | 'intervention'
  | 'uncertainty';
```

## Construct Schema

```ts
interface Construct {
  id: string;
  type: string;
  label: string;
  description?: string;
  confidence: Confidence;
  evidenceQuoteIds: string[];
}
```

## Construct Relationship Schema

```ts
interface ConstructRelationship {
  id: string;
  sourceConstructId: string;
  targetConstructId: string;
  relationshipType:
    | 'supports'
    | 'contradicts'
    | 'contributes_to'
    | 'escalates'
    | 'deescalates'
    | 'protects'
    | 'threatens'
    | 'co_occurs_with'
    | 'alternative_to'
    | 'intervention_for';
  confidence: Confidence;
}
```

## Module Definition Schema

```ts
interface ModuleDefinition {
  id: string;
  name: string;
  version: string;
  primaryLens: string;
  analyticalLevel: 'observable' | 'individual' | 'relational' | 'integrative' | 'methodological';
  unitOfAnalysis: 'speaker' | 'dyad' | 'interaction' | 'relationship' | 'narrative' | 'analysis_output';
  primaryQuestion: string;
  secondaryQuestions: string[];
  requiredConstructs: string[];
  outputSchemaId: string;
  recommendedCompanions: string[];
  dependencies: string[];
  inferenceDepth: 'low' | 'medium' | 'high';
  confidenceCeiling: Confidence;
}
```

## Module Run Output Schema

Each module should return:

```json
{
  "module_id": "string",
  "module_version": "string",
  "executive_summary": "string",
  "findings": [],
  "constructs": [],
  "relationships": [],
  "recommendations": [],
  "limitations": [],
  "raw_markdown_report": "string"
}
```

## Why Include Raw Markdown?

Structured data powers the application. Markdown supports readability, exports, and debugging. Store both.

## MVP Database Tables

Minimum tables:

- transcripts
- speakers
- turns
- evidence_quotes
- workflows
- workflow_runs
- modules
- module_runs
- findings
- constructs
- construct_relationships
- synthesis_reports
