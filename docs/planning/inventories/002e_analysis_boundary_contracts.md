# 002-E Analysis Boundary Contracts

## Status

Accepted as the Phase 002-E analysis boundary contract inventory.

---

# Purpose

Provide compact architecture contracts for later implementation of analysis scope, reflection lenses, bounded hypotheses, safety posture, reflection points, validation, and corpus-aware reasoning.

These contracts are not database schemas yet.

They are concept-to-architecture targets.

---

# AnalysisScope Contract

## Purpose

Declare what evidence an analysis run is allowed to use.

## Candidate fields

```text
id
owner_id
scope_type
scope_id
case_id optional
selected_transcript_version_ids
excluded_transcript_version_ids
requested_lens_ids
user_provided_context
user_provided_hypotheses
analysis_purpose
created_at
```

## Allowed scope types

```text
single_transcript_version
selected_transcript_set
case_evidence_corpus
future_explicit_workspace_corpus
```

## Rules

- Scope must be explicit.
- Do not silently use all retained transcripts.
- Do not include deleted, expired, or stale transcript versions as active evidence.
- Corpus-level claims must cite transcript versions and quote IDs.

---

# ReflectionLensContract

## Purpose

Map an implementation module to product-safe lens behavior.

## Candidate fields

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

## Rules

- Product-facing term is `Reflection Lens`.
- Implementation may continue using module terminology internally.
- Therapeutic and diagnostic frameworks may be source-framework references, not authority claims.
- Each lens must declare what it cannot conclude.

---

# PsychologicalHypothesis Contract

## Purpose

Represent an evidence-limited reflective hypothesis without diagnosis or labeling.

## Candidate fields

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

## Allowed sources

```text
user_provided_context
user_question
lens_suggested
corpus_pattern_review
```

## Allowed support levels

```text
observed_behavior
consistent_with_hypothesis
partially_consistent_with_hypothesis
contradicts_hypothesis
insufficient_evidence
alternative_explanation_likely
```

## Forbidden support levels

```text
confirmed
diagnosed
proved
clinically_established
ruled_in
ruled_out
pathological
```

---

# HypothesisSupportAssessment Contract

## Purpose

Separate the evidence assessment from the hypothesis label.

## Candidate fields

```text
id
hypothesis_id
scope_type
scope_id
support_level
confidence
supporting_evidence_quote_ids
contradicting_evidence_quote_ids
missing_evidence
alternative_explanations
corpus_enrichment_type optional
transcript_version_count
limitations
created_at
```

## Rules

- Support is not diagnosis.
- Contradiction and alternatives must be first-class, not footnotes.
- Corpus support requires multiple transcript/version references when recurrence is claimed.

---

# SafetyPosture Contract

## Purpose

Represent safety-aware override state and required output behavior.

## Candidate fields

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

## Suggested posture values

```text
none_detected
elevated_caution
high_risk
immediate_or_crisis_indicators
```

## Rules

- Safety posture is not a legal or clinical conclusion.
- Safety posture must be evidence-linked.
- Elevated/high-risk posture can suppress ordinary reflection or repair guidance.
- Safety-aware framing overrides ordinary hypothesis exploration.

---

# ReflectionPoint Contract

## Purpose

Represent non-prescriptive, evidence-linked self-review prompts.

## Candidate fields

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

## Rules

- Reflection points are not commands.
- Reflection points are not treatment instructions.
- Reflection points should not pressure confrontation or repair in high-risk contexts.
- Reflection points must trace back to evidence or findings.

---

# CorpusPatternAssessment Contract

## Purpose

Represent evidence enrichment across multiple transcript versions.

## Candidate fields

```text
id
scope_type
scope_id
case_id optional
pattern_name
enrichment_type
source_transcript_version_ids
supporting_evidence_quote_ids
contradicting_evidence_quote_ids
confidence
confidence_rationale
context_split
trend_summary
limitations
staleness_status
created_at
```

## Enrichment types

```text
recurrence
contradiction
strengthening
weakening
context_split
temporal_change
insufficient_corpus_evidence
```

## Rules

- A prior model conclusion is not evidence.
- Duplicate quote reuse must not inflate support.
- Corpus claims must remain inspectable back to quote IDs.
- Deleted evidence must invalidate, stale-mark, recompute, or lower confidence of dependent corpus objects.

---

# AnalysisValidationResult Contract

## Purpose

Represent whether an output passed analysis-boundary gates before display, retention, export, or corpus reuse.

## Candidate fields

```text
id
run_id
scope_id
validator_version
passed
critical_failures
warnings
blocked_output_sections
required_revisions
created_at
```

## Validator categories

```text
evidence_linkage
scope_and_version_binding
hypothesis_boundary
diagnosis_labeling_prohibition
intent_as_fact_prohibition
therapeutic_authority_prohibition
safety_override_behavior
corpus_overreach
confidence_calibration
reflection_point_safety
report_language
export_readiness
```

---

# ReportScope Contract

## Purpose

Declare how a report should present its evidence basis.

## Candidate fields

```text
report_id
scope_type
scope_id
source_transcript_version_ids
case_id optional
lens_ids
safety_posture_id optional
contains_hypotheses
contains_corpus_claims
limitations
created_at
```

## Rules

Reports should visibly distinguish:

- single-transcript analysis
- selected-transcript comparison
- case-corpus analysis

---

# Decision

These contracts should guide later schema, prompt, validator, reasoning graph, and report work.

They do not require immediate implementation before the Phase 002-I exit review.
