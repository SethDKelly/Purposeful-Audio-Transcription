# 003-G UI/Report Alignment Gate Checklist

## Status

Accepted as the Phase 003-G UI/report alignment gate checklist.

---

# Purpose

Define the minimum questions later implementation must answer before UI, report, graph, export, deletion, settings, cost-state display, API DTO, or test changes are accepted.

This checklist is not code.

---

# Gate Principle

```text
A UI/report surface is not acceptable merely because it displays backend data; it is acceptable only when it preserves product framing, scope, evidence, uncertainty, safety posture, validation state, retention meaning, export boundaries, corpus boundaries, and cost-state semantics.
```

---

# Universal UI/Report Checklist

Every UI/report implementation must answer:

1. Does the surface use product-safe terminology?
2. Does the surface avoid diagnosis, therapy, surveillance, adjudication, and raw transcription framing?
3. Is the evidence scope visible before analysis when applicable?
4. Is the transcript version basis visible where reports, evidence, or graph claims depend on it?
5. Are hypotheses distinct from findings and diagnosis-like labels?
6. Are support levels distinct from confidence?
7. Are evidence quotes inspectable for claims that rely on them?
8. Are alternatives, limitations, contradictions, and uncertainty visible where required?
9. Is safety posture visible and does it change report/reflection behavior where required?
10. Are ordinary recommendations/interventions avoided in favor of reflection points?
11. Is case/corpus scope explicit for multi-transcript reasoning?
12. Are stale/deleted evidence effects visible where relevant?
13. Are export scope, validation, redaction, retention, and downloaded-copy boundaries visible?
14. Are deletion or remove-from-case actions previewed with cascade implications?
15. Is Cost State shown as intentional low-cost behavior, not product failure?
16. Are admin/developer/debug surfaces separated from ordinary reflective product flows?
17. Is sensitive content kept out of operational status, logs, and debug-style user messages?
18. Are tests defined for both acceptable and boundary-failing surfaces?

---

# Operation-Specific Checks

## Product framing and navigation

Required checks:

- product identity is reflection-first
- audio/transcription is presented as an input capability
- RRE appears as internal engine or compact brand shorthand, not sole conceptual authority
- implementation surfaces such as modules/workflows/evaluations are separated from ordinary owner flows or clearly marked
- navigation does not imply diagnosis, treatment, surveillance, or adjudication

Blocking failure examples:

- primary dashboard describes the product as an audio transcription dashboard
- ordinary navigation centers `Modules` and `Workflow lifecycle` without product-safe framing
- UI markets output as diagnosis, treatment, or professional decision support

---

## Transcript lifecycle and retention display

Required checks:

- source type is shown when relevant
- draft vs saved vs case-retained state is visible
- draft expiration is visible when applicable
- audio deletion default is visible for audio intake
- save/retain action meaning is clear
- case assignment retention and corpus implications are explained
- deletion path is discoverable

Blocking failure examples:

- upload/transcription implies durable retention without saying so
- case assignment appears to be only folder organization
- saved transcript and draft transcript look identical from a retention standpoint

---

## Analysis setup and scope display

Required checks:

- user sees whether analysis is single-transcript, selected-set, or case-corpus scoped
- included transcript versions are visible
- excluded/stale versions are not hidden
- requested reflection lenses are visible
- user-provided context/hypotheses are marked as user context, not system truth
- non-diagnostic boundary is visible enough for hypothesis-heavy flows

Blocking failure examples:

- `Analyze everything` silently uses all retained account history
- workflow IDs are the only user-visible analysis setup concept
- user-provided diagnosis is displayed as system-confirmed context

---

## Report scope and validation state

Required checks:

- report header shows scope type
- source transcript versions are visible
- case/corpus scope is visible when applicable
- validation status is visible or at least available
- stale evidence/report state is visible
- report limitations and boundary reminder are present
- blocked sections are hidden or explained safely

Blocking failure examples:

- report cannot tell the user what evidence basis it used
- stale report warning is missing after transcript version changes
- report displays failed/unvalidated output as final reflection

---

## Finding and evidence display

Required checks:

- each evidence-backed claim shows quote IDs or clear evidence links
- quote text is concise by default with optional context
- evidence quotes preserve transcript version and speaker context when available
- findings without evidence are marked as limitations/uncertainty or blocked
- evidence precision warnings are visible where needed

Blocking failure examples:

- finding has no evidence and is displayed as ordinary insight
- evidence panel shows long paragraphs when atomic quotes are available
- quote IDs cannot be traced to source version

---

## Hypothesis display

Required checks:

- hypotheses appear as hypotheses, not findings or labels
- source is declared as system-generated, lens-generated, or user-provided context
- support level uses allowed labels
- evidence for, evidence against, missing evidence, and alternatives are visible
- confidence remains separate from support level
- boundary language states non-diagnostic limitations

Blocking failure examples:

- hypothesis card says a person has a disorder or fixed trait
- support label says `confirmed` or `diagnosed`
- contradictory evidence is hidden

---

## Reflection point display

Required checks:

- reflection points are non-prescriptive
- reflection points link to evidence, finding, hypothesis, or safety posture
- reflection points are framed for self-review
- high-risk safety posture suppresses confrontation/reconciliation pressure
- treatment, command, and professional-instruction language is avoided

Blocking failure examples:

- UI labels the section `Treatment plan` or `Interventions` for ordinary users
- reflection point tells the user to confront someone after high-risk indicators
- recommendation appears without evidence basis or limitation

---

## Safety posture display

Required checks:

- safety posture label is visible when elevated/high-risk/immediate indicators exist
- trigger evidence is available where safe
- report section order changes where required
- unsafe mutual-improvement framing is suppressed
- reconciliation pressure is blocked in high-risk contexts
- posture does not claim legal or clinical determination
- product does not present itself as crisis support

Blocking failure examples:

- direct threat is rendered as ordinary relationship communication issue
- report says both sides should compromise when coercion indicators dominate
- UI labels a person as abusive/dangerous as a settled legal/identity verdict

---

## Case and corpus display

Required checks:

- case is described as retained longitudinal evidence boundary
- included transcript versions are visible
- corpus scope is explicit and owner-scoped
- recurrence claims show multiple transcript/version support
- contradictions, weakening evidence, context splits, and temporal change are visible
- stale/deleted evidence effects are visible
- case conclusions are not described as account-wide conclusions

Blocking failure examples:

- case view hides which transcripts were used for a corpus conclusion
- one transcript is presented as a longitudinal pattern
- corpus view treats prior model reports as independent evidence

---

## Graph and evidence lineage display

Required checks:

- graph legend distinguishes evidence, finding, hypothesis, reflection point, safety, limitation, alternative, and corpus nodes/edges where supported
- support, contradiction, alternative, limitation, recurrence, strengthening, weakening, and contextualization edges are distinguishable
- graph edges do not imply hidden intent or causality as fact
- stale/deleted evidence status is represented
- evidence quote lineage survives graph merging

Blocking failure examples:

- edge label implies `proves motive`
- merged graph hides source quote IDs
- stale/deleted evidence continues to appear as active support

---

## Export readiness and boundary display

Required checks:

- export preview shows scope and transcript version basis
- export includes or references evidence appendix when supported
- limitations and boundary language are preserved
- redaction choice is visible
- server retention behavior is explicit
- downloaded-copy boundary is explicit
- export blocks or warns on validation failures

Blocking failure examples:

- export loses source version metadata
- export appears to be a clinical/legal report
- UI implies downloaded copies can still be deleted by the app

---

## Deletion and remove-from-case display

Required checks:

- destructive target is clear
- cascade preview lists affected evidence, reports, graph objects, corpus claims, exports, and case links where applicable
- remove-from-case is distinguished from deleting transcript
- deleting report is distinguished from deleting source transcript
- downloaded export boundary is clear
- confirmation is explicit for destructive actions

Blocking failure examples:

- delete button only hides row with no cascade explanation
- remove-from-case deletes source transcript unexpectedly
- deleting transcript leaves corpus claim displayed without stale/recompute warning

---

## Cost-state display

Required checks:

- accepted Cost State vocabulary is used or current aliases are mapped
- sleeping/asleep is explained as intentional cost control
- wake progress is visible
- active blocking jobs keeping app awake are visible where relevant
- idle-pending warning is visible where relevant
- failed wake/shutdown is actionable
- maintenance is distinguished from failure
- cost state does not change analysis/report meaning

Blocking failure examples:

- asleep state appears as unexplained outage
- UI says data or reports are gone because app is asleep
- active reflection run keeping app awake is hidden

---

## Settings and privacy display

Required checks:

- account/session ownership is visible
- privacy reminders are product-facing rather than developer-doc dependent
- retention defaults are shown where available
- export redaction preference is explained as preference, not guarantee beyond server behavior
- case/corpus retention effects are explained
- content-free operational logs are described carefully when exposed
- future enterprise settings are not implied as present

Blocking failure examples:

- settings send ordinary users to developer docs as the only retention explanation
- redacted export preference is presented as guaranteed if server behavior differs
- enterprise/workspace controls appear before policy exists

---

## Accessibility and destructive-action usability

Required checks:

- safety and validation warnings are prominent and announced/accessibly labeled
- destructive actions require explicit confirmation
- keyboard navigation supports report/evidence review
- evidence expansion does not hide core claim context
- long IDs and technical labels are understandable or copyable without dominating the UI
- color is not the only status indicator

Blocking failure examples:

- high-risk safety status shown only by color
- delete cascade warning cannot be read by assistive tech
- evidence quote buttons are unlabeled or impossible to navigate by keyboard

---

# Required Test Families

Later implementation should add tests for:

```text
product_navigation_reflection_first
implementation_surfaces_admin_separated
transcript_lifecycle_badges_visible
draft_expiration_visible
audio_deletion_default_visible_when_audio_intake
case_assignment_retention_warning_visible
analysis_scope_selector_required
analysis_scope_versions_visible
user_context_not_system_truth_label
report_scope_header_visible
report_transcript_version_visible
report_stale_warning_visible
validation_status_visible
finding_evidence_links_visible
finding_without_evidence_marked_or_blocked
hypothesis_support_level_visible
hypothesis_not_diagnosis_label
reflection_point_not_intervention_label
safety_posture_banner_visible
safety_high_risk_blocks_reconciliation_prompt
case_evidence_corpus_label_visible
corpus_recurrence_requires_multiple_versions_display
corpus_contradiction_display_visible
graph_boundary_legend_visible
export_preview_scope_versions_visible
export_downloaded_copy_boundary_visible
delete_transcript_cascade_preview_visible
remove_from_case_not_delete_transcript_label
cost_state_asleep_not_outage_copy
cost_state_active_job_keeps_awake_visible
settings_retention_privacy_product_copy
```

---

# Validation Ordering

Recommended gate order:

```text
1. Product framing and terminology check
2. Navigation/admin-surface separation check
3. Scope/version/retention display check
4. Evidence and validation-state display check
5. Hypothesis/support/reflection-point language check
6. Safety posture and safety-override UI check
7. Case/corpus boundary display check
8. Graph/evidence lineage display check
9. Export readiness and boundary check
10. Deletion cascade preview check
11. Cost-state status/control display check
12. Settings/privacy display check
13. Accessibility/usability check
14. Regression and release readiness check
```

Reason:

Product framing and scope visibility should be checked before polishing report sections. Safety, export, deletion, and cost-state surfaces then add stricter contextual gates.

---

# Decision

This checklist carries forward to later implementation phases as part of the UI terminology gate, report scope gate, analysis scope display gate, evidence display gate, hypothesis display gate, safety posture display gate, corpus scope display gate, export readiness UI gate, deletion cascade UI gate, cost-state status UI gate, accessibility/usability gate, evaluation gate, regression gate, and release readiness gate.
