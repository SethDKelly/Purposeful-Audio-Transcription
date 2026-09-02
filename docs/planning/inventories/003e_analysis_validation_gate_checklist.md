# 003-E Analysis Validation Gate Checklist

## Status

Accepted as the Phase 003-E analysis-boundary validation gate checklist.

---

# Purpose

Define the minimum questions later implementation must answer before analysis, prompt, model output, report, export, graph, corpus, hypothesis, safety, or reflection-point changes are accepted.

This checklist is not code.

---

# Gate Principle

```text
An analysis output is not acceptable merely because the model produced it; it is acceptable only when its scope, evidence basis, confidence, hypothesis boundary, safety posture, corpus lineage, and report/export language pass validation.
```

---

# Universal Analysis Checklist

Every analysis implementation must answer:

1. What evidence scope was declared before analysis?
2. Who owns the evidence scope?
3. Which transcript versions were included?
4. Which transcript versions were excluded?
5. Is the scope a single transcript, selected transcript set, case evidence corpus, or future explicit corpus/workspace?
6. Are all evidence quote IDs valid within that scope?
7. Is every claim either evidence-linked or explicitly marked as limitation/uncertainty?
8. Does any claim diagnose, label, adjudicate, or present treatment/legal authority?
9. Does any claim state hidden intent as fact?
10. Does any hypothesis include support level, confidence, alternatives, missing evidence, and non-diagnostic boundary?
11. Does safety posture modify or suppress ordinary reflection guidance where required?
12. Does any corpus claim preserve transcript-version and quote lineage?
13. Does any corpus recurrence claim rely on at least two transcript versions?
14. Are contradictions, weakening evidence, and context differences represented?
15. Are reflection points non-prescriptive and safe under current posture?
16. Can the result be displayed, retained, exported, and reused in corpus reasoning?
17. Are validation errors/warnings logged only as content-free codes/IDs/counts?
18. Are tests defined for both pass and fail cases?

---

# Operation-Specific Checks

## Analysis scope

Required checks:

- scope type is explicit before prompt construction
- owner scope is known
- included transcript version IDs are explicit
- excluded or stale versions are not silently used
- case/corpus scope is explicit when multi-transcript analysis is requested
- hidden all-account transcript analysis is impossible by default

Blocking failure examples:

- prompt compiler uses all retained transcripts without user/case selection
- report cannot identify which transcript version it analyzed
- corpus run mixes case transcripts and unrelated transcripts without explicit scope

---

## Evidence linkage

Required checks:

- every finding/hypothesis/graph edge/report claim cites valid quote IDs or is marked as limitation
- quote IDs are interpreted within transcript/version scope
- evidence span length follows precision rules
- unknown quote IDs fail validation
- duplicated evidence does not inflate confidence

Blocking failure examples:

- finding has no evidence and is not a limitation
- evidence quote ID is invalid for the selected transcript version
- paragraph-length evidence is used where atomic evidence is required

---

## Reflection lens contract

Required checks:

- lens has product-safe name
- lens family is declared
- source-framework references are not authority claims
- permitted inference depth is declared
- confidence ceiling is declared
- forbidden claims are declared
- safety behavior is declared
- output object types are declared

Blocking failure examples:

- a diagnostic-framework-informed lens presents itself as diagnosis
- a module outputs hypotheses without declaring hypothesis support behavior
- a lens bypasses safety suppression or modification rules

---

## Hypothesis handling

Required checks:

- hypothesis source is declared
- support level uses allowed categories
- confidence remains separate from support level
- evidence for, evidence against, missing evidence, and alternatives are represented
- user-provided diagnostic context is not confirmed or ruled out
- non-diagnostic boundary is present
- corpus support is backed by multiple transcript versions when recurrence is claimed

Blocking failure examples:

- output says the transcript confirms BPD, NPD, schizoid traits, or any diagnosis
- output treats a hypothesis as identity or settled fact
- output omits alternative explanations for inferred psychological interpretation

---

## Safety posture

Required checks:

- safety posture is determined or explicitly none-detected
- safety posture has trigger evidence when elevated/high-risk
- elevated/high-risk posture modifies prompt/report/reflection behavior
- ordinary mutual-improvement framing is suppressed when serious safety indicators dominate
- reconciliation pressure is blocked in high-risk contexts
- safety output remains non-diagnostic and non-legal

Blocking failure examples:

- direct threat is treated as ordinary communication conflict
- report recommends confrontation or reconciliation after coercion indicators
- risk is explained primarily as a personality diagnosis

---

## Reflection point

Required checks:

- reflection point links to evidence, finding, or hypothesis
- language is non-prescriptive
- output is self-review oriented
- safety constraints are applied
- contraindications or not-to-be-used-when conditions are present where needed
- treatment, command, confrontation, or reconciliation pressure language is avoided

Blocking failure examples:

- reflection point tells user what to do as treatment
- reflection point encourages unsafe confrontation in high-risk posture
- recommendation appears without evidence basis or limitation

---

## Corpus reasoning

Required checks:

- corpus scope is explicit and owner-scoped
- corpus uses retained saved/case transcript versions only
- recurrence claims cite multiple transcript versions
- contradictions and context differences are represented
- duplicate quotes or reused model conclusions do not count as independent evidence
- deleted/expired/stale evidence invalidates, recomputes, or stale-marks dependent corpus claims

Blocking failure examples:

- one transcript is presented as proof of longitudinal pattern
- corpus claim uses prior model conclusion as evidence without quote lineage
- deleted transcript remains active support for case-corpus pattern

---

## Reasoning graph

Required checks:

- graph node/edge type distinguishes evidence, observation, finding, hypothesis, reflection point, safety posture, limitation, alternative, and corpus pattern
- causal or motive-like edges require stricter evidence and lower confidence ceilings
- edge rationale is evidence-linked or clearly limited
- merged constructs preserve evidence quote lineage
- graph objects have staleness behavior tied to evidence deletion

Blocking failure examples:

- graph edge implies hidden intent as fact
- merged construct loses source quote IDs
- stale graph object remains active after evidence removal

---

## Prompt and repair flow

Required checks:

- prompt includes scope, evidence basis, forbidden claims, confidence rules, safety posture, and output schema
- prompt does not include unnecessary corpus content
- repair flow fixes validation errors without expanding scope
- raw output reuse in repair is reviewed under privacy/logging policy
- prompt hashes reflect boundary-relevant versions

Blocking failure examples:

- repair prompt introduces additional evidence not in original scope
- prompt logs contain transcript text or raw completions
- corpus prompt dumps every retained transcript instead of scoped evidence

---

## Report and export readiness

Required checks:

- report identifies scope type and source transcript versions
- report language avoids diagnosis, treatment authority, legal conclusions, hidden intent as fact, and moral verdicts
- report includes confidence, limitations, alternatives, and safety posture where relevant
- exported artifact preserves evidence scope and version basis
- export readiness blocks unsupported corpus or hypothesis claims

Blocking failure examples:

- export loses evidence appendix/source version metadata
- report says `this person is narcissistic` or equivalent identity label
- report displays corpus conclusion with no lineage

---

# Required Test Families

Later implementation should add tests for:

```text
analysis_scope_required
analysis_scope_owner_checked
transcript_version_basis_required_for_retained_analysis
evidence_quote_id_unknown_fails
evidence_quote_wrong_version_fails
finding_without_evidence_fails_unless_limitation
confidence_ceiling_enforced
inferred_finding_requires_alternative
hypothesis_support_level_allowed
hypothesis_forbidden_confirmed_diagnosis_fails
user_provided_diagnosis_not_validated
intent_as_fact_blocked
therapeutic_authority_blocked
safety_posture_high_risk_modifies_output
safety_mutualization_blocked
reconciliation_pressure_blocked
reflection_point_non_prescriptive
reflection_point_safety_constrained
corpus_scope_explicit
corpus_recurrence_requires_multiple_versions
corpus_prior_model_conclusion_not_evidence
corpus_deleted_evidence_stale_marks_claim
reasoning_graph_edge_boundary_enforced
report_scope_required
export_readiness_preserves_scope_and_versions
validation_events_content_free
```

---

# Validation Ordering

Recommended validator order:

```text
1. Analysis scope and owner check
2. Transcript version basis check
3. Evidence quote ID and precision check
4. Safety posture check
5. Hypothesis/support boundary check
6. Diagnostic/intent/authority text check
7. Confidence calibration check
8. Reflection point safety check
9. Corpus reasoning/staleness check
10. Reasoning graph boundary check
11. Report scope/language check
12. Export readiness check
13. Content-free validation event/log check
```

Reason:

Scope and evidence errors should block before report polish, while safety errors should be able to suppress or modify downstream reflection output.

---

# Decision

This checklist carries forward to later implementation phases as part of the analysis scope gate, evidence linkage gate, hypothesis boundary gate, safety posture gate, corpus reasoning gate, reasoning graph boundary gate, report scope gate, export readiness gate, privacy boundary gate, evaluation gate, and regression gate.
