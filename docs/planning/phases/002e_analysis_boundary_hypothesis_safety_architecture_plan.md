# 002-E — Analysis Boundary, Hypothesis, and Safety Architecture Plan

## Status

Complete.

This subgroup translates the accepted analysis-boundary, hypothesis-aware reflection, therapeutic reflection lens, safety, and corpus-reasoning decisions into architecture planning requirements.

---

# Purpose

002-E defines how the system should preserve evidence-limited, non-diagnostic, safety-aware reasoning before cost/deployment architecture planning begins.

It answers:

- What is the analysis boundary?
- How should reflection lenses be represented architecturally?
- How should therapeutic and diagnostic-framework-informed reasoning be bounded?
- How should psychological hypotheses be structured?
- How should safety posture override ordinary analysis?
- How should corpus-level evidence affect confidence and graph enrichment?
- What validation gates are required before output display/export/corpus reuse?
- What must be handed to 002-F?

---

# Outputs

| Output | Document |
|---|---|
| Analysis boundary, hypothesis, and safety architecture plan | `../architecture/002e_analysis_boundary_hypothesis_safety_architecture_plan.md` |
| Analysis boundary contracts | `../inventories/002e_analysis_boundary_contracts.md` |
| Validation gate matrix | `../inventories/002e_validation_gate_matrix.md` |

---

# Accepted Decisions

## 1. Analysis Boundary is enforceable architecture

The analysis boundary should be enforced across lens metadata, prompt construction, output schemas, validators, report rendering, reasoning graph rules, evaluation fixtures, and UI copy.

## 2. Reflection Lens is the product concept

Implementation may continue to use modules internally, but product architecture should map modules to `ReflectionLensContract` records.

## 3. Therapeutic frameworks are reasoning references, not authority

Therapeutic, behavioral, cognitive, psychodynamic, attachment-informed, trauma-informed, and diagnostic-framework-informed concepts may inform reasoning.

They must not become diagnosis, treatment, pathology detection, clinical assessment, or professional authority.

## 4. Psychological Hypothesis needs a bounded contract

A hypothesis should preserve source, scope, evidence for, evidence against, missing evidence, alternatives, support level, confidence, safety considerations, and non-diagnostic boundary.

## 5. SafetyPosture needs a structured representation

Safety-aware framing is a concept-level override.

It should be represented as structured output posture capable of affecting prompts, lenses, reports, reflection points, UI banners, and validators.

## 6. Corpus-aware confidence must preserve evidence lineage

Corpus-level reasoning may enrich the reasoning graph across multiple retained transcripts, but only when scope is explicit and evidence lineage is preserved.

Corpus output may represent recurrence, contradiction, strengthening, weakening, context split, temporal change, or insufficient corpus evidence.

## 7. Reflection Point should replace prescriptive recommendation semantics

Product architecture should move from `recommendation` / `intervention` language toward `ReflectionPoint` as a non-prescriptive, evidence-linked self-review prompt.

---

# Resolved / Advanced 002-D Handoff Items

| 002-D Handoff | 002-E Resolution |
|---|---|
| Bounded psychological hypotheses | Add `PsychologicalHypothesis` and `HypothesisSupportAssessment` contracts |
| Confidence calibration across single/corpus evidence | Add support-level and corpus-aware confidence rules |
| Safety-aware override behavior | Add `SafetyPosture` contract and safety-specific validation gates |
| Diagnostic-framework-informed reasoning | Bound as source-framework reference, not authority |
| Prompt/input scope controls | Add `AnalysisScope` requirements |
| Output validation and report language | Add validation gate matrix |
| Corpus-aware reasoning graph enrichment | Add `CorpusPatternAssessment` and graph boundary rules |
| Contradiction and alternatives | Add first-class evidence-against and alternative explanation requirements |

---

# Handoff to 002-F

002-F should define cost state and personal deployment architecture without corrupting analysis semantics.

Cost state may affect system availability, wake/sleep behavior, worker idleness, and background job timing.

It must not corrupt:

- in-flight analysis scope
- corpus scope
- safety posture
- validation results
- evidence lineage
- deletion cascades
- retained graph objects

---

# Non-goals

002-E does not implement:

- schema migrations
- prompt rewrites
- validators
- evaluation fixtures
- safety detection logic
- corpus retrieval logic
- graph storage changes
- report rendering changes
- UI copy
- deployment changes

Implementation remains blocked until Phase 002-I exit review authorizes the next phase.

---

# Exit Criteria

002-E is complete when:

- analysis boundary architecture is defined
- reflection lens contract is defined
- hypothesis contract is defined
- safety posture contract is defined
- corpus-aware confidence rules are defined
- validation gate matrix exists
- report/output requirements are documented
- 002-F handoff is explicit

All criteria are satisfied.

---

# Next Phase

Proceed to:

```text
002-F — Cost State and Personal Deployment Architecture Plan
```
