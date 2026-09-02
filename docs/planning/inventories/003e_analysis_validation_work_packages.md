# 003-E Analysis Validation Work Packages

## Status

Accepted as the Phase 003-E analysis-boundary and validation implementation-planning work package inventory.

These packages are not implementation authorization.

---

# Purpose

Break analysis-boundary and validation work into later implementation-ready packages.

Each package must be gated before code, schema, prompt, validator, graph, report, export, corpus, UI, or production data migration changes are accepted.

---

# Work Package Legend

| Field | Meaning |
|---|---|
| ID | Stable Phase 003-E work package identifier |
| Priority | P0, P1, or P2 |
| Target | Main implementation area later affected |
| Gate | Acceptance gate that must pass before implementation is accepted |

---

# P0 Work Packages

## ABV-WP-001 — AnalysisScope execution contract

Priority: P0

Target:

```text
backend/domain/workflow.py
backend/services/workflow_engine.py
backend/services/module_runner.py
backend/services/prompt_compiler.py
backend/api/routes/workflows.py
future /api/v1 analysis routes
```

Purpose:

Define exactly what evidence an analysis run is allowed to use before prompt construction begins.

Required planning outcomes:

- scope type enum
- owner and privacy binding
- transcript version inclusion/exclusion
- case/corpus scope binding
- user-provided context and hypotheses handling
- scope propagation to workflow, module, report, graph, export, and validation layers
- explicit prohibition against hidden all-account corpus analysis

Gate:

```text
analysis_scope_gate
transcript_version_basis_gate
privacy_boundary_gate
```

---

## ABV-WP-002 — Transcript-version and evidence-basis hardening

Priority: P0

Target:

```text
backend/domain/transcript.py
backend/db/models.py
backend/repositories/transcript_repository.py
backend/services/evidence_index.py
backend/services/workflow_engine.py
backend/services/module_output_validator.py
```

Purpose:

Ensure retained analysis and reports are bound to the transcript versions and quote IDs they actually analyzed.

Required planning outcomes:

- retained analysis requires transcript version ID
- report scope records source transcript versions
- evidence quote IDs are interpreted within transcript/version scope
- stale/deleted evidence is excluded from active analysis
- old reports do not silently point to new transcript text

Gate:

```text
transcript_version_basis_gate
evidence_linkage_gate
corpus_staleness_gate
```

---

## ABV-WP-003 — ReflectionLensContract compatibility plan

Priority: P0

Target:

```text
backend/core/module_registry.py
config/modules/
config/prompts/
config/framework/
```

Purpose:

Map implementation modules to product-safe reflection lens contracts.

Required planning outcomes:

- lens family vocabulary
- source-framework reference field
- permitted inference depth
- confidence ceiling
- forbidden claims
- required limitations
- safety behavior
- corpus/hypothesis support flags
- output object expectations
- migration plan from module labels to reflection-lens language

Gate:

```text
reflection_lens_contract_gate
hypothesis_boundary_gate
safety_override_gate
```

---

## ABV-WP-004 — Unified AnalysisValidationResult plan

Priority: P0

Target:

```text
backend/services/module_output_validator.py
backend/services/safety_validator.py
backend/services/output_parser.py
backend/services/module_runner.py
backend/domain/workflow.py
future persistence layer
```

Purpose:

Create a unified validation result contract across module, safety, corpus, report, and export validation.

Required planning outcomes:

- validator category vocabulary
- critical failure vs warning distinction
- blocked output section semantics
- required revision semantics
- content-free validation event fields
- persistence or runtime-only decision
- report/export/corpus reuse behavior when validation fails

Gate:

```text
analysis_validation_result_gate
log_redaction_gate
regression_gate
```

---

## ABV-WP-005 — PsychologicalHypothesis and support assessment plan

Priority: P0

Target:

```text
backend/domain/finding.py
backend/domain/enums.py
backend/schemas/module_output_v1.py
backend/services/output_parser.py
backend/services/module_output_validator.py
report/corpus services
```

Purpose:

Separate bounded hypothesis reasoning from ordinary findings and diagnostic labeling.

Required planning outcomes:

- `PsychologicalHypothesis` candidate fields
- `HypothesisSupportAssessment` candidate fields
- allowed support levels
- forbidden support levels
- hypothesis source field
- user-provided diagnosis handling rule
- evidence for/evidence against/missing evidence/alternatives
- corpus support summary linkage
- migration from `FindingType.HYPOTHESIS`

Gate:

```text
hypothesis_boundary_gate
support_level_separation_gate
user_provided_diagnosis_handling_gate
```

---

## ABV-WP-006 — SafetyPosture implementation plan

Priority: P0

Target:

```text
backend/services/safety_validator.py
backend/services/safety_policy.py
config/safety_policy.yaml
backend/db/models.py
workflow/report/corpus services
```

Purpose:

Move from boolean `safety_mode` and string safety flags toward structured safety posture.

Required planning outcomes:

- posture values
- trigger evidence linkage
- risk indicator vocabulary
- confidence/uncertainty handling
- suppressed/modified lens behavior
- required report sections
- reflection point constraints
- validator strictness by posture
- safety event/content-free logging posture

Gate:

```text
safety_posture_gate
safety_override_gate
lifecycle_event_redaction_gate
```

---

## ABV-WP-007 — ReflectionPoint migration plan

Priority: P0

Target:

```text
backend/schemas/module_output_v1.py
backend/domain/finding.py
backend/domain/synthesis.py
report renderer
frontend/report views
```

Purpose:

Replace product-facing recommendation/intervention semantics with evidence-linked self-review prompts.

Required planning outcomes:

- `ReflectionPoint` candidate fields
- mapping from recommendations/interventions
- safety constraints
- evidence/source finding linkage
- non-prescriptive language rules
- report display rules
- export rules

Gate:

```text
reflection_point_gate
safety_override_gate
report_scope_gate
```

---

## ABV-WP-008 — CorpusPatternAssessment and corpus validation plan

Priority: P0

Target:

```text
backend/services/longitudinal_synthesis_service.py
backend/services/structured_graph_service.py
backend/services/graph_merge_service.py
backend/repositories/
case/corpus/report services
```

Purpose:

Make multi-transcript reasoning explicit, scoped, lineage-preserving, and stale-aware.

Required planning outcomes:

- corpus scope object or service contract
- recurrence threshold
- contradiction/weakening/context split/temporal change handling
- duplicate quote/evidence controls
- transcript version and quote lineage requirements
- deleted/stale evidence behavior
- prior model conclusion is not evidence rule
- cross-case/cross-owner prohibitions

Gate:

```text
corpus_reasoning_gate
corpus_scope_gate
corpus_staleness_gate
reasoning_graph_boundary_gate
```

---

## ABV-WP-009 — Boundary-aware text validation plan

Priority: P0

Target:

```text
backend/services/safety_validator.py
backend/services/module_output_validator.py
report/export validators
tests/
```

Purpose:

Formalize forbidden and cautionary language checks beyond existing regex foundations.

Required planning outcomes:

- diagnostic/labeling prohibition checks
- user-provided diagnosis validation checks
- hidden intent as fact checks
- therapeutic authority checks
- legal/medical/adjudication checks
- safety mutualization and reconciliation pressure checks
- corpus overreach checks
- report/export language checks

Gate:

```text
diagnosis_labeling_prohibition_gate
intent_as_fact_gate
therapeutic_authority_gate
report_language_gate
```

---

# P1 Work Packages

## ABV-WP-010 — Prompt boundary and repair flow plan

Priority: P1

Target:

```text
backend/services/prompt_compiler.py
backend/services/module_runner.py
config/framework/
config/prompts/
```

Purpose:

Ensure prompts and repair prompts receive explicit boundaries and do not weaken privacy or analysis gates.

Required planning outcomes:

- prompt inputs include analysis scope and safety posture
- repair prompts avoid unnecessary sensitive content reuse
- corpus prompts retrieve scoped evidence, not entire account content
- prompt hashes include boundary-relevant versions
- prompt logs remain content-free

Gate:

```text
prompt_boundary_gate
privacy_boundary_gate
log_redaction_gate
```

---

## ABV-WP-011 — ReportScope and report validation plan

Priority: P1

Target:

```text
backend/domain/synthesis.py
backend/schemas/module_output_v1.py
backend/services/report/export surfaces
frontend/report views
```

Purpose:

Make report scope, evidence basis, safety posture, hypothesis/corpus claims, and limitations explicit before report display/export.

Gate:

```text
report_scope_gate
hypothesis_boundary_gate
export_readiness_gate
```

---

## ABV-WP-012 — Reasoning graph boundary vocabulary plan

Priority: P1

Target:

```text
backend/domain/enums.py
backend/domain/finding.py
backend/services/graph_merge_service.py
backend/services/structured_graph_service.py
backend/repositories/relationship_repository.py
```

Purpose:

Define graph node and edge vocabulary that distinguishes evidence, observation, finding, hypothesis, alternative, limitation, safety posture, reflection point, and corpus pattern relationships.

Gate:

```text
reasoning_graph_boundary_gate
evidence_linkage_gate
confidence_calibration_gate
```

---

## ABV-WP-013 — Export readiness validation plan

Priority: P1

Target:

```text
future export services
report services
privacy/encryption/export artifact planning
```

Purpose:

Prevent exports from losing scope/version/evidence/safety/hypothesis limitations.

Gate:

```text
export_readiness_gate
export_boundary_gate
privacy_boundary_gate
```

---

## ABV-WP-014 — Analysis validation test and fixture plan

Priority: P1

Target:

```text
tests/
config/evaluation or fixtures
backend/services/evaluation_run_service.py
```

Purpose:

Define test fixtures that prove analysis boundaries are enforced across module, synthesis, corpus, report, and export outputs.

Gate:

```text
evaluation_gate
regression_gate
release_readiness_gate
```

---

## ABV-WP-015 — UI validation state handoff

Priority: P1

Target:

```text
backend/api/schemas.py
frontend/report views
003-G UI/report planning
```

Purpose:

Define safe user-facing display for validation warnings, blocked sections, evidence scope, hypothesis support level, safety posture, corpus scope, and report/export readiness.

Gate:

```text
ui_language_gate
report_scope_gate
privacy_boundary_gate
```

---

# P2 Work Packages

## ABV-WP-016 — Advanced lens/source-framework registry

Priority: P2

Target:

```text
config/modules/
config/framework/
future domain/reference data
```

Purpose:

Consider a richer registry for therapeutic, diagnostic-framework-informed, behavioral, cognitive, relational, and methodological source references.

Gate:

```text
reflection_lens_contract_gate
therapeutic_authority_gate
```

---

## ABV-WP-017 — Advanced corpus trend scoring

Priority: P2

Target:

```text
corpus/graph services
future evaluation fixtures
```

Purpose:

Plan careful scoring for recurrence, strengthening, weakening, contradiction, and temporal change after baseline corpus boundaries are safe.

Gate:

```text
corpus_reasoning_gate
confidence_calibration_gate
corpus_staleness_gate
```

---

## ABV-WP-018 — Future workspace corpus support

Priority: P2

Target:

```text
future enterprise/workspace policy layer
```

Purpose:

Defer cross-case/workspace corpus reasoning until future identity, access, retention, and enterprise policy layers exist.

Gate:

```text
corpus_scope_gate
privacy_boundary_gate
future_enterprise_policy_gate
```

---

# Dependency Order

Recommended order for later implementation:

```text
ABV-WP-001
ABV-WP-002
ABV-WP-003
ABV-WP-004
ABV-WP-005
ABV-WP-006
ABV-WP-007
ABV-WP-008
ABV-WP-009
ABV-WP-010 through ABV-WP-015
```

Do not expand corpus reasoning, exports, reports, or UI claims before ABV-WP-001 through ABV-WP-009 are planned and gated.

---

# Decision

These packages are ready to feed 003-F, 003-G, and the 003-H exit review.
