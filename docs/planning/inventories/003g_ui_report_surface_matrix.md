# 003-G UI/Report Surface Matrix

## Status

Accepted as the Phase 003-G UI/report surface implementation matrix.

---

# Purpose

Map accepted UI/report concepts to current implementation surfaces, remaining risks, target implementation posture, and gates.

This matrix is implementation planning only.

---

# Matrix Legend

| Status | Meaning |
|---|---|
| `existing_foundation` | Useful implementation exists and should be preserved |
| `existing_but_incomplete` | Useful implementation exists but lacks accepted UI/report semantics |
| `new_or_equivalent` | Needs a new component, route, copy surface, schema field, or service contract |
| `admin_or_dev_surface` | Useful for admin/developer workflows but should not dominate product UX |
| `policy_only_initially` | May begin as documented/copy policy before schema/code |
| `defer` | Valid but not needed for current implementation foundation |

---

# Surface Matrix

| Surface / Concept | Current Implementation Surface | Status | Required Implementation Target | Primary Gates |
|---|---|---|---|---|
| Product framing | README/concept docs; app shell `RRE`; dashboard product shell copy | existing_but_incomplete | reflection-first product identity with RRE as internal engine label | product_framing_gate, UI_terminology_gate |
| Navigation | `App.tsx`, `AppShell.tsx` routes: Dashboard, Ingest, Cases, Modules, Evals, Settings | existing_but_incomplete | user-facing Transcripts, Cases, Reports, Evidence/Graph, Exports, Settings, System Status; admin/developer surfaces separated | navigation_authority_gate, admin_developer_surface_separation_gate |
| Dashboard | `DashboardPage.tsx` | existing_but_incomplete | owner orientation showing cost state, transcripts, cases, drafts, reports, runs, validation warnings, blocking jobs, retention cues | product_framing_gate, cost_state_status_UI_gate |
| Ingest | `IngestPage.tsx` paste transcript creation | existing_foundation | intake status for paste/file/import/audio, source type, draft status, audio deletion default, draft expiration, save/case prompts | retention_visibility_gate, privacy_settings_gate |
| Transcript prepare | `PreparePage.tsx` speaker/turn edit, exclusion, rebuild evidence, mark ready | existing_foundation | version-binding explanation, draft/saved/case-retained state, lifecycle warnings, evidence-basis clarity | transcript_version_display_gate, retention_visibility_gate |
| Analysis setup | `AnalyzePage.tsx` workflow selection and safety-aware mode | existing_but_incomplete | explicit AnalysisScope UI, included versions, selected case/corpus, selected Reflection Lenses, user context/hypotheses, boundary language | analysis_scope_display_gate, safety_posture_display_gate |
| Reflection lens/module UI | `ModulesPage.tsx`, module lifecycle API | existing_but_incomplete | product-safe Reflection Lens presentation; module lifecycle remains admin/dev detail | UI_terminology_gate, admin_developer_surface_separation_gate |
| Run progress | `AnalyzePage.tsx` run ID/status/attempt/error; polling | existing_foundation | reflection-run progress, validation state, blocking-job/cost-state relation, safe cancellation semantics when implemented | validation_state_display_gate, cost_state_status_UI_gate |
| Report header | `ReportPage.tsx` run ID, transcript version, stale warning, safety mode | existing_foundation | ReportScope header with scope type, version basis, case/corpus, lenses, validation status, safety posture, stale evidence, export readiness | report_scope_gate, transcript_version_display_gate |
| Report findings | `FindingCard.tsx`, report filters | existing_foundation | distinct finding display with evidence, confidence, alternatives, limitations, validation state | evidence_display_gate, validation_state_display_gate |
| Hypotheses | `exploratory_hypotheses` rendered as ordinary findings | existing_but_incomplete | structured hypothesis/support display with source, support level, evidence for/against/missing, alternatives, limitations, boundary | hypothesis_display_gate, support_level_language_gate |
| Recommendations/interventions | `report.interventions`; schema `interventions`; `FindingType.INTERVENTION` | existing_but_incomplete | ReflectionPoint display and compatibility mapping from legacy recommendations/interventions | reflection_point_language_gate, safety_override_UI_gate |
| Safety display | `risk_level`, matched categories, `safety_mode`, `safety_flags` | existing_but_incomplete | structured SafetyPosture banner/panel and layout/action changes by posture | safety_posture_display_gate, safety_override_UI_gate |
| Evidence display | `EvidencePanel.tsx` with concise text/context and quote IDs | existing_foundation | preserve concise evidence; add source version/scope, stale/deleted status, claim linkage, quote precision warnings | evidence_display_gate, graph_boundary_display_gate |
| Graph explorer | `GraphPage.tsx` nodes/edges/confidence filters/evidence IDs/rationale/alternatives | existing_foundation | boundary-aware graph labels for finding/hypothesis/reflection/safety/corpus/stale relationships | graph_boundary_display_gate, corpus_scope_display_gate |
| Case UI | `CasesPage.tsx` create case, notes, transcript assignment, compare, longitudinal synthesis | existing_foundation | case as Case Evidence Corpus; retention/corpus explanation; included versions; recurrence/contradiction/change/staleness display | case_evidence_corpus_gate, corpus_scope_display_gate |
| Longitudinal synthesis display | JSON preview in `CasesPage.tsx` | existing_but_incomplete | product-safe case/corpus report view instead of raw parsed JSON for normal users | report_scope_gate, corpus_scope_display_gate |
| Export action | `ReportPage.tsx` export package ZIP; client API `/api/v1/exports` | existing_foundation | export preview/readiness flow with scope, versions, redaction, limitations, retention, downloaded-copy boundary | export_readiness_UI_gate, privacy_settings_gate |
| Deletion/remove flows | case delete API client; no complete UI cascade preview | existing_but_incomplete | cascade preview for transcript/report/export/case/remove-from-case actions | deletion_cascade_UI_gate, retention_visibility_gate |
| Settings/privacy | `SettingsPage.tsx` privacy banner, redacted export preference, auth status | existing_foundation | product-level retention/privacy settings, draft expiry, case/corpus retention, content-free logs, cost-state prefs | privacy_settings_gate, retention_visibility_gate |
| Login/wake | `LoginPage.tsx` environment state, waking step, handoff | existing_foundation | accepted Cost State vocabulary, failed wake/retry/maintenance status, clear cost-saving sleep language | cost_state_status_UI_gate, UI_terminology_gate |
| System status | no separate page; login and API health only | new_or_equivalent | System Status page/panel for Cost State, active jobs, idle, wake/sleep/keep-awake, failed wake, maintenance | cost_state_status_UI_gate |
| API client types | `frontend-react/src/api/client.ts` | existing_foundation | extend with AnalysisScope, ReportScope, SafetyPosture, ValidationResult, ReflectionPoint, CorpusPattern, ExportValidation DTOs | report_scope_gate, validation_state_display_gate |
| Backend response schemas | `backend/api/schemas.py` | existing_foundation | provide UI-ready scope/version/safety/validation/export/corpus fields without leaking raw internals | report_scope_gate, privacy_settings_gate |
| Report domain | `backend/domain/synthesis.py` | existing_but_incomplete | ReflectionReport/ReportScope semantics and reflection-point/hypothesis-support fields | report_scope_gate, hypothesis_display_gate |
| Admin/evaluations | `EvaluationsPage.tsx`, module lifecycle, debug package/graph views | admin_or_dev_surface | preserve for owner/admin but separate from ordinary reflective product path | admin_developer_surface_separation_gate |
| Accessibility/usability | basic semantic elements and forms | existing_but_incomplete | keyboard/screen-reader, warning prominence, destructive confirmation, evidence expansion, status announcements | accessibility_usability_gate |
| UI tests | `IngestPage.test.tsx` only visible in page tree | existing_but_incomplete | test coverage for terminology, report boundaries, safety, corpus, export, deletion, and cost state | evaluation_regression_gate |

---

# Current Strengths to Preserve

- route coverage for major product areas
- transcript preparation with speaker and turn controls
- explicit evidence panel with quote IDs and concise quote display
- report stale-version warning
- safety-aware mode and safety flag display
- graph explorer with evidence quote IDs and alternative explanations
- case timeline, pinned findings, compare, and longitudinal synthesis hooks
- login wake/handoff flow and environment status display
- settings privacy reminder and export redaction preference
- local saved-report and review-state preferences
- feedback labels that identify unsupported, too speculative, too clinical, and unsafe framing

---

# Priority Gaps

## P0 gaps

- ReportScope header is incomplete
- AnalysisScope is not visible before execution
- case/corpus scope is not explicit enough
- hypothesis support display is not first-class
- ReflectionPoint language has not replaced recommendations/interventions
- SafetyPosture is not structured in UI
- export readiness and deletion cascade previews are incomplete
- UI terminology still exposes implementation language too prominently

## P1 gaps

- dashboard lacks cost state, blocking jobs, draft retention, and validation attention cues
- modules/evaluations/debug surfaces need admin/developer separation
- graph UI needs boundary-aware edge/node semantics
- settings should expose product retention/privacy controls rather than developer-doc references
- System Status should become a dedicated UI surface or persistent panel
- UI acceptance tests need boundary cases

## P2 gaps

- advanced corpus visualization
- advanced evidence heatmaps/timelines
- future workspace/org navigation
- enterprise SSO/admin/billing/compliance surfaces
- polished visual design system beyond semantic alignment

---

# Target Component / Contract Set

Later implementation should consider this minimum target set:

```text
ProductShellNavigation
OwnerDashboardSummary
TranscriptLifecycleBadge
EvidenceScopeSelector
AnalysisScopePanel
ReflectionLensSelector
ReportScopeHeader
ValidationStatusPanel
SafetyPostureBanner
FindingCard
HypothesisSupportCard
ReflectionPointCard
EvidenceQuotePanel
CaseEvidenceCorpusPanel
CorpusPatternPanel
BoundaryAwareGraphLegend
ExportReadinessPanel
DeletionCascadePreview
SystemStatusPanel
PrivacyRetentionSettings
AdminDeveloperModeBoundary
```

Equivalent means a clearly documented UI component, route, DTO, or report section may be acceptable before a fully reusable component exists, as long as gates pass.

---

# Decision

This matrix is ready to feed the 003-G work packages and the 003-H exit review.
