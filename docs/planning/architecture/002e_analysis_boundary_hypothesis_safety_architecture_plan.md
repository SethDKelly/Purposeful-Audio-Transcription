# 002-E Analysis Boundary, Hypothesis, and Safety Architecture Plan

## Status

Accepted as the Phase 002-E architecture plan.

This document translates the accepted hypothesis-aware reflection, therapeutic reflection lens, safety boundary, and corpus reasoning decisions into architecture requirements for later implementation phases.

It does not authorize code, schema, prompt, validator, UI, deployment, or evaluation changes by itself.

---

# Purpose

Define how the system should enforce evidence-limited analysis, bounded psychological hypotheses, diagnostic-framework-informed reasoning without clinical authority, safety-aware override behavior, corpus-aware confidence, and non-diagnostic report language.

This plan builds on:

- `docs/concepts/015_hypothesis_reflection_boundary.md`
- `docs/concepts/016_therapeutic_lens_language_decision.md`
- `docs/concepts/017_safety_boundary_decision.md`
- `docs/planning/inventories/002d_corpus_reasoning_scope_rules.md`

---

# Accepted Analysis Principle

```text
The system may reason from transcript evidence through bounded reflection lenses and hypotheses.
It must not diagnose, label, adjudicate, prove hidden intent, provide treatment authority, or mutualize serious safety concerns.
```

---

# Architecture Decision Summary

## 1. Analysis Boundary becomes an enforceable architecture layer

`Analysis Boundary` should be represented across:

- lens registry metadata
- prompt/input construction
- output schemas
- validators
- report rendering
- reasoning graph edge rules
- evaluation fixtures
- UI copy and disclaimers

It should not exist only as documentation.

## 2. Reflection Lens is the product concept; module is implementation

The product-facing concept is `Reflection Lens`.

Implementation may continue to use modules/workflows internally, but each module should map to a lens contract that declares:

- purpose
- lens family
- source-framework references
- permitted inference depth
- confidence ceiling
- evidence requirements
- safety behavior
- forbidden claims
- expected output objects

## 3. Therapeutic and diagnostic frameworks may inform reasoning but not authority

CBT-style, DBT-style, psychodynamic, attachment-informed, trauma-informed, behavioral, and diagnostic-framework-informed concepts may provide reasoning references.

They must be framed as evidence-limited reflection aids.

They must not be framed as:

- diagnosis
- treatment
- pathology detection
- clinical assessment
- professional conclusion
- mental health determination

## 4. Psychological Hypothesis needs a bounded domain contract

A `PsychologicalHypothesis` should be represented separately from an ordinary finding when later implementation supports it.

It should preserve:

- hypothesis name
- hypothesis source
- analysis scope
- evidence for
- evidence against
- missing evidence
- alternatives
- support level
- confidence
- inference depth
- safety considerations
- non-diagnostic boundary statement
- corpus support summary when applicable

## 5. Safety-aware framing is an override, not a report option

Safety posture should be determined early enough to affect:

- prompt selection
- enabled/disabled lenses
- hypothesis framing
- report section ordering
- suppressed recommendations/reflection prompts
- UI banner or warning behavior
- evaluation gates

A simple boolean is not enough as the mature architecture target.

## 6. Corpus-aware reasoning may strengthen or weaken hypotheses only with evidence lineage

Corpus-level support must distinguish:

- recurrence across transcript versions
- contradiction across transcript versions
- temporal change
- context split
- strengthening evidence
- weakening evidence
- insufficient corpus evidence

Prior model conclusions are not evidence by themselves.

Corpus claims require source transcript version and evidence quote lineage.

## 7. Analysis output should prefer reflection points over recommendations/interventions

The implementation may still contain `recommendations` or `intervention` legacy terms, but product architecture should move toward `ReflectionPoint`.

A reflection point is:

```text
non-prescriptive, evidence-linked, self-review oriented, and bounded by safety posture
```

---

# Architecture Layers

## 1. Input Scope Layer

Every analysis run should declare its evidence scope before analysis begins.

Allowed scopes:

```text
single_transcript_version
selected_transcript_set
case_evidence_corpus
future_explicit_workspace_corpus
```

Required scope metadata:

```text
scope_type
scope_id or selected transcript version ids
owner_id
included_transcript_version_ids
excluded_transcript_version_ids
case_id when applicable
analysis_purpose
requested_lenses
user_provided_context
user_provided_hypotheses
```

Rules:

- Do not silently use all retained transcripts.
- Do not use expired drafts in durable corpus reasoning.
- Do not use deleted or stale transcript versions as active evidence.
- Do not treat raw audio as corpus evidence after transcription.
- Do not treat prior model conclusions as evidence.

## 2. Lens Contract Layer

Each reflection lens should declare an architecture contract.

Candidate contract fields:

```text
lens_id
product_name
implementation_module_id
lens_family
source_frameworks
primary_question
secondary_questions
permitted_inference_depth
confidence_ceiling
requires_evidence_quotes
supports_corpus_reasoning
supports_hypothesis_output
safety_behavior
forbidden_claims
required_limitations
output_object_types
```

Example lens families:

```text
communication_reflection
behavioral_reflection
cognitive_reflection
therapeutic_reflection
attachment_informed_reflection
trauma_informed_reflection
safety_aware_reflection
methodological_review
corpus_longitudinal_review
```

## 3. Hypothesis Contract Layer

A bounded hypothesis object should not behave like a diagnosis or label.

Candidate fields:

```text
id
hypothesis_name
hypothesis_source
scope_type
scope_id
subject_ref_or_speaker_ref optional
support_level
confidence
confidence_rationale
inference_depth
evidence_for_quote_ids
evidence_against_quote_ids
missing_evidence
alternative_explanations
safety_considerations
non_diagnostic_boundary
corpus_support_summary_id optional
created_from_lens_id
created_from_run_id
```

Allowed hypothesis sources:

```text
user_provided_context
user_question
lens_suggested
corpus_pattern_review
```

Allowed support levels:

```text
observed_behavior
consistent_with_hypothesis
partially_consistent_with_hypothesis
contradicts_hypothesis
insufficient_evidence
alternative_explanation_likely
```

Forbidden support levels:

```text
confirmed
diagnosed
proved
clinically_established
ruled_in
ruled_out
pathological
```

## 4. Safety Posture Layer

Safety posture should be a structured object, not only prose or a boolean.

Candidate fields:

```text
id
scope_type
scope_id
posture
trigger_evidence_quote_ids
risk_indicators
confidence
uncertainty
recommended_output_posture
suppressed_lenses
suppressed_sections
required_report_sections
support_category
limitations
created_from_run_id
```

Suggested posture values:

```text
none_detected
elevated_caution
high_risk
immediate_or_crisis_indicators
```

These are architecture labels for output posture, not legal or clinical determinations.

Safety posture must be evidence-linked and uncertainty-aware.

## 5. Reflection Point Layer

A reflection point should replace prescriptive recommendation semantics.

Candidate fields:

```text
id
source_finding_ids
source_hypothesis_ids optional
source_evidence_quote_ids
scope_type
reflection_prompt
why_it_may_matter
confidence
limitations
safety_posture_constraint
not_to_be_used_when
```

Rules:

- Reflection points are not treatment instructions.
- Reflection points are not commands.
- Reflection points should not pressure confrontation or repair in high-risk contexts.
- Reflection points should remain anchored to evidence and limitations.

## 6. Reasoning Graph Boundary Layer

Graph nodes and edges should preserve inference boundaries.

Graph objects should distinguish:

```text
evidence node
observation node
finding node
hypothesis node
reflection point node
safety posture node
corpus pattern node
limitation node
alternative explanation node
```

Graph edges should distinguish:

```text
supports
partially_supports
contradicts
alternative_to
co_occurs_with
recurs_across
strengthens
weakens
contextualizes
requires_safety_override
limited_by
```

Causal or motive-implying edges should require stricter evidence and lower confidence ceilings.

## 7. Output Validation Layer

Every major output should pass validators before being shown, retained, exported, or used in corpus summaries.

Required validator categories:

- evidence linkage
- transcript version / corpus scope
- hypothesis boundary
- diagnosis / labeling prohibition
- hidden-intent-as-fact prohibition
- therapeutic authority prohibition
- safety override behavior
- corpus overreach
- confidence calibration
- reflection point safety
- report language
- export readiness

---

# Prompt Architecture Requirements

Prompt construction should receive explicit boundaries, not rely on general instruction alone.

Every analysis prompt should include structured context for:

```text
evidence scope
included transcript versions
requested lenses
forbidden claims
hypothesis support levels
confidence rules
safety override rules
corpus reasoning rules when applicable
output schema
validation checklist
```

Prompts should avoid sending unnecessary corpus content.

Corpus prompts should retrieve selected evidence and summaries with lineage, not dump all retained transcripts by default.

---

# Report Architecture Requirements

Reports should be marked by scope:

```text
single-transcript report
selected-transcript comparison
case-corpus report
```

Every report should identify:

- evidence scope
- transcript version basis
- lenses used
- safety posture if relevant
- hypothesis support level if hypotheses are included
- confidence and limitations
- alternatives / contradictions
- corpus evidence count when applicable

Reports should avoid:

- diagnosis language
- treatment plan language
- intent as fact
- moral verdicts
- legal conclusions
- unsupported reconciliation pressure
- ordinary mutual-improvement framing in high-risk safety contexts

---

# Corpus-Aware Confidence Rules

Corpus-level confidence may increase only when:

- evidence comes from multiple transcript versions
- evidence is independently grounded in quote IDs
- duplicate quotes are not counted as independent support
- contradictions are considered
- context differences are described
- user-selected scope is explicit

Corpus-level confidence should remain cautious when:

- evidence comes from one transcript only
- speaker identity is uncertain
- context differs substantially
- safety implications exist
- diagnostic implications exist
- evidence is sparse, ambiguous, or contradicted

Corpus-level output should say:

```text
This pattern recurs across the selected case corpus...
```

not:

```text
This person always behaves this way...
```

---

# Safety Override Requirements

When safety posture is elevated or high-risk, the system should:

- prioritize safety-relevant evidence
- suppress ordinary mutual-improvement framing when inappropriate
- avoid reconciliation pressure
- avoid personality explanations as the primary frame
- avoid asking the user to challenge fear when the transcript supports fear
- limit or suppress reflection points that could increase risk
- provide product limitations and support categories when warranted

Safety-aware output should not:

- diagnose the risky participant
- adjudicate legal fault
- treat threats as ordinary conflict
- mutualize coercion or intimidation
- explain away danger through a hypothesis label
- provide crisis management beyond product scope

---

# Confidence Vocabulary Reconciliation

Current implementation confidence values may remain initially:

```text
observed
high
moderate
low
exploratory
insufficient_evidence
```

However, hypothesis support should use separate support-level categories:

```text
observed_behavior
consistent_with_hypothesis
partially_consistent_with_hypothesis
contradicts_hypothesis
insufficient_evidence
alternative_explanation_likely
```

This avoids forcing confidence values to carry both evidentiary strength and hypothesis-support semantics.

Future implementation can map:

| Concept Need | Existing/Proposed Representation |
|---|---|
| Direct observation | `Confidence.OBSERVED` plus evidence quote |
| Strong support | `Confidence.HIGH` or `MODERATE`, depending evidence and inference depth |
| Hypothesis possibility | `support_level=consistent_with_hypothesis` with bounded confidence |
| Contradiction | `support_level=contradicts_hypothesis` plus evidence against |
| Insufficient evidence | `Confidence.INSUFFICIENT_EVIDENCE` and `support_level=insufficient_evidence` |
| Alternative explanation | separate alternative explanation object or support level |

---

# Required Evaluation Gates

Later implementation should include gates for:

1. No diagnostic conclusion.
2. No identity labeling.
3. No user-provided diagnosis validation.
4. No hidden intent as fact.
5. No safety mutualization.
6. No high-risk reconciliation pressure.
7. No unsupported corpus generalization.
8. Every finding/hypothesis has evidence or is explicitly a limitation.
9. Corpus claims cite multiple transcript versions when claiming recurrence.
10. Reflection points are non-prescriptive and safety-aware.
11. Therapeutic frameworks are framed as reflection aids, not treatment authority.
12. Report language matches the declared scope.

---

# Proposed Later Implementation Concepts

These are architecture targets, not 002-E implementation tasks.

## ReflectionLensContract

Maps implementation modules to product-safe lens behavior.

## AnalysisScope

Declares transcript/corpus scope before prompt construction.

## PsychologicalHypothesis

Represents evidence-limited hypothesis reasoning separately from ordinary findings.

## HypothesisSupportAssessment

Stores support, contradiction, missing evidence, alternatives, and corpus context.

## SafetyPosture

Represents safety-aware override state and required output behavior.

## ReflectionPoint

Replaces recommendation/intervention semantics with bounded self-review prompts.

## AnalysisValidationResult

Captures validator results before display/export/retention.

## CorpusPatternAssessment

Captures recurrence, contradiction, strengthening, weakening, context split, and temporal change across selected transcript versions.

---

# Handoff to 002-F

002-F should use this plan to avoid mixing operational cost state with analysis state.

Cost state may determine availability and wake/sleep behavior, but it must not corrupt:

- analysis scope
- corpus scope
- in-flight safety posture
- retained evidence lineage
- validation state
- deletion/cascade jobs

---

# Non-goals

002-E does not implement:

- schema migrations
- prompt rewrites
- validators
- evaluation fixtures
- UI copy
- graph storage changes
- safety detection logic
- corpus retrieval logic
- report rendering changes

Implementation remains blocked until Phase 002-I exit review authorizes the next phase.

---

# Acceptance Result

The analysis boundary, hypothesis, safety, corpus-aware confidence, and validation architecture is ready to feed 002-F and later implementation sequencing.

Proceed next to:

```text
002-F — Cost State and Personal Deployment Architecture Plan
```
