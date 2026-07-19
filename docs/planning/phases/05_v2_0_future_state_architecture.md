# 05 — v2.0 Future State Architecture

## Vision

v2.0 should establish the Relationship Reasoning Engine as a mature analytical platform.

The application should no longer feel like a prompt runner or prototype analysis app. It should feel like a structured, evidence-linked reasoning system for interpersonal transcripts and cases.

---

# v2 Product Principles

## 1. Evidence-Linked by Default

Every meaningful claim should connect to finding, evidence quote IDs, source transcript, source module, confidence, and alternatives/limitations.

## 2. Structured Before Narrative

The system should store structured findings, constructs, relationships, feedback, and evaluation metadata before rendering narrative reports. Reports are views over structured reasoning outputs.

## 3. Modules Are Replaceable

Modules should be versioned and evaluated. Prompts should be implementation artifacts, not the permanent center of the system.

## 4. Safety Is a Product Capability

Safety is not just disclaimer text. It should influence module selection, report framing, confidence language, UI warnings, recommendations, and escalation to support resources where appropriate.

## 5. Cases Matter

For real use, single-transcript analysis is only the beginning. Cases and longitudinal comparison are the durable product value.

---

# v2 Target Architecture

```text
React Product UI
        ↓
FastAPI /api/v1 or /api/v2
        ↓
Domain Services
        ↓
Workflow Engine / Job Queue
        ↓
Worker Service
        ↓
LLM / Transcribe / Storage Providers
        ↓
Postgres + Object Storage
        ↓
Ontology / Graph / Evaluation Layer
```

Optional internal tools:

```text
Streamlit Eval/Admin Console
        ↓
Same API
```

---

# Core v2 Capabilities

## 1. React Product UI

React should support transcript preparation, workflow selection, job progress, report exploration, evidence navigation, graph exploration, case dashboard, longitudinal analysis, feedback review, export packages, and settings/privacy.

## 2. API Platform

The backend should provide stable contracts for transcripts, cases, workflow runs, jobs, module runs, reports, findings, constructs, relationships, evidence, feedback, exports, evaluations, and safety events.

## 3. Durable Workflow Engine

The workflow engine should support DAG dependencies, parallel execution, retries, cancellation, job recovery, partial reruns, module-level status, workflow-level telemetry, and worker backpressure.

## 4. Ontology and Graph Reasoning

The graph layer should support canonical construct types, canonical relationship types, duplicate/near-duplicate construct merge, cross-module convergence, contradiction detection, evidence-weighted synthesis, and longitudinal construct tracking.

## 5. Evaluation System

The evaluation system should support golden fixtures, safety red-team fixtures, module version comparisons, signal scoring, forbidden-claim scoring, evidence relevance scoring, human review rubrics, release gates, and eval dashboards.

## 6. Case and Longitudinal Analysis

v2 should support multi-transcript cases, case-level themes, recurring cycles, progress over time, pinned findings, case notes, longitudinal synthesis, and case report packages.

## 7. Safety Governance

The system should support high-risk transcript detection, safety-aware report modes, module suppression or framing changes, red-team fixture coverage, cautious support/resource language, no overconfident abuse/manipulation/diagnostic conclusions, and auditability of safety events.

## 8. Professional-Grade Reporting

Reports should include executive summary, evidence-linked findings, confidence legend, module contribution summary, high/moderate/low-confidence sections, limitations, quote appendix, version manifest, and export controls/redaction.

---

# v2 Data Model Direction

Important entities:

```text
User / Account
Case
CaseParticipant
Transcript
TranscriptTurn
EvidenceQuote
WorkflowRun
Job
ModuleRun
Finding
FindingEvidence
Construct
ConstructRelationship
Synthesis
Report
ReportPackage
Feedback
EvaluationRun
SafetyEvent
Export
AuditEvent
```

---

# v2 Deployment Direction

Preferred mature deployment:

```text
React static app → S3 + CloudFront
FastAPI API service → ECS/Fargate or equivalent
Worker service → ECS/Fargate or equivalent
Postgres → RDS
Object storage → S3
LLM/ASR providers → Bedrock / Transcribe initially
```

Streamlit, if retained, should be an internal admin/eval console, not the primary user-facing UI.

---

# v2 Readiness Criteria

The application is ready to be called v2 when React owns the primary user journey, API contracts are stable and versioned, worker execution is durable and observable, evidence-linked findings are normalized and queryable, graph reasoning improves synthesis, golden and safety evals gate releases, case/longitudinal workflows are useful, safety-aware UX is mature, deployment and data governance are credible, module lifecycle is managed, and Streamlit has a resolved role.

---

# v2 Non-Goals

Do not require v2 to include every possible analysis module, clinical-grade diagnosis, legal determinations, fully automated safety adjudication, replacement for professional therapy/mediation, or a public marketplace/module plugin system.

---

# Future Beyond v2

Potential v2.x/v3 areas include multi-provider LLM routing, offline/local model support, advanced graph analytics, collaborative reviewer workflows, therapist/coach organization workspaces, annotation tools, user-authored custom workflows, plugin/module marketplace, benchmarking dashboard, and multi-modal audio tone analysis with strong ethical caution.
