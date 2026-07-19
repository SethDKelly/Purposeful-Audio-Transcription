# Tenet Compliance Evaluation Plan

## Purpose

This document defines how to evaluate whether the Relationship Reasoning Engine complies with its [core product tenets](../product/core_tenets.md). The goal is to make the tenets testable.

It supports planning phase **[002](../planning/phases/002_v2_1_core_tenets_and_governance.md)** and release-candidate gates in **[009](../planning/phases/009_v2_1_react_api_contract_and_release_candidate_readiness.md)**.

---

# Evaluation Dimensions

## 1. Evidence Traceability

Metrics:

```yaml
findings_without_evidence_count: 0
invalid_quote_id_count: 0
average_evidence_chars: 150
paragraph_evidence_count: 0
evidence_version_mismatch_count: 0
```

## 2. Confidence Calibration

Metrics:

```yaml
confidence_ceiling_violations: 0
unsupported_high_confidence_claims: 0
alternative_explanation_missing_count: 0
```

## 3. Multi-Lens Analysis

Metrics:

```yaml
module_count: 0
lens_coverage_count: 0
cross_lens_convergence_count: 0
cross_lens_disagreement_count: 0
```

## 4. Non-Diagnostic Discipline

Metrics:

```yaml
forbidden_claim_count: 0
diagnostic_language_count: 0
intent_as_fact_count: 0
personality_label_count: 0
```

## 5. Longitudinal Case Tracking

Metrics:

```yaml
case_evidence_missing_transcript_id_count: 0
case_evidence_missing_version_id_count: 0
longitudinal_claim_without_prior_evidence_count: 0
```

## 6. Professional Workflow Fit

Metrics:

```yaml
export_includes_version_manifest: true
export_includes_confidence_legend: true
export_includes_evidence_appendix: true
feedback_capture_available: true
```

## 7. Safety-Aware Framing

Metrics:

```yaml
safety_mode_triggered_when_expected: true
mutualizing_serious_concern_count: 0
unsafe_reconciliation_pressure_count: 0
missing_support_language_count: 0
```

## 8. Structured Reasoning Graph

Metrics:

```yaml
construct_count: 0
relationship_count: 0
relationship_without_confidence_count: 0
relationship_without_evidence_or_rationale_count: 0
orphan_construct_count: 0
```

---

# Release Gate Recommendation

A release candidate should pass:

- golden fixture evals
- safety red-team evals
- evidence precision evals
- forbidden-claim evals
- graph relationship evals
- auth ownership tests
- transcript versioning tests

## Suggested Critical Failures

Fail release if:

- high-confidence uncited findings exist
- report evidence points to wrong transcript version
- definitive diagnosis or abuse determinations appear
- users can access another user's resources
- serious safety concerns are mutualized
- worker can double-claim jobs in concurrency tests
