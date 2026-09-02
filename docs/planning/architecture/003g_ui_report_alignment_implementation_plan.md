# 003-G UI/Report Alignment Implementation Plan

## Status

Accepted as the Phase 003-G UI/report alignment implementation plan.

This document converts the accepted Phase 002 UI/UX concept alignment architecture into implementation-ready work packages and gates.

It does not implement React components, routes, copy changes, report renderer changes, API schema changes, graph UI changes, export behavior, settings changes, cost-state controls, tests, deployment changes, or production data migrations by itself.

---

# Purpose

Prepare UI and report implementation work so later changes preserve the accepted product boundary:

```text
a secure, evidence-linked conversation analysis and reflection system
```

003-G turns the accepted UI/UX architecture into staged implementation planning for:

- product-facing terminology
- navigation and information architecture
- transcript intake and preparation flows
- save/retain/case-assignment visibility
- explicit analysis scope selection
- reflection lens language
- report scope and evidence-basis display
- bounded hypothesis display
- safety posture display
- reflection point migration
- case evidence corpus and longitudinal reasoning UI
- graph/evidence lineage display
- validation warning/failure display
- export-readiness and export-boundary display
- retention/deletion cascade visibility
- cost-state status and controls
- settings/privacy surfaces
- UI/report tests and acceptance gates

---

# Governing Inputs

Primary authority:

- `docs/planning/architecture/002g_ui_ux_concept_alignment_plan.md`
- `docs/planning/inventories/002g_ui_ux_language_matrix.md`
- `docs/planning/inventories/002g_user_flow_alignment_inventory.md`
- `docs/planning/architecture/003b_domain_terminology_concept_mapping_implementation_plan.md`
- `docs/planning/architecture/003c_data_lifecycle_retention_foundation_implementation_plan.md`
- `docs/planning/architecture/003d_privacy_boundary_encryption_baseline_implementation_plan.md`
- `docs/planning/architecture/003e_analysis_boundary_validation_implementation_plan.md`
- `docs/planning/architecture/003f_cost_state_control_plane_implementation_plan.md`

Implementation reference inspected:

- `frontend-react/src/App.tsx`
- `frontend-react/src/components/AppShell.tsx`
- `frontend-react/src/pages/DashboardPage.tsx`
- `frontend-react/src/pages/IngestPage.tsx`
- `frontend-react/src/pages/PreparePage.tsx`
- `frontend-react/src/pages/AnalyzePage.tsx`
- `frontend-react/src/pages/ReportPage.tsx`
- `frontend-react/src/pages/GraphPage.tsx`
- `frontend-react/src/pages/CasesPage.tsx`
- `frontend-react/src/pages/LoginPage.tsx`
- `frontend-react/src/pages/SettingsPage.tsx`
- `frontend-react/src/pages/ModulesPage.tsx`
- `frontend-react/src/components/FindingCard.tsx`
- `frontend-react/src/components/EvidencePanel.tsx`
- `frontend-react/src/api/client.ts`
- `backend/api/schemas.py`
- `backend/domain/synthesis.py`
- `backend/api/routes/power.py`

---

# Accepted UI/Report Principle

```text
The UI is an authority surface: it must make scope, evidence, uncertainty, retention, safety posture, validation state, export boundaries, corpus use, and cost state understandable without turning the product into diagnosis, therapy, surveillance, or raw transcription tooling.
```

UI and report work is not cosmetic only.

Poor labels, missing scope, hidden corpus use, or unsafe report sections can create product-boundary failures even when backend analysis is cautious.

---

# Current Implementation Baseline

The prototype already has useful UI/report foundations:

1. React routes exist for dashboard, ingest, transcript preparation, analysis, reports, graph exploration, cases, modules, evaluations, settings, and login.
2. The app shell handles sign-in state, power handoff query tokens, login redirects, and authenticated navigation.
3. Dashboard orients the owner to ingest, cases, saved reports, module lifecycle, and API health.
4. Ingest flow supports pasted transcript creation and routes to transcript preparation.
5. Prepare flow supports speaker review, turn edits, exclusions, evidence rebuild, readiness marking, dirty-state warning, quality warnings, and transition to analysis.
6. Analyze flow shows transcript ID, workflow selection, safety scan, safety-aware mode, workflow status, attempts, errors, and report navigation.
7. Report flow shows run ID, transcript version number, stale-version warning, safety-aware mode, safety flags, confidence/type/module filters, finding cards, evidence panel, graph link, saved report preference, and export package action.
8. Finding cards show confidence, type, source module run, evidence quote IDs, alternatives, limitations, review state, and feedback labels including speculative/clinical/unsafe framing labels.
9. Evidence panel shows quote ID, speaker, evidence type, concise quote text, optional context, and a list of available quotes.
10. Graph explorer shows graph nodes, edges, confidence filters, node/edge evidence quote IDs, rationale, and alternative explanations.
11. Cases flow supports case creation, notes, timeline, transcript assignment, transcript listing, compare transcripts, longitudinal synthesis, and pinned findings.
12. Login flow already displays environment/power state and a waking step for the application.
13. Settings flow includes account identity, privacy reminder preferences, export redaction preference, and notes about retention/deletion following API/ops policy.
14. API schemas expose useful report, workflow, transcript version, evidence quote, case, safety assessment, graph, and export fields.

The baseline is useful, but incomplete for the accepted UI/report concept model.

Current gaps and risks:

- navigation still exposes `RRE`, `Ingest`, and `Modules` prominently without enough product-facing reflection/case/report language
- dashboard copy still says `module lifecycle` and does not surface Cost State, draft expiration, active blocking jobs, validation warnings, or retained/corpus scope
- ingest is paste-only in the React surface and does not yet display audio deletion defaults, draft expiration, or save/retention implications when other intake modes are introduced
- prepare flow does not explicitly explain that analysis binds to a transcript version and that saving/case assignment changes retention posture
- analysis setup selects workflow rather than explicit `AnalysisScope` and `ReflectionLens` concepts
- safety UI is based on `risk_level`, `matched_categories`, and boolean `safety_mode` rather than structured `SafetyPosture`
- report UI shows transcript version and stale warning, but lacks a complete `ReportScope` header with scope type, included/excluded versions, case/corpus scope, lenses, validation status, and export readiness
- `exploratory_hypotheses` are displayed through ordinary finding cards without structured hypothesis support sections
- `interventions` still appear in the report package viewer instead of product-safe `ReflectionPoint` language
- graph UI is useful but still presents graph edges without stronger boundary labels for support, contradiction, limitation, corpus recurrence, stale evidence, and safety posture
- case UI supports longitudinal compare/synthesis but does not yet make `Case Evidence Corpus` and retention/corpus implications explicit enough
- longitudinal synthesis currently displays raw parsed JSON preview, which is useful for developers but not an aligned product report surface
- delete/remove/export flows are not yet concept-complete from the UI perspective
- export package action does not yet preview export scope, version basis, limitations, server retention, or downloaded-copy boundary
- login power state uses current implementation vocabulary such as `awake`, and should later reconcile with accepted Cost State vocabulary
- settings/privacy copy is useful but still points to developer docs for retention rather than product-level retention surfaces
- UI tests do not yet encode terminology, report boundary, safety, corpus, export, deletion, or cost-state acceptance gates

---

# Accepted Implementation Principle

```text
Future UI and report implementation must be reviewed as concept implementation, not merely presentation work.
```

A later UI change should not pass merely because it renders data correctly.

It must preserve accepted terminology, scope visibility, evidence lineage, hypothesis boundaries, safety posture, retention/deletion meaning, export boundaries, and cost-state semantics.

---

# Implementation Planning Decisions

## 1. Product-facing navigation should become reflection-oriented

Later implementation should evolve navigation from implementation categories toward product concepts.

Near-term acceptable navigation:

```text
Dashboard
Transcripts
Cases
Reports
Evidence / Graph
Exports
Settings
System Status
```

Implementation-only surfaces such as modules, workflow lifecycle, evaluations, and debug graph views may remain available to admin/developer mode, but should not dominate ordinary personal-owner product navigation.

## 2. Dashboard should become the owner orientation surface

Dashboard should show or link to:

- current Cost State
- recent transcripts and draft expirations
- recent cases and case evidence corpus state
- reports needing review
- active or recent reflection runs
- validation warnings/failures requiring attention
- active blocking jobs keeping the app awake
- retention/privacy reminders when useful

It should not frame the product as a module/workflow dashboard.

## 3. Intake and prepare flows should expose lifecycle state

Transcript intake and preparation should show:

- source type
- draft vs saved status
- draft expiration when applicable
- audio deletion default when audio intake is used
- current transcript version
- readiness for analysis
- save/retain action meaning
- case assignment retention/corpus effect

Analysis should bind to a visible transcript version.

## 4. Analysis setup should declare AnalysisScope before execution

Later UI should not only pick a workflow.

It should let the user understand and eventually choose:

```text
single transcript version
selected transcript set
case evidence corpus
```

The screen should show included versions, selected case/corpus when applicable, selected reflection lenses, user-provided context or hypotheses, retention/export posture, and safety boundary language.

Workflow IDs may remain implementation details.

## 5. Reflection Lens language should wrap module UI

Modules are implementation.

Reflection lenses are product-facing.

A future module/lens screen should expose:

- product-safe lens name
- lens family
- source-framework references as reasoning references, not authority
- confidence ceiling
- permitted inference depth
- evidence requirements
- safety behavior
- corpus/hypothesis capability
- forbidden claims and required limitations, if visible in admin mode

## 6. Report header should become a ReportScope surface

Every report should begin with a scope and boundary header.

Minimum fields:

```text
report type
analysis scope type
source transcript version ids
case/corpus scope if applicable
selected reflection lenses
validation status
safety posture
generated at
stale evidence status
export readiness
boundary reminder
```

This should be implemented before report UI grows more persuasive or export-heavy.

## 7. Findings, hypotheses, and reflection points need distinct display components

Later implementation should split display semantics:

- `FindingCard` for evidence-backed findings
- `HypothesisCard` or equivalent for `PsychologicalHypothesis` plus support assessment
- `ReflectionPointCard` or equivalent for non-prescriptive self-review prompts
- `SafetyPostureBanner` or equivalent for elevated/high-risk contexts
- `ValidationStatusPanel` or equivalent for warnings/failures

Compatibility layers may still read legacy `findings`, `exploratory_hypotheses`, `recommendations`, and `interventions`, but product-facing labels should migrate.

## 8. Safety posture should alter layout and available actions

Elevated or high-risk safety posture should affect:

- report header/banner
- section ordering
- hypothesis language
- reflection point availability
- export readiness
- caution text
- suppression of ordinary mutual-improvement prompts
- avoidance of reconciliation/confrontation pressure

Safety posture is not a legal or clinical conclusion.

## 9. Corpus and case UI must show evidence boundaries

Case UI should describe cases as retained longitudinal evidence boundaries, not simple folders.

Case/corpus views should show:

- case evidence corpus label
- included transcript versions
- time span
- recurrence count
- contradiction/weakening/context split/temporal change summaries
- stale/deleted evidence status
- what is excluded from the corpus
- reminder that case-level conclusions are not account-wide conclusions

## 10. Graph UI should become boundary-aware

Graph UI should preserve visual exploration while adding boundary labels for:

- evidence quote nodes
- finding nodes
- hypothesis nodes
- reflection point nodes
- safety posture nodes or annotations
- support/contradiction/alternative/limitation edges
- corpus recurrence/strengthening/weakening/contextualization edges
- stale/deleted evidence state

Edges should not imply causality, hidden intent, identity, or verdict unless explicitly bounded and validated.

## 11. Export UI should become a deliberate export-readiness flow

Export should preview:

- report scope
- included transcript versions
- included evidence appendix
- safety and hypothesis limitations
- validation status
- redaction choice
- server-retention behavior
- downloaded-copy boundary

Export should be blocked or warned when report/export readiness gates fail.

## 12. Deletion UI should preview cascade effects

Deletion and remove-from-case flows should distinguish:

- delete transcript
- delete report
- delete export artifact
- remove transcript from case
- delete case wrapper only
- delete case and contained retained transcripts, if ever supported

The UI should preview dependent evidence, reports, graph objects, corpus claims, and stale-marking/recompute behavior.

## 13. Cost State should become a System Status surface

Later UI should expose accepted Cost State vocabulary:

```text
asleep
waking
active
idle_pending
shutting_down
failed_wake
failed_shutdown if introduced
maintenance
```

The status surface should show active jobs keeping the app awake, idle warning, manual wake/sleep/keep-awake controls when implemented, failed wake/retry state, and maintenance status.

It should not imply that sleeping means data loss or report invalidity.

## 14. Settings should become product-retention/privacy oriented

Settings should eventually expose product-level retention and privacy controls rather than pointing users to developer docs.

Near-term settings targets:

- account/session status
- privacy reminders
- default export redaction preference
- retention defaults display
- draft expiration display
- case/corpus retention explanation
- content-free logs reminder
- cost-state preferences when implemented

---

# Proposed Implementation Sequence

## Stage 0 — UI/report authority lock

Create implementation-facing notes that point developers to 002-G and 003-G before UI/report work begins.

## Stage 1 — UI surface inventory and copy audit

Inventory all pages, components, API types, report schemas, and current labels against the accepted language matrix.

## Stage 2 — Navigation and product framing plan

Define the personal-owner navigation model and admin/developer escape hatches for implementation surfaces.

## Stage 3 — Lifecycle/status display plan

Define transcript draft/saved/version/case-retained/export/cost-state status components and copy.

## Stage 4 — Analysis setup scope plan

Define UI state and API dependency for `AnalysisScope`, selected versions, selected case/corpus, reflection lenses, user context, and safety note.

## Stage 5 — ReportScope header and validation panel plan

Define report header, validation status panel, stale evidence display, safety posture display, and export readiness display.

## Stage 6 — Finding/hypothesis/reflection point component plan

Split current finding rendering into distinct product-safe components and compatibility mappings.

## Stage 7 — Case/corpus UI plan

Define case evidence corpus display, longitudinal evidence summaries, recurrence/contradiction/change language, and retention/corpus warnings.

## Stage 8 — Graph/evidence lineage UI plan

Define boundary-aware graph node/edge labels, evidence quote expansion, stale state, and source version display.

## Stage 9 — Export and deletion flow plan

Define export preview/readiness and deletion cascade preview before expanding export/delete features.

## Stage 10 — System Status / Cost State UI plan

Define cost-state status and control UI using accepted vocabulary and job-safe behavior.

## Stage 11 — UI/report acceptance tests

Define tests for product terminology, report scope, evidence display, hypothesis support, safety posture, reflection points, corpus scope, deletion/export boundaries, and cost-state state display.

---

# Required Gates

003-G carries forward or introduces these gates for later implementation:

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

003-H should consolidate whether Phase 003 has enough implementation-readiness material to authorize a next phase.

For UI/report work, 003-H should specifically check:

- whether UI/report implementation is sequenced after domain, lifecycle, privacy, analysis, validation, and cost-state foundations
- whether product-facing language avoids diagnosis, therapy, surveillance, and raw transcription framing
- whether reports display scope, evidence basis, safety posture, validation status, and limitations before export expansion
- whether case/corpus UI prevents hidden account-wide inference
- whether deletion/export flows carry explicit boundary and cascade gates
- whether cost-state UI explains low-cost sleep/wake without implying product failure

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

# Acceptance Result

The UI/report alignment implementation plan is ready to feed the Phase 003 exit review.

Proceed next to:

```text
003-H — Phase 003 Exit Review and Consolidation
```
