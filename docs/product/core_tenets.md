# Core Product Tenets

## Purpose

This document defines the durable product tenets for the Relationship Reasoning Engine.

These tenets should guide product design, backend architecture, prompt/module design, evaluation, UI behavior, exports, and future market-specific workflows.

The application should remain market-agnostic in the near term. It should not over-specialize for therapy, mediation, enterprise, coaching, or consumer relationship use until the core reasoning platform is more mature.

The durable goal is:

> Turn interpersonal transcripts into evidence-linked, confidence-calibrated, multi-lens structured reasoning while avoiding diagnostic or overconfident claims.

---

# Tenet 1 — Evidence Traceability

Every meaningful analytical claim must link to specific transcript evidence.

A user should be able to move from:

```text
finding
→ evidence quote
→ transcript location
→ speaker
→ surrounding context
```

## Product Requirements

- Every finding should cite one or more evidence quote IDs unless it is explicitly a limitation, uncertainty, or meta-observation.
- Every construct should cite evidence or derive from evidence-backed findings.
- Every graph relationship should cite evidence or explain that it is an inferred relationship with appropriate confidence.
- Report exports should include an evidence appendix.
- Evidence references should remain stable after report generation.

## Anti-Patterns

Avoid:

- uncited claims
- broad claims based on vague transcript impressions
- evidence blocks so long that users cannot tell which phrase supports the claim
- evidence references that change after transcript edits
- claims based only on module assumptions

---

# Tenet 2 — Confidence Calibration

The application must distinguish between what is observed, what is plausible, and what is insufficiently supported.

Every analytical claim should include:

- confidence level
- basis for confidence
- limitations
- alternative explanations when relevant

Confidence should be lower when:

- transcript context is incomplete
- tone/audio cues are unavailable
- behavior occurs once
- intent is inferred
- psychological state is inferred
- safety or diagnostic implications are possible

---

# Tenet 3 — Multi-Lens Analysis

The system should analyze relationship conversations through multiple complementary lenses without letting any single lens dominate.

Core lenses include:

- communication patterns
- interaction cycles
- systems dynamics
- cognitive patterns
- mediation interests
- NVC observations/feelings/needs/requests
- attachment-informed interaction patterns
- trauma-informed communication
- emotional needs and values
- narrative identity and meaning-making
- safety-aware review
- bias and reliability audit

---

# Tenet 4 — Non-Diagnostic Discipline

The application must avoid diagnosing people, assigning disorders, or making unsupported clinical/legal determinations.

The system may discuss:

- observable behavior
- communication patterns
- possible interpretations
- evidence-limited hypotheses
- safety-relevant indicators
- areas needing professional review

The system must avoid definitive claims such as:

- this person has narcissistic personality disorder
- this is abuse as a settled fact
- this person is intentionally manipulating
- this proves trauma
- this person has an attachment style
- this relationship is doomed

---

# Tenet 5 — Longitudinal Case Tracking

The application should eventually identify change across conversations, not merely summarize isolated transcripts.

Product requirements:

- Cases should support multiple transcripts.
- Findings should reference the transcript/session they came from.
- Quote IDs must be scoped by transcript or evidence version.
- Longitudinal synthesis should distinguish recurring patterns from one-time events.
- Progress claims should cite comparable evidence across time.

---

# Tenet 6 — Professional Workflow Fit

The product should support professional review even while remaining market-agnostic.

Potential users may include:

- therapists
- mediators
- coaches
- supervisors
- educators
- enterprise leadership facilitators
- researchers

Product requirements:

- Reports should be exportable.
- Findings should be reviewable.
- Feedback should be capturable.
- Version manifests should be included.
- Evidence appendices should be available.
- Review/supervision workflows should be possible.
- Outputs should avoid making professional decisions on behalf of the user.

---

# Tenet 7 — Safety-Aware Framing

When transcripts include safety-relevant indicators, the application should change framing.

The system should not automatically treat every conflict as mutual communication difficulty.

Safety-aware mode should:

- avoid mutualizing serious concerns
- avoid reconciliation pressure
- use cautious and evidence-limited language
- recommend appropriate professional or emergency support when warranted
- suppress or modify modules that may produce unsafe framing
- distinguish elevated risk from ordinary conflict

---

# Tenet 8 — Structured Reasoning Graph

The system should produce a structured reasoning graph, not merely a chat-style response.

Core objects:

```text
Transcript
TranscriptVersion
EvidenceQuote
WorkflowRun
ModuleRun
Finding
FindingEvidence
Construct
ConstructEvidence
ConstructRelationship
RelationshipEvidence
Synthesis
Report
Feedback
EvaluationRun
SafetyEvent
Case
```

Product requirements:

- Findings should be structured objects.
- Constructs should be normalized and ontology-aware.
- Relationships should be typed and evidence-backed.
- Graph merge should preserve evidence and confidence.
- Synthesis should be generated from structured reasoning objects.
- Reports should be views over structured reasoning, not the only storage format.

---

# Tenet Compliance Questions

Every new feature should answer:

1. Does this improve evidence traceability?
2. Does this improve confidence calibration?
3. Does this preserve non-diagnostic discipline?
4. Does this support multi-lens reasoning?
5. Does this improve or preserve safety-aware framing?
6. Does this enrich the structured reasoning graph?
7. Does this support longitudinal understanding?
8. Does this remain broadly useful across markets?
9. Does this avoid turning the app into an unsupported diagnostic or adjudication tool?
10. Does this support professional review, export, or feedback?

If the answer is no to most of these, the feature belongs in the deferred backlog.
