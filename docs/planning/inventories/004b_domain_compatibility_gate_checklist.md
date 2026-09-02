# 004-B Domain Compatibility Gate Checklist

## Status

Accepted as the Phase 004-B domain compatibility gate checklist.

---

# Purpose

Define the minimum checks for 004-B and later domain-terminology implementation work.

This checklist prevents concept-safe names from becoming unsafe physical renames or product-boundary drift.

---

# Gate Principle

```text
A domain terminology change is acceptable only when it improves concept alignment without breaking compatibility, weakening evidence lineage, collapsing support/confidence semantics, or bypassing lifecycle, privacy, analysis, report, corpus, UI, migration, and regression gates.
```

---

# Universal Checks

Every domain compatibility change must answer:

1. Does the change identify the Phase 004 subgroup?
2. Does the change identify the Phase 003 work package it executes?
3. Does the change preserve current runtime behavior unless explicitly authorized otherwise?
4. Does the change avoid destructive class/table/API field renames?
5. If it introduces a concept alias, is the existing implementation object still available?
6. If it introduces a concept contract, is it additive and safe to import without side effects?
7. Does it keep user-facing/product-facing terminology distinct from implementation terminology?
8. Does it keep `Confidence` separate from hypothesis support levels?
9. Does it preserve transcript-version and evidence-quote lineage expectations?
10. Does it avoid diagnosing, labeling, adjudicating, or treating hypotheses as confirmed traits?
11. Does it avoid expanding corpus reasoning without explicit scope?
12. Does it avoid expanding reports/exports/UI before the relevant later subgroup gates?
13. Does it avoid production migrations?
14. Are tests or verification recorded?
15. Are deferred decisions explicit?

---

# 004-B Checks

## Documentation authority gate

Required:

- `docs/domain/README.md` points to the accepted authority stack.
- 004-B implementation record names the guardrails and 003-B work packages.
- Phase indexes are updated after completion.

Blocking failures:

- domain docs cite older design package as higher authority than concepts
- guardrails are bypassed
- a new independent status source is created

## Terminology drift gate

Required:

- legacy/current implementation terms are mapped to accepted concept terms
- internal terms remain allowed only as implementation terms
- product-facing concept names are available for later code

Blocking failures:

- `WorkflowRun`, `ModuleRun`, or `SynthesisReport` are described as final product concepts
- `interventions` or recommendations are treated as safe final user-facing language
- `safety_mode` is treated as sufficient final safety architecture

## Domain compatibility gate

Required:

- aliases are additive
- existing classes remain importable
- no table/column/API field rename occurs
- no migration is introduced

Blocking failures:

- class/table names are renamed without migration plan
- existing service imports are broken
- persisted data shape is changed casually

## Analysis scope gate

Required foundation:

- `AnalysisScope` exists
- scope type can represent single transcript version, selected transcript set, and case evidence corpus
- explicitness can be checked

Deferred:

- service enforcement
- prompt compiler integration
- UI/report display

## Transcript version basis gate

Required foundation:

- contracts can carry transcript version IDs
- corpus/report contracts can preserve version basis

Deferred:

- requiring `EvidenceQuote.transcript_version_id`
- migration/backfill
- report/API enforcement

## Evidence linkage gate

Required foundation:

- hypothesis, reflection point, corpus, and report contracts can carry evidence quote IDs

Deferred:

- validators enforcing all claim/evidence relations
- graph/report/export integration

## Hypothesis boundary gate

Required foundation:

- `PsychologicalHypothesis` exists separately from `Finding`
- `HypothesisSupportAssessment` carries support level, evidence for/against, missing evidence, alternatives, limitations, and confidence
- boundary text states non-diagnostic limitation

Blocking failures:

- support labels include `confirmed`, `diagnosed`, or equivalent clinical certainty
- user-provided diagnosis is treated as system truth

## Support-level separation gate

Required:

- `HypothesisSupportLevel` is separate from `Confidence`
- tests verify the two are not collapsed

Blocking failures:

- confidence enum is reused as hypothesis support relation
- support level implies diagnostic certainty

## Safety posture gate

Required foundation:

- `SafetyPostureLevel` exists
- `SafetyPosture` can carry posture, trigger categories, evidence quote IDs, suppressed sections, required report behavior, and limitations
- high-risk and immediate/crisis posture levels can be detected as override states

Deferred:

- validator integration
- report behavior enforcement
- UI layout/action suppression

## Reflection point gate

Required foundation:

- `ReflectionPoint` exists
- it is non-prescriptive by default
- it can link to evidence, findings, hypotheses, and safety posture

Deferred:

- migration from `interventions`
- report/UI/export rendering

## Corpus scope gate

Required foundation:

- `CaseEvidenceCorpus` alias exists
- `CorpusPatternAssessment` carries scope, version IDs, quote IDs, recurrence, contradiction, temporal change, and limitations
- tests distinguish single-version claims from longitudinal basis

Deferred:

- query enforcement
- stale/deleted evidence handling
- duplicate evidence controls

## Report scope gate

Required foundation:

- `ReportScope` exists
- it carries analysis scope, reflection lenses, validation state, safety posture, stale flag, export readiness, and boundary reminder

Deferred:

- backend report response integration
- report renderer implementation
- export readiness enforcement

## Regression gate

Required foundation:

- tests cover runtime aliases, mappings, scope explicitness, hypothesis support separation, safety override, reflection point defaults, corpus basis, report scope, and alias construction

Not performed here:

- test execution in CI, because GitHub Actions remain intentionally disabled
- local test execution in this chat

---

# Later Subgroup Warning

004-B prepares contract surfaces.

It does not authorize later code to assume gates are fully enforced.

The following remain later-gated:

```text
lifecycle enforcement
privacy owner-scope enforcement
route/API migration
prompt construction
validator behavior
report rendering
export behavior
UI display
cost-state behavior
production migrations
GitHub Actions restoration
```

---

# Decision

004-B satisfies the domain compatibility gate for an additive contract foundation.

Later implementation must still satisfy behavioral gates before expanding usage.
