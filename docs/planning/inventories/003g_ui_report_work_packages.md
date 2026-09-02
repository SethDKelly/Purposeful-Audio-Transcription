# 003-G UI/Report Alignment Work Packages

## Status

Accepted as the Phase 003-G UI/report alignment implementation-planning work package inventory.

These packages are not implementation authorization.

---

# Purpose

Break UI/report alignment work into later implementation-ready packages.

Each package must be gated before component, route, copy, report renderer, graph UI, export UI, deletion UI, settings, API DTO, test, or deployment changes are accepted.

---

# Work Package Legend

| Field | Meaning |
|---|---|
| ID | Stable Phase 003-G work package identifier |
| Priority | P0, P1, or P2 |
| Target | Main implementation area later affected |
| Gate | Acceptance gate that must pass before implementation is accepted |

---

# P0 Work Packages

## UIR-WP-001 — Product framing and navigation reconciliation

Priority: P0

Target:

```text
frontend-react/src/App.tsx
frontend-react/src/components/AppShell.tsx
frontend-react/src/pages/DashboardPage.tsx
README/docs entry points where UI language is referenced
```

Purpose:

Move ordinary user-facing navigation from implementation-first language toward reflection-first product language.

Required planning outcomes:

- ordinary personal-owner navigation model
- admin/developer surface separation model
- accepted product name and engine-name placement
- implementation terms that may remain in developer/admin mode
- terminology test expectations

Gate:

```text
product_framing_gate
navigation_authority_gate
UI_terminology_gate
admin_developer_surface_separation_gate
```

---

## UIR-WP-002 — Dashboard owner-orientation plan

Priority: P0

Target:

```text
frontend-react/src/pages/DashboardPage.tsx
frontend-react/src/api/client.ts
backend/api/schemas.py
future system status/report summary APIs
```

Purpose:

Make dashboard orient the owner to transcripts, cases, reports, retention, validation, active jobs, and Cost State.

Required planning outcomes:

- dashboard status sections
- data required from API
- draft expiration and retention cues
- active reflection run and validation attention cues
- active blocking job/cost-state cues
- privacy reminder behavior

Gate:

```text
product_framing_gate
retention_visibility_gate
cost_state_status_UI_gate
validation_state_display_gate
```

---

## UIR-WP-003 — Transcript lifecycle display plan

Priority: P0

Target:

```text
frontend-react/src/pages/IngestPage.tsx
frontend-react/src/pages/PreparePage.tsx
frontend-react/src/api/client.ts
backend/api/schemas.py
```

Purpose:

Show source type, draft/saved/case-retained state, draft expiration, audio deletion defaults, version basis, evidence readiness, and save/case promotion effects.

Required planning outcomes:

- transcript lifecycle badge vocabulary
- draft expiration UI
- save/retain explanation
- case assignment retention explanation
- audio deletion copy for audio intake
- version-binding display
- readiness-to-analysis copy

Gate:

```text
transcript_version_display_gate
retention_visibility_gate
privacy_settings_gate
```

---

## UIR-WP-004 — AnalysisScope setup UI plan

Priority: P0

Target:

```text
frontend-react/src/pages/AnalyzePage.tsx
frontend-react/src/api/client.ts
backend/api/schemas.py
future analysis routes
```

Purpose:

Replace workflow-only analysis setup with visible evidence scope and reflection lens setup.

Required planning outcomes:

- scope selector: single transcript version, selected transcript set, case evidence corpus
- included/excluded transcript version display
- case/corpus selector behavior
- reflection lens selector language
- user-provided context/hypothesis handling
- non-diagnostic boundary copy
- safety posture preview

Gate:

```text
analysis_scope_display_gate
transcript_version_display_gate
corpus_scope_display_gate
safety_posture_display_gate
```

---

## UIR-WP-005 — ReportScope header and validation status plan

Priority: P0

Target:

```text
frontend-react/src/pages/ReportPage.tsx
frontend-react/src/api/client.ts
backend/api/schemas.py
backend/domain/synthesis.py
```

Purpose:

Ensure every report visibly declares scope, evidence basis, safety posture, validation state, stale status, and export readiness.

Required planning outcomes:

- ReportScope header fields
- validation status panel
- stale evidence/report warning behavior
- lens list display
- safety posture summary
- limitations/boundary reminder
- export readiness state

Gate:

```text
report_scope_gate
validation_state_display_gate
transcript_version_display_gate
export_readiness_UI_gate
```

---

## UIR-WP-006 — Findings, hypotheses, and support display split

Priority: P0

Target:

```text
frontend-react/src/components/FindingCard.tsx
frontend-react/src/pages/ReportPage.tsx
frontend-react/src/api/client.ts
backend/api/schemas.py
```

Purpose:

Separate evidence-backed findings from psychological hypotheses and support assessments.

Required planning outcomes:

- finding display requirements
- hypothesis support display requirements
- support-level labels
- evidence-for/evidence-against/missing evidence display
- alternatives and limitations layout
- confidence/support distinction
- forbidden diagnosis/identity phrasing checks

Gate:

```text
hypothesis_display_gate
support_level_language_gate
evidence_display_gate
UI_terminology_gate
```

---

## UIR-WP-007 — ReflectionPoint migration UI plan

Priority: P0

Target:

```text
frontend-react/src/pages/ReportPage.tsx
frontend-react/src/components/FindingCard.tsx
frontend-react/src/api/client.ts
backend/api/schemas.py
legacy recommendations/interventions surfaces
```

Purpose:

Replace product-facing recommendation/intervention language with evidence-linked reflection points.

Required planning outcomes:

- ReflectionPoint card/section requirements
- compatibility mapping from legacy `interventions` and recommendations
- evidence/source linkage display
- non-prescriptive copy rules
- safety-posture suppression/modification behavior
- export behavior

Gate:

```text
reflection_point_language_gate
safety_override_UI_gate
report_scope_gate
```

---

## UIR-WP-008 — SafetyPosture display plan

Priority: P0

Target:

```text
frontend-react/src/pages/AnalyzePage.tsx
frontend-react/src/pages/ReportPage.tsx
frontend-react/src/api/client.ts
backend/api/schemas.py
future SafetyPosture DTO
```

Purpose:

Move from risk strings and boolean safety mode toward structured safety posture display and behavior.

Required planning outcomes:

- SafetyPosture user-facing labels
- evidence-linked trigger display
- report section ordering
- action suppression rules
- high-risk warning language
- crisis-support boundary language
- export readiness interaction

Gate:

```text
safety_posture_display_gate
safety_override_UI_gate
hypothesis_display_gate
reflection_point_language_gate
```

---

## UIR-WP-009 — Case Evidence Corpus UI plan

Priority: P0

Target:

```text
frontend-react/src/pages/CasesPage.tsx
frontend-react/src/api/client.ts
backend/api/schemas.py
case/corpus APIs
```

Purpose:

Make cases visible as privacy-significant retained longitudinal evidence boundaries.

Required planning outcomes:

- Case Evidence Corpus label and explanation
- included transcript version display
- recurrence/contradiction/weakening/temporal change summaries
- corpus evidence count and time span
- excluded/stale/deleted evidence display
- add-to-case retention warning
- remove-from-case vs delete-transcript distinction

Gate:

```text
case_evidence_corpus_gate
corpus_scope_display_gate
retention_visibility_gate
privacy_settings_gate
```

---

## UIR-WP-010 — Export readiness and export-boundary UI plan

Priority: P0

Target:

```text
frontend-react/src/pages/ReportPage.tsx
frontend-react/src/api/client.ts
backend/api/schemas.py
future export services
```

Purpose:

Make exports deliberate portable artifacts that preserve scope, evidence/version basis, limitations, redaction, validation status, and retention boundary.

Required planning outcomes:

- export preview modal/screen requirements
- redaction preference and override behavior
- scope/version/evidence appendix display
- safety/hypothesis/corpus limitations
- server-retention behavior
- downloaded-copy boundary
- blocked/warned export states

Gate:

```text
export_readiness_UI_gate
privacy_settings_gate
report_scope_gate
```

---

## UIR-WP-011 — Deletion cascade and remove-from-case UI plan

Priority: P0

Target:

```text
frontend-react/src/pages/PreparePage.tsx
frontend-react/src/pages/CasesPage.tsx
frontend-react/src/pages/ReportPage.tsx
frontend-react/src/api/client.ts
backend/api/schemas.py
```

Purpose:

Show destructive and non-destructive retention actions clearly before data or derived artifacts are removed, invalidated, or stale-marked.

Required planning outcomes:

- delete transcript cascade preview
- delete report behavior
- delete export artifact behavior
- remove transcript from case behavior
- delete case wrapper vs contained transcripts decision display
- graph/corpus stale-marking explanation
- confirmation and undo/recovery posture if any

Gate:

```text
deletion_cascade_UI_gate
retention_visibility_gate
privacy_settings_gate
```

---

# P1 Work Packages

## UIR-WP-012 — Boundary-aware graph/evidence UI plan

Priority: P1

Target:

```text
frontend-react/src/pages/GraphPage.tsx
frontend-react/src/components/EvidencePanel.tsx
frontend-react/src/api/client.ts
backend/api/schemas.py
```

Purpose:

Preserve graph exploration while making support, contradiction, alternative, limitation, hypothesis, safety, corpus, and stale evidence boundaries visible.

Gate:

```text
graph_boundary_display_gate
evidence_display_gate
corpus_scope_display_gate
```

---

## UIR-WP-013 — System Status / Cost State UI plan

Priority: P1

Target:

```text
frontend-react/src/pages/LoginPage.tsx
frontend-react/src/components/AppShell.tsx
future SystemStatusPage
frontend-react/src/api/client.ts
backend/api/routes/power.py
```

Purpose:

Show accepted Cost State status and controls without making sleep/wake behavior look like a product failure.

Gate:

```text
cost_state_status_UI_gate
UI_terminology_gate
privacy_settings_gate
```

---

## UIR-WP-014 — Settings privacy/retention product surface plan

Priority: P1

Target:

```text
frontend-react/src/pages/SettingsPage.tsx
frontend-react/src/prefs/localPrefs.ts
backend/api/schemas.py
future retention/cost-state settings APIs
```

Purpose:

Move settings from browser reminders and developer-doc references toward product-level retention, privacy, export, case/corpus, and cost-state preference display.

Gate:

```text
privacy_settings_gate
retention_visibility_gate
cost_state_status_UI_gate
```

---

## UIR-WP-015 — Admin/developer mode separation plan

Priority: P1

Target:

```text
frontend-react/src/components/AppShell.tsx
frontend-react/src/pages/ModulesPage.tsx
frontend-react/src/pages/EvaluationsPage.tsx
frontend-react/src/pages/GraphPage.tsx
frontend-react/src/pages/CasesPage.tsx
```

Purpose:

Keep module lifecycle, evaluations, debug JSON, lifecycle hashes, and raw structured inventories available when useful without making them ordinary user-facing product authority.

Gate:

```text
admin_developer_surface_separation_gate
product_framing_gate
privacy_settings_gate
```

---

## UIR-WP-016 — UI/API DTO alignment plan

Priority: P1

Target:

```text
frontend-react/src/api/client.ts
backend/api/schemas.py
report/case/corpus/export/power endpoints
```

Purpose:

Align frontend types and backend response schemas with AnalysisScope, ReportScope, ValidationStatus, SafetyPosture, ReflectionPoint, CorpusPatternAssessment, ExportValidationResult, and CostStateRecord.

Gate:

```text
report_scope_gate
validation_state_display_gate
cost_state_status_UI_gate
regression_gate
```

---

## UIR-WP-017 — UI/report acceptance test plan

Priority: P1

Target:

```text
frontend-react/src/**/*.test.tsx
backend API contract tests
future visual/regression checks
```

Purpose:

Define tests that enforce UI/report terminology, evidence scope, hypotheses, safety, corpus, deletion/export, privacy, and cost-state boundaries.

Gate:

```text
evaluation_regression_gate
release_readiness_gate
```

---

## UIR-WP-018 — Accessibility and destructive-action usability plan

Priority: P1

Target:

```text
frontend-react/src/pages/*
frontend-react/src/components/*
```

Purpose:

Ensure warnings, validation failures, safety posture, stale evidence, destructive actions, and cost-state transitions are accessible and understandable.

Gate:

```text
accessibility_usability_gate
deletion_cascade_UI_gate
safety_posture_display_gate
```

---

# P2 Work Packages

## UIR-WP-019 — Advanced corpus visualization plan

Priority: P2

Target:

```text
future corpus/graph/timeline UI
```

Purpose:

Plan richer longitudinal timelines, recurrence charts, contradiction views, evidence density, and change-over-time summaries after core corpus boundaries are safe.

Gate:

```text
corpus_scope_display_gate
graph_boundary_display_gate
future_enterprise_policy_gate if workspace scoped
```

---

## UIR-WP-020 — Future workspace/enterprise navigation plan

Priority: P2

Target:

```text
future enterprise/workspace UI
```

Purpose:

Defer organizations, workspaces, SSO, role delegation, audit/compliance, billing, and clinician/client hierarchy until future enterprise policy layers are authorized.

Gate:

```text
future_enterprise_policy_gate
privacy_boundary_gate
release_readiness_gate
```

---

## UIR-WP-021 — Visual design system polish

Priority: P2

Target:

```text
frontend-react/src/index.css
future design tokens/components
```

Purpose:

Defer visual polish until semantic/report/safety/privacy/corpus/cost-state alignment is safe.

Gate:

```text
accessibility_usability_gate
product_framing_gate
```

---

# Dependency Order

Recommended order for later implementation:

```text
UIR-WP-001
UIR-WP-002
UIR-WP-003
UIR-WP-004
UIR-WP-005
UIR-WP-006
UIR-WP-007
UIR-WP-008
UIR-WP-009
UIR-WP-010
UIR-WP-011
UIR-WP-012 through UIR-WP-018
```

Do not expand report persuasion, exports, case/corpus views, or graph visualizations before ReportScope, AnalysisScope, SafetyPosture, evidence display, and validation-state gates are planned and accepted.

---

# Decision

These packages are ready to feed 003-H exit review and a later authorized implementation phase.
