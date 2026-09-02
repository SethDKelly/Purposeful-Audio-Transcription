# 003-B — Domain Terminology and Concept Mapping Implementation Plan

## Status

Complete.

This subgroup converts accepted concept/domain mappings into implementation-ready terminology and mapping plans.

---

# Purpose

003-B prepares domain refactor planning without changing code or schemas.

It answers:

- Which existing domain artifacts should be preserved?
- Which code names should become internal implementation terms rather than product-facing terms?
- Which concept names should be introduced as aliases, contracts, or future schema objects?
- Which renames are unsafe to perform immediately?
- Which work packages should feed 003-C through 003-G?

---

# Outputs

| Output | Document |
|---|---|
| Domain terminology and mapping implementation plan | `../architecture/003b_domain_terminology_concept_mapping_implementation_plan.md` |
| Domain concept mapping inventory | `../inventories/003b_domain_concept_mapping_inventory.md` |
| Domain terminology migration work packages | `../inventories/003b_domain_terminology_migration_work_packages.md` |

---

# Existing Artifacts Reviewed

003-B reviewed the accepted Phase 002 mapping and the current domain package, including:

```text
docs/design/03_domain_model.md
backend/domain/transcript.py
backend/domain/finding.py
backend/domain/workflow.py
backend/domain/case.py
backend/domain/synthesis.py
backend/domain/enums.py
```

---

# Accepted Decisions

## 1. The current domain model is useful and should be preserved

The existing implementation has strong foundations for transcripts, transcript versions, evidence quotes, findings, graph constructs, workflow/module runs, cases, synthesis reports, and confidence values.

003-B does not recommend discarding the prototype domain model.

## 2. Transcript remains the practical near-term aggregate root

`Transcript` remains the near-term implementation aggregate.

`ConversationRecord` remains a conceptual umbrella unless later lifecycle planning proves a separate implementation object is needed.

## 3. Version binding should be hardened later

`TranscriptVersion` and `EvidenceQuote` already support version-aware analysis, but later implementation should make retained analysis and reports version-bound by rule.

## 4. Workflow/module language becomes internal implementation language

`WorkflowRun` maps to `ReflectionRun`.

`ModuleDefinition` and `ModuleRun` map to `ReflectionLens` / lens execution concepts.

Do not physically rename these immediately.

## 5. Hypothesis, SafetyPosture, ReflectionPoint, and CorpusPatternAssessment need stronger representations

`FindingType.HYPOTHESIS`, `safety_mode`, `safety_flags`, `interventions`, and current graph relationships are transitional foundations, not mature concept representations.

## 6. ReflectionPoint replaces intervention/recommendation semantics in product language

Intervention/recommendation wording is not safe as default user-facing product terminology.

Later implementation should migrate to evidence-linked, non-prescriptive, safety-bounded `ReflectionPoint` semantics.

## 7. Case should become the explicit Case Evidence Corpus boundary

Case remains a strong implementation foundation, but later work should make case membership retention-significant, privacy-significant, and corpus-reasoning significant.

## 8. Confidence and hypothesis support remain separate

Confidence should describe evidentiary strength.

Hypothesis support should describe relation to a hypothesis.

Do not force both meanings into one enum.

---

# Key Mapping Results

```text
WorkflowRun -> ReflectionRun
ModuleDefinition / ModuleRun -> ReflectionLens / LensExecution
SynthesisReport -> ReflectionReport
FindingType.HYPOTHESIS -> PsychologicalHypothesis / HypothesisSupportAssessment
FindingType.INTERVENTION / interventions -> ReflectionPoint
safety_mode / safety_flags -> SafetyPosture
Case + transcript versions -> Case Evidence Corpus
SourceType.AUDIO -> Recording source marker; lifecycle handled by SourceArtifact / RecordingArtifact planning
```

---

# Handoff to 003-C

003-C should use this mapping to prepare implementation plans for lifecycle and retention objects before corpus reasoning or report expansion is implemented.

Primary handoff concepts:

- SourceArtifact / RecordingArtifact
- RetentionRule
- transcript draft state
- transcript version retention and staleness
- evidence quote retention
- derived artifact retention inheritance
- export artifact lifecycle
- deletion cascades

---

# Non-goals

003-B does not implement:

- class renames
- table renames
- database migrations
- API field changes
- prompt changes
- report renderer changes
- UI changes
- validators
- tests
- data migrations

---

# Exit Criteria

003-B is complete when:

- current domain artifacts have been reviewed at planning level
- preserve/alias/promote/new/defer decisions are documented
- implementation-facing mapping inventory exists
- terminology migration work packages exist
- Phase 003 indexes are updated
- 003-C handoff is explicit
- broad implementation remains blocked

All criteria are satisfied.

---

# Next Phase

Proceed to:

```text
003-C — Data Lifecycle / Retention Foundation Implementation Plan
```
