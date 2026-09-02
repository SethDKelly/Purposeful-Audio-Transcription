# 003-B Domain Terminology Migration Work Packages

## Status

Accepted as the Phase 003-B implementation-planning work package inventory.

---

# Purpose

Break domain terminology and concept mapping into later implementation-ready work packages.

These work packages are planning artifacts only.

They are not authorization to implement code or schema changes during 003-B.

---

# Work Package Legend

| Field | Meaning |
|---|---|
| ID | Stable Phase 003-B work package identifier |
| Priority | P0, P1, or P2 |
| Target | Main implementation area later affected |
| Gate | Acceptance gate that must pass before implementation is accepted |

---

# P0 Work Packages

## DTM-WP-001 — Domain authority and glossary lock

Priority: P0

Target:

```text
docs/domain or equivalent developer planning surface
```

Purpose:

Create a concise implementation-facing glossary that maps current code names to accepted concept names.

Required mappings:

- WorkflowRun -> ReflectionRun
- ModuleDefinition / ModuleRun -> ReflectionLens / LensExecution
- SynthesisReport -> ReflectionReport
- Intervention / Recommendation -> ReflectionPoint
- SafetyMode / safety flags -> SafetyPosture
- SourceType.AUDIO -> Recording source marker, not lifecycle boundary

Gate:

```text
documentation_authority_gate
terminology_drift_gate
```

---

## DTM-WP-002 — Transcript aggregate decision record

Priority: P0

Target:

```text
backend/domain/transcript.py
docs/design/03_domain_model.md
future domain ADR
```

Purpose:

Record the decision that `Transcript` remains the practical near-term aggregate root while `ConversationRecord` remains conceptual.

Gate:

```text
domain_mapping_gate
```

Acceptance notes:

- no separate `ConversationRecord` implementation required yet
- future source artifact/lifecycle complexity may reopen the decision
- transcript version and evidence basis must not be weakened

---

## DTM-WP-003 — TranscriptVersion and EvidenceQuote hardening plan

Priority: P0

Target:

```text
backend/domain/transcript.py
alembic/versions/*
analysis/report services
```

Purpose:

Plan how retained analysis will require stable transcript-version binding and evidence quote lineage.

Gate:

```text
analysis_boundary_gate
report_scope_gate
corpus_reasoning_gate
```

Acceptance notes:

- `EvidenceQuote.transcript_version_id` should not remain optional for retained analysis forever
- reports must identify source transcript versions
- corpus claims must trace to transcript versions and quote IDs

---

## DTM-WP-004 — ReflectionRun compatibility mapping

Priority: P0

Target:

```text
backend/domain/workflow.py
backend/api/*
report/export surfaces
```

Purpose:

Map `WorkflowRun` to product concept `ReflectionRun` without immediate destructive rename.

Gate:

```text
terminology_drift_gate
domain_mapping_gate
```

Acceptance notes:

- internal orchestration may remain `WorkflowRun`
- user-facing surfaces should not expose workflow terminology as product meaning by default
- migration must preserve existing run history

---

## DTM-WP-005 — ReflectionLens contract mapping

Priority: P0

Target:

```text
backend/domain/finding.py
module registry/configs
analysis services
```

Purpose:

Map `ModuleDefinition` and `ModuleRun` to Reflection Lens semantics and prepare `ReflectionLensContract` fields.

Gate:

```text
analysis_boundary_gate
hypothesis_boundary_gate
safety_override_gate
```

Acceptance notes:

- product-facing term is Reflection Lens
- source frameworks are reasoning references, not clinical authority
- lens contracts must declare forbidden claims and confidence ceilings

---

## DTM-WP-006 — Hypothesis separation plan

Priority: P0

Target:

```text
backend/domain/finding.py
backend/domain/synthesis.py
analysis output schemas
validators
```

Purpose:

Plan how `FindingType.HYPOTHESIS` transitions into bounded `PsychologicalHypothesis` and `HypothesisSupportAssessment` semantics.

Gate:

```text
hypothesis_boundary_gate
confidence_calibration_gate
analysis_boundary_gate
```

Acceptance notes:

- support level is not confidence
- user-provided diagnoses are context, not confirmation targets
- evidence against and alternative explanations must be first-class

---

## DTM-WP-007 — SafetyPosture migration plan

Priority: P0

Target:

```text
backend/domain/workflow.py
backend/domain/finding.py
backend/domain/synthesis.py
analysis validators
report rendering
```

Purpose:

Plan migration from boolean/list safety signals to structured safety posture.

Gate:

```text
safety_override_gate
safety_mutualization_gate
```

Acceptance notes:

- safety posture must affect output behavior
- elevated/high-risk posture suppresses unsafe reflection points
- safety must be evidence-linked and uncertainty-aware

---

## DTM-WP-008 — ReflectionPoint migration plan

Priority: P0

Target:

```text
backend/domain/enums.py
backend/domain/synthesis.py
report and UI surfaces
```

Purpose:

Replace recommendation/intervention terminology with `ReflectionPoint` semantics.

Gate:

```text
reflection_point_gate
ui_language_gate
report_scope_gate
```

Acceptance notes:

- reflection points are non-prescriptive
- no treatment or directive framing
- high-risk contexts may suppress reflection points

---

## DTM-WP-009 — Case Evidence Corpus mapping plan

Priority: P0

Target:

```text
backend/domain/case.py
transcript/case services
analysis scope services
reasoning graph
```

Purpose:

Plan explicit case-corpus scope for multi-transcript reasoning.

Gate:

```text
corpus_reasoning_gate
corpus_staleness_gate
privacy_boundary_gate
```

Acceptance notes:

- case is more than a folder
- corpus claims require included transcript versions and evidence quote lineage
- hidden account-wide inference remains blocked by default

---

# P1 Work Packages

## DTM-WP-010 — Reasoning graph edge vocabulary expansion

Priority: P1

Target:

```text
backend/domain/enums.py
graph services
ontology docs
```

Purpose:

Plan graph relationship vocabulary for recurrence, strengthening, weakening, contextualization, limitation, and safety override.

Gate:

```text
corpus_reasoning_gate
analysis_boundary_gate
```

---

## DTM-WP-011 — Confidence/support-level mapping

Priority: P1

Target:

```text
backend/domain/enums.py
analysis output schemas
validators
reports
```

Purpose:

Keep confidence values and hypothesis support levels distinct.

Gate:

```text
confidence_calibration_gate
hypothesis_boundary_gate
```

---

## DTM-WP-012 — ReflectionReport compatibility mapping

Priority: P1

Target:

```text
backend/domain/synthesis.py
report services
export services
frontend report views
```

Purpose:

Map `SynthesisReport` to product-facing `ReflectionReport` without breaking existing report generation.

Gate:

```text
report_scope_gate
export_boundary_gate
ui_language_gate
```

---

## DTM-WP-013 — API/DTO terminology audit

Priority: P1

Target:

```text
backend/api/*
frontend API clients
OpenAPI or API reference docs
```

Purpose:

Identify endpoints and DTO fields that expose legacy terminology to users or future agents.

Gate:

```text
terminology_drift_gate
regression_gate
```

---

# P2 Work Packages

## DTM-WP-014 — Physical code rename decision

Priority: P2

Target:

```text
backend/domain/*
alembic/versions/*
API and frontend references
```

Purpose:

Decide whether code-level names should eventually be physically renamed or permanently treated as internal implementation names with product-facing aliases.

Gate:

```text
release_readiness_gate
regression_gate
```

---

## DTM-WP-015 — Future enterprise naming reservation

Priority: P2

Target:

```text
future policy/access/domain planning
```

Purpose:

Reserve enterprise terms such as organization, workspace, role, sharing grant, and audit policy for later authorized enterprise planning.

Gate:

```text
documentation_authority_gate
privacy_boundary_gate
```

---

# Cross-Package Rules

1. Do not rename persisted schema fields without migration planning.
2. Do not expose legacy terms as user-facing product authority merely because code uses them internally.
3. Do not make report/UI copy changes before retention, privacy, analysis, and safety gates are attached.
4. Do not introduce corpus reasoning without explicit scope and evidence lineage.
5. Do not collapse hypothesis support into confidence.
6. Do not treat safety posture as optional report decoration.
7. Do not restore old workflow assumptions while domain terms are still unresolved.

---

# Decision

These work packages should feed 003-C through 003-G and the 003-H exit review.

They are not implementation authorization by themselves.
