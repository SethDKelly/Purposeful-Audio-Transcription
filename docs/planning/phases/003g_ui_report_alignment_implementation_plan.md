# 003-G — UI/Report Alignment Implementation Plan

## Status

Complete.

This subgroup converts accepted UI/UX concept alignment into implementation-ready UI/report plans.

It does not implement React components, route changes, API schema changes, report renderer changes, graph UI changes, export behavior changes, deletion behavior changes, retention behavior changes, cost-state controls, styling/design-system changes, accessibility fixes, tests, deployment changes, or production data migrations.

---

# Purpose

003-G prepares UI/report work so later implementation can preserve product boundaries across user-facing surfaces.

It answers:

- Which UI/report foundations already exist in the prototype?
- How should product framing move from transcription/module/workflow language toward evidence-linked reflection language?
- How should transcript lifecycle, retention, version, and case/corpus state be surfaced?
- How should analysis setup display scope, selected transcript versions, reflection lenses, and safety boundaries?
- How should reports display scope, evidence basis, validation status, hypotheses, safety posture, reflection points, and export readiness?
- How should case/corpus and graph views preserve lineage, recurrence, contradiction, stale evidence, and boundaries?
- How should deletion/export/cost-state/settings surfaces communicate user control without overpromising?

---

# Outputs

| Output | Document |
|---|---|
| UI/report alignment implementation plan | `../architecture/003g_ui_report_alignment_implementation_plan.md` |
| UI/report surface matrix | `../inventories/003g_ui_report_surface_matrix.md` |
| UI/report work packages | `../inventories/003g_ui_report_work_packages.md` |
| UI/report gate checklist | `../inventories/003g_ui_report_gate_checklist.md` |

---

# Implementation Reference Reviewed

003-G reviewed the accepted Phase 002 UI/UX architecture, prior Phase 003 foundation plans, and current implementation references including:

```text
docs/planning/architecture/002g_ui_ux_concept_alignment_plan.md
docs/planning/inventories/002g_ui_ux_language_matrix.md
docs/planning/inventories/002g_user_flow_alignment_inventory.md
docs/planning/architecture/003b_domain_terminology_concept_mapping_implementation_plan.md
docs/planning/architecture/003c_data_lifecycle_retention_foundation_implementation_plan.md
docs/planning/architecture/003d_privacy_boundary_encryption_baseline_implementation_plan.md
docs/planning/architecture/003e_analysis_boundary_validation_implementation_plan.md
docs/planning/architecture/003f_cost_state_control_plane_implementation_plan.md
frontend-react/src/App.tsx
frontend-react/src/components/AppShell.tsx
frontend-react/src/pages/DashboardPage.tsx
frontend-react/src/pages/IngestPage.tsx
frontend-react/src/pages/PreparePage.tsx
frontend-react/src/pages/AnalyzePage.tsx
frontend-react/src/pages/ReportPage.tsx
frontend-react/src/pages/GraphPage.tsx
frontend-react/src/pages/CasesPage.tsx
frontend-react/src/pages/LoginPage.tsx
frontend-react/src/pages/SettingsPage.tsx
frontend-react/src/pages/ModulesPage.tsx
frontend-react/src/components/FindingCard.tsx
frontend-react/src/components/EvidencePanel.tsx
frontend-react/src/api/client.ts
backend/api/schemas.py
backend/domain/synthesis.py
backend/api/routes/power.py
```

---

# Current Baseline Findings

The prototype already has useful UI/report foundations:

- React routes for dashboard, ingest, prepare, analysis, report, graph, cases, modules, evaluations, settings, and login
- app shell with authentication state, handoff token handling, and route navigation
- dashboard links for ingest, cases, saved reports, modules, and health
- transcript preparation with speaker/turn editing, exclusions, evidence rebuild, readiness marking, dirty-state warning, and quality warnings
- analysis screen with workflow selection, safety scan, safety-aware mode, run status, attempt count, and error display
- report screen with transcript version display, stale warning, safety mode/flags, finding filters, evidence panel, graph link, saved report state, and export package action
- finding cards with confidence, type, source run, evidence IDs, alternatives, limitations, feedback, and review state
- evidence panel with concise quote display and optional surrounding context
- graph explorer with confidence filters, node/edge selection, evidence quote IDs, rationale, and alternatives
- case screen with transcript assignment, timeline, compare, longitudinal synthesis, and pinned findings
- login wake/status flow with handoff
- settings page with account, privacy reminders, and export redaction preference

The prototype is not yet sufficient for the accepted UI/report model because product-facing surfaces still expose implementation language prominently, analysis scope is not explicit enough, case/corpus semantics are not visible enough, report scope/validation/export readiness are incomplete, hypotheses and reflection points need separate display semantics, safety posture is not structured, deletion/export flows lack cascade/boundary previews, and cost-state UI is not yet a first-class product status surface.

---

# Accepted Decisions

## 1. UI/report work is concept implementation

UI and report surfaces can preserve or break the product boundary. They must be reviewed as concept implementation, not cosmetic presentation only.

## 2. Navigation should become reflection-oriented

Ordinary user navigation should emphasize transcripts, cases, reports, evidence/graph, exports, settings, and system status. Modules, workflows, evaluations, raw JSON, and lifecycle hashes should be admin/developer surfaces unless intentionally exposed.

## 3. Transcript lifecycle must be visible

Draft, saved, versioned, case-retained, stale, deleted, export, and cost-state-related statuses should be understandable from user-facing flows.

## 4. Analysis setup must show scope before execution

Workflow selection is not enough. The user should understand whether the run uses a single transcript version, selected transcript set, or case evidence corpus.

## 5. Reports need a ReportScope header and validation status

Reports should display scope type, transcript version basis, selected lenses, case/corpus scope, validation state, safety posture, limitations, stale evidence status, and export readiness.

## 6. Findings, hypotheses, and reflection points need distinct UI semantics

Ordinary findings, psychological hypotheses/support assessments, and reflection points should not be collapsed into one generic card or intervention list.

## 7. Case/corpus UI must show longitudinal evidence boundaries

Cases should be presented as retained Case Evidence Corpus boundaries, not only folders or timelines.

## 8. Graph UI must remain boundary-aware

Graph nodes and edges should distinguish evidence, findings, hypotheses, reflection points, safety, limitations, alternatives, corpus recurrence, contradiction, and stale evidence.

## 9. Export and deletion flows require explicit preview/boundary behavior

Export should preview scope/version/evidence/limitations/redaction/retention. Deletion should preview cascade effects and distinguish remove-from-case from delete-source.

## 10. Cost State should be visible without implying product failure

Sleep/wake/active/idle-pending/shutting-down/failed/maintenance states should be explained as availability/cost posture, not data loss or analysis invalidity.

---

# Work Package Summary

003-G defines work packages for:

```text
UIR-WP-001 — Product framing and navigation reconciliation
UIR-WP-002 — Dashboard owner-orientation plan
UIR-WP-003 — Transcript lifecycle display plan
UIR-WP-004 — AnalysisScope setup UI plan
UIR-WP-005 — ReportScope header and validation status plan
UIR-WP-006 — Findings, hypotheses, and support display split
UIR-WP-007 — ReflectionPoint migration UI plan
UIR-WP-008 — SafetyPosture display plan
UIR-WP-009 — Case Evidence Corpus UI plan
UIR-WP-010 — Export readiness and export-boundary UI plan
UIR-WP-011 — Deletion cascade and remove-from-case UI plan
UIR-WP-012 — Boundary-aware graph/evidence UI plan
UIR-WP-013 — System Status / Cost State UI plan
UIR-WP-014 — Settings privacy/retention product surface plan
UIR-WP-015 — Admin/developer mode separation plan
UIR-WP-016 — UI/API DTO alignment plan
UIR-WP-017 — UI/report acceptance test plan
UIR-WP-018 — Accessibility and destructive-action usability plan
```

P2 decisions remain for advanced corpus visualization, future workspace/enterprise navigation, and visual design system polish.

---

# Gates Carried Forward

003-G carries forward these gates:

- product framing gate
- navigation authority gate
- UI terminology gate
- report scope gate
- analysis scope display gate
- transcript version display gate
- evidence display gate
- hypothesis display gate
- support-level language gate
- reflection point language gate
- safety posture display gate
- safety override UI gate
- corpus scope display gate
- case evidence corpus gate
- graph boundary display gate
- validation state display gate
- export readiness UI gate
- deletion cascade UI gate
- retention visibility gate
- privacy/settings gate
- cost-state status UI gate
- admin/developer surface separation gate
- accessibility/usability gate
- evaluation/regression gate
- release readiness gate

---

# Handoff to 003-H

003-H should consolidate all Phase 003 outputs and determine whether a next implementation phase is authorized, modified, or blocked.

For UI/report work, 003-H should verify that later implementation is sequenced after domain, lifecycle, privacy, analysis/validation, and cost-state foundations, and that reports/exports/corpus views do not expand before their gates exist.

---

# Non-goals

003-G does not implement:

- React components
- route changes
- API schema changes
- report renderer changes
- graph UI changes
- export behavior changes
- deletion behavior changes
- retention behavior changes
- cost-state controls
- styling/design-system changes
- accessibility fixes
- tests
- deployment changes
- production data migration

---

# Exit Criteria

003-G is complete when:

- UI/report alignment implementation plan exists
- UI/report surface matrix exists
- UI/report work packages exist
- UI/report gate checklist exists
- current implementation references are reviewed at planning level
- 003-H handoff is explicit
- Phase 003 indexes are updated
- broad implementation remains blocked

All criteria are satisfied.

---

# Next Phase

Proceed to:

```text
003-H — Phase 003 Exit Review and Consolidation
```
