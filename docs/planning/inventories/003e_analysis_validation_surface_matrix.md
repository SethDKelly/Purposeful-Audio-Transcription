# 003-E Analysis Validation Surface Matrix

## Status

Accepted as the Phase 003-E analysis validation surface implementation matrix.

---

# Purpose

Map accepted analysis-boundary concepts to current implementation surfaces, remaining risks, target implementation posture, and gates.

This matrix is implementation planning only.

---

# Matrix Legend

| Status | Meaning |
|---|---|
| `existing_foundation` | Useful implementation exists and should be preserved |
| `existing_but_incomplete` | Useful implementation exists but lacks accepted analysis-boundary semantics |
| `new_or_equivalent` | Needs a new object, field set, config registry, validator, or service contract |
| `policy_only_initially` | May begin as documented/configured policy before schema/code |
| `defer` | Valid but not needed for current implementation foundation |

---

# Surface Matrix

| Surface / Concept | Current Implementation Surface | Status | Required Implementation Target | Primary Gates |
|---|---|---|---|---|
| Analysis scope | workflow/module run transcript ID and optional transcript version ID | existing_but_incomplete | explicit `AnalysisScope` with scope type, owner, included/excluded transcript versions, case/corpus scope, user context, requested lenses | analysis_scope_gate, privacy_boundary_gate |
| Transcript version basis | `WorkflowRun.transcript_version_id`, `Transcript.current_version_id`, version-aware bundle retrieval | existing_foundation | require version basis for retained analysis and report/corpus outputs | transcript_version_basis_gate, report_scope_gate |
| Evidence index | `EvidenceIndexService`, evidence quote IDs, quote text maps | existing_foundation | scope-aware evidence retrieval; no draft/deleted/stale evidence in retained/corpus runs | evidence_linkage_gate, corpus_staleness_gate |
| Reflection lens contract | `ModuleConfig`, module YAML, prompt files | existing_but_incomplete | `ReflectionLensContract` wrapper around modules with source-frameworks, forbidden claims, safety behavior, output objects | reflection_lens_contract_gate |
| Prompt compiler | `PromptCompiler`, shared instructions, validation section, safety overlays | existing_foundation | prompt receives explicit `AnalysisScope`, safety posture, hypothesis/support rules, corpus rules, privacy/logging constraints | prompt_boundary_gate, safety_posture_gate |
| Shared framework instructions | `config/framework/shared_instructions.md` | existing_foundation | reconcile language with accepted terminology and non-diagnostic/corpus rules | hypothesis_boundary_gate, corpus_reasoning_gate |
| Output schema | `ModuleRunOutput`, `FindingInput`, `SynthesisOutput` | existing_but_incomplete | add/wrap contracts for hypotheses, support assessments, safety posture, reflection points, report scope, validation result | analysis_scope_gate, hypothesis_boundary_gate |
| Output parser | JSON extraction, alias normalization, enum coercion, default alternatives | existing_foundation | preserve compatibility while avoiding silent conversion that weakens boundaries | support_level_separation_gate, regression_gate |
| Module output validator | evidence, quote IDs, confidence ceiling, alternatives, evidence precision, construct coverage | existing_foundation | extend into boundary categories and feed `AnalysisValidationResult` | evidence_linkage_gate, confidence_calibration_gate |
| Safety validator | diagnostic/legal/intent/abuse/attachment/mutualization pattern checks | existing_foundation | tie to structured `SafetyPosture`; distinguish warning vs blocking by posture/scope | safety_posture_gate, safety_override_gate |
| Safety policy config | suppress/modify modules, safety framing, mutualization prohibition | existing_foundation | map to structured safety posture and reflection-lens safety behavior | reflection_lens_contract_gate, safety_override_gate |
| Workflow engine | creates runs, stores version ID, runs module waves, suppresses modules in safety mode | existing_foundation | require scope object and validation result lifecycle before completion/report/corpus reuse | analysis_scope_gate, safety_posture_gate |
| Module runner | compile, LLM call, parse, validate, safety validate, retry, persist | existing_foundation | integrate unified validation result and privacy-aware raw output handling | prompt_boundary_gate, log_redaction_gate |
| Raw/parsed model output persistence | `ModuleRun.raw_output`, `parsed_output` | existing_but_incomplete | retention/privacy/encryption-aware persistence and validation state | privacy_boundary_gate, field_encryption_target_gate |
| Finding | `Finding`, `FindingRow`, `FindingType.HYPOTHESIS` | existing_but_incomplete | separate ordinary finding from psychological hypothesis/support assessment | hypothesis_boundary_gate, support_level_separation_gate |
| Recommendations/interventions | `recommendations`, synthesis `interventions`, `FindingType.INTERVENTION` | existing_but_incomplete | migrate product semantics to `ReflectionPoint` | reflection_point_gate, safety_override_gate |
| Confidence | `Confidence`, confidence ceilings, ranks | existing_foundation | keep separate from support level and corpus enrichment type | confidence_calibration_gate, support_level_separation_gate |
| Reasoning graph constructs | `Construct`, `ConstructRelationship`, graph merge/convergence | existing_foundation | boundary-aware node/edge vocabulary and evidence lineage/staleness semantics | reasoning_graph_boundary_gate, corpus_staleness_gate |
| Synthesis report | `SynthesisReport`, `SynthesisOutput`, `SynthesisReportRow.report_json` | existing_but_incomplete | `ReportScope`, scope/version basis, safety posture, hypothesis/corpus validation | report_scope_gate, export_readiness_gate |
| Longitudinal synthesis | `LongitudinalSynthesisService` case handoff with >=2 transcripts and version IDs | existing_foundation | reusable `CorpusPatternAssessment`, explicit scope, duplicate evidence controls, owner checks, staleness handling | corpus_reasoning_gate, corpus_scope_gate |
| Safety event rows | `SafetyEventRow` with risk/category/detail fields | existing_but_incomplete | align with structured safety posture and content-free validation events | safety_posture_gate, lifecycle_event_redaction_gate |
| Validation persistence | module run errors/warnings, safety flags | existing_but_incomplete | unified `AnalysisValidationResult` or equivalent record | analysis_validation_result_gate |
| Evaluation runs | `EvaluationRunRow`, release-gate history | existing_but_incomplete | fixtures for boundary, safety, corpus, report/export, and privacy-aware validation | evaluation_gate, regression_gate |
| Export readiness | no clear first-class export artifact | new_or_equivalent | export validator preserving report scope, evidence/version basis, limitations, and privacy boundaries | export_readiness_gate, export_boundary_gate |
| UI/report warning display | report/client surfaces | existing_but_incomplete | clear validation pass/warning/blocking behavior without leaking sensitive content | ui_language_gate, report_scope_gate |

---

# Current Strengths to Preserve

- evidence quote ID validation
- confidence-ceiling enforcement
- alternative-explanation enforcement for inferred findings
- evidence precision checks
- paragraph-length evidence warnings
- construct coverage warnings
- safety language pattern checks
- safety-mode module suppression/modification
- transcript-version-bound workflow runs
- structured graph handoff
- longitudinal synthesis requiring at least two case transcripts
- prompt hash/module version/compiler version tracking

---

# Priority Gaps

## P0 gaps

- `AnalysisScope` missing as first-class execution contract
- `SafetyPosture` missing as structured gate driver
- hypothesis support not separated from findings
- validation results not unified across module/safety/report/corpus/export
- corpus reasoning scope/staleness not reusable enough
- recommendations/interventions still use old semantics

## P1 gaps

- reflection lens contracts not explicit in module registry
- report/export readiness validation not first-class
- graph edge vocabulary not fully boundary-aware
- prompt repair/raw output handling needs privacy review
- evaluation fixtures need to encode accepted boundary failures

## P2 gaps

- advanced lens taxonomy and source-framework registry
- future workspace corpus support
- advanced contradiction/change-over-time scoring

---

# Target Object Set

Later implementation should consider this minimum target set:

```text
AnalysisScope
ReflectionLensContract
PsychologicalHypothesis
HypothesisSupportAssessment
SafetyPosture
ReflectionPoint
CorpusPatternAssessment
AnalysisValidationResult
ReportScope
ExportValidationResult
```

Equivalent means a clearly documented field/config/service contract may be acceptable before a dedicated database table, as long as gates pass.

---

# Decision

This matrix is ready to feed the 003-E work packages, 003-F control-plane planning, 003-G UI/report planning, and 003-H exit review.
