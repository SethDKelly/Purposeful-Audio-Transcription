# Domain Terminology Compatibility Guide

## Status

Accepted as the Phase 004-B implementation-facing domain terminology guide.

This document is a compact bridge between current prototype code names and accepted concept language.

It does not authorize destructive renames, schema migrations, API rewrites, prompt rewrites, report renderer rewrites, UI rewrites, or production data migrations.

---

# Authority

Follow the repository authority order:

```text
docs/concepts/
→ Phase 003 exit review and Phase 004 authorized scope
→ Phase 004 overview and current subgroup summary
→ directly relevant Phase 003 gates and work packages
→ reconciled implementation docs
→ code
→ legacy/reference/historical docs
```

Current runtime contracts live at:

```text
backend/domain/concept_contracts.py
```

---

# Compatibility Principle

```text
Keep useful implementation foundations, introduce concept-safe aliases and contracts, and defer destructive renames until retention, privacy, analysis, and evaluation gates are ready.
```

Existing implementation names are allowed internally when they remain stable and useful.

Product-facing, report-facing, UI-facing, and future API-facing language should move toward accepted concept terms.

---

# Core Mapping

| Current / legacy implementation term | Accepted concept term | Compatibility posture |
|---|---|---|
| `WorkflowRun` | `ReflectionRun` | Alias first; migrate later only if gated |
| `ModuleDefinition` | `ReflectionLens` | Alias first; wrap with `ReflectionLensContract` |
| `ModuleRun` | `LensExecution` | Alias first; migrate later only if gated |
| `SynthesisReport` | `ReflectionReport` | Alias first; add `ReportScope` before user-facing expansion |
| `FindingType.HYPOTHESIS` | `PsychologicalHypothesis` / `HypothesisSupportAssessment` | Split/promote |
| `FindingType.INTERVENTION` / `interventions` | `ReflectionPoint` | Split/promote and change product language |
| `safety_mode` / `safety_flags` | `SafetyPosture` | Split/promote into structured safety posture |
| `CaseDetail` | `CaseEvidenceCorpus` | Retain and harden |
| `SourceType.AUDIO` | Recording source marker | Retain and harden; lifecycle belongs to SourceArtifact planning |

---

# Runtime Contract Surface

`backend/domain/concept_contracts.py` provides:

```text
ReflectionRun
ReflectionLens
LensExecution
ReflectionReport
CaseEvidenceCorpus
AnalysisScope
AnalysisScopeType
ReflectionLensContract
HypothesisSupportLevel
HypothesisSupportAssessment
PsychologicalHypothesis
SafetyPostureLevel
SafetyPosture
ReflectionPoint
CorpusPatternAssessment
ReportScope
ValidationStatus
DomainTermMapping
concept_term_for()
get_domain_term_mapping()
```

The aliases preserve runtime compatibility with existing classes.

The contracts provide additive concept-safe structures for later Phase 004 subgroups.

---

# What This Means for Implementation

## Allowed now

- Import concept-safe aliases/contracts from `backend.domain.concept_contracts`.
- Use `ReflectionRun` as the concept alias for `WorkflowRun`.
- Use `ReflectionLens` and `LensExecution` as aliases for module concepts.
- Use `AnalysisScope`, `ReportScope`, `SafetyPosture`, `ReflectionPoint`, and hypothesis-support contracts in new implementation code when the subgroup authorizes that surface.
- Keep existing persisted tables, fields, route names, and data shapes stable.

## Not allowed from 004-B alone

- Rename tables or columns.
- Rename existing classes destructively.
- Remove legacy fields such as `workflow_run_id`, `module_id`, `safety_mode`, or `interventions`.
- Change public API response fields without compatibility planning.
- Expand corpus reasoning, export behavior, UI/report rendering, prompt construction, or validators outside their authorized subgroups.

---

# Notes by Concept

## Transcript and ConversationRecord

`Transcript` remains the practical near-term aggregate root.

`ConversationRecord` remains conceptual unless later lifecycle/source-artifact implementation proves a separate object is needed.

## TranscriptVersion and EvidenceQuote

`TranscriptVersion` remains the stable evidence basis.

`EvidenceQuote.transcript_version_id` may remain optional for compatibility today, but retained analysis should move toward version-required evidence after migration gates.

## WorkflowRun and ReflectionRun

`WorkflowRun` remains internal orchestration.

`ReflectionRun` is the concept-safe alias for user-facing analysis execution over an explicit evidence scope.

## Modules and Reflection Lenses

`ModuleDefinition` and `ModuleRun` remain implementation foundations.

`ReflectionLensContract` should wrap module semantics with product-safe lens metadata, confidence ceilings, inference depth, evidence requirements, safety behavior, and forbidden claims.

## Hypotheses

Hypotheses are not ordinary findings and not diagnoses.

`HypothesisSupportAssessment.support_level` is separate from `Confidence`.

## Safety

Boolean `safety_mode` and list-style `safety_flags` are transitional implementation signals.

`SafetyPosture` is the target concept for report behavior, output suppression/modification, and UI display.

## Reflection Points

Reflection points replace ordinary recommendation/intervention language for product-facing use.

They are evidence-linked, non-prescriptive, self-review oriented, safety-aware, and limitation-bounded.

## Case Evidence Corpus

A case is more than a folder when used for analysis.

`CaseEvidenceCorpus` is the concept alias for explicit, owner-scoped, multi-transcript reasoning boundaries.

## Reports

`SynthesisReport` remains current implementation output.

`ReflectionReport` is the product/concept alias.

`ReportScope` should be added before reports become more persuasive, export-heavy, or corpus-heavy.

---

# Required Gate Awareness

Any future work using these contracts must still satisfy applicable gates from Phase 003 and Phase 004, especially:

```text
domain compatibility gate
terminology drift gate
analysis scope gate
transcript version basis gate
evidence linkage gate
hypothesis boundary gate
support-level separation gate
safety posture gate
reflection point gate
corpus scope gate
report scope gate
privacy boundary gate
retention gate
regression gate
release readiness gate
```

---

# Decision

This guide and `backend/domain/concept_contracts.py` establish the Phase 004-B compatibility foundation for domain terminology and concept contracts.
