# 002-H Refactor Backlog

## Status

Accepted as the Phase 002-H refactor backlog inventory.

This backlog is not an implementation authorization.

It provides candidate work items for later phases after the 002-I exit review.

---

# Purpose

Translate Phase 002 concept-to-architecture decisions into a structured backlog that can be sequenced safely.

The backlog preserves the principle:

```text
concept authority first, sensitive-data safety second, implementation convenience third
```

---

# Backlog Legend

| Field | Meaning |
|---|---|
| ID | Stable planning identifier |
| Priority | P0, P1, or P2 |
| Type | Documentation, Decision, Implementation, Validation, Security, UX, Operations |
| Source | Phase 002 subgroup that produced the need |
| Gate | Acceptance gate that must pass |

---

# P0 Backlog

| ID | Priority | Type | Source | Backlog Item | Gate |
|---|---|---|---|---|---|
| H-P0-001 | P0 | Documentation | 002-A | Reconcile living documentation indexes so concept docs and Phase 002 architecture are the current authority | documentation_authority_gate |
| H-P0-002 | P0 | Documentation | 002-A | Mark older v2.1 planning material as reference, superseded, or pending reconciliation | documentation_authority_gate |
| H-P0-003 | P0 | Documentation | 002-A/002-G | Add terminology drift checks for product-facing terms such as Reflection Lens, Reflection Run, Reflection Point, Case Evidence Corpus, and Cost State | terminology_drift_gate |
| H-P0-004 | P0 | Implementation | 002-B | Preserve and harden Transcript, TranscriptVersion, EvidenceQuote, Finding, Case, and graph concepts as prototype foundations | domain_mapping_gate |
| H-P0-005 | P0 | Decision | 002-B/002-C | Decide whether Transcript remains the practical aggregate root or whether ConversationRecord becomes a separate implementation object | domain_mapping_gate |
| H-P0-006 | P0 | Implementation | 002-C | Add explicit Recording / SourceArtifact lifecycle boundary for ephemeral audio | retention_gate |
| H-P0-007 | P0 | Implementation | 002-C | Add RetentionRule semantics or equivalent configuration for each artifact class | retention_gate |
| H-P0-008 | P0 | Implementation | 002-C | Define and implement draft expiration and failed-audio retry TTL behavior | retention_gate |
| H-P0-009 | P0 | Implementation | 002-C | Define deletion cascades for drafts, saved transcripts, versions, evidence, reports, cases, exports, and graph objects | deletion_cascade_gate |
| H-P0-010 | P0 | Security | 002-D | Ensure every retained sensitive artifact carries or inherits owner scope | privacy_boundary_gate |
| H-P0-011 | P0 | Security | 002-D | Confirm logs and telemetry never include audio, transcript bodies, evidence quote text, prompt payloads, model completions, report bodies, exports, secrets, session tokens, or login codes | log_redaction_gate |
| H-P0-012 | P0 | Security | 002-D | Confirm infrastructure encryption baseline before expanding retained sensitive content | encryption_baseline_gate |
| H-P0-013 | P0 | Security | 002-D | Require explicit corpus scope for multi-transcript reasoning; block hidden account-wide inference | corpus_reasoning_gate |
| H-P0-014 | P0 | Implementation | 002-E | Add AnalysisScope or equivalent before prompt/report/corpus work | analysis_boundary_gate |
| H-P0-015 | P0 | Implementation | 002-E | Add ReflectionLensContract or equivalent lens registry metadata | analysis_boundary_gate |
| H-P0-016 | P0 | Implementation | 002-E | Add bounded PsychologicalHypothesis / HypothesisSupportAssessment semantics or schema convention | hypothesis_boundary_gate |
| H-P0-017 | P0 | Implementation | 002-E | Add SafetyPosture as structured override behavior beyond a boolean | safety_override_gate |
| H-P0-018 | P0 | Validation | 002-E | Add validators for diagnosis/label prohibition, hidden intent, therapeutic authority, safety mutualization, corpus overreach, and evidence linkage | validation_gate |
| H-P0-019 | P0 | Operations | 002-F | Define CostStateRecord or equivalent control-plane state | cost_state_gate |
| H-P0-020 | P0 | Operations | 002-F | Define BlockingJobRecord or equivalent job registry to prevent unsafe shutdown | job_safe_shutdown_gate |
| H-P0-021 | P0 | Operations | 002-F | Replace or redesign deleted GitHub Actions workflow assumptions before any deployment automation is restored | workflow_replacement_gate |
| H-P0-022 | P0 | UX | 002-G | Add report scope headers showing single transcript, selected transcript set, or case evidence corpus | report_scope_gate |
| H-P0-023 | P0 | UX | 002-G | Replace user-facing Recommendation / Intervention language with Reflection Point semantics | reflection_point_gate |
| H-P0-024 | P0 | UX | 002-G | Show retention and deletion consequences for transcript save, case assignment, delete, unlink, and export actions | retention_visibility_gate |

---

# P1 Backlog

| ID | Priority | Type | Source | Backlog Item | Gate |
|---|---|---|---|---|---|
| H-P1-001 | P1 | Implementation | 002-C | Add ArtifactLifecycleEvent or equivalent non-content audit/event model | lifecycle_event_redaction_gate |
| H-P1-002 | P1 | Implementation | 002-C | Add ExportArtifact semantics for deliberate portable outputs | export_boundary_gate |
| H-P1-003 | P1 | Security | 002-D | Design application-level / field-level encryption target for retained transcripts, evidence, findings, hypotheses, reflection points, reports, cases, corpus summaries, and exports | encryption_target_gate |
| H-P1-004 | P1 | Implementation | 002-D/002-E | Add Case Evidence Corpus support that distinguishes retained case scope from account-wide data | corpus_reasoning_gate |
| H-P1-005 | P1 | Implementation | 002-E | Add CorpusPatternAssessment for recurrence, contradiction, strengthening, weakening, context split, and temporal change | corpus_reasoning_gate |
| H-P1-006 | P1 | Implementation | 002-E | Add graph edge types for supports, contradicts, recurs_across, strengthens, weakens, contextualizes, limited_by, and requires_safety_override | analysis_boundary_gate |
| H-P1-007 | P1 | Validation | 002-E | Add fixtures for user-provided diagnosis handling and non-diagnostic hypothesis output | evaluation_gate |
| H-P1-008 | P1 | Validation | 002-E | Add safety fixtures for elevated and high-risk safety contexts | evaluation_gate |
| H-P1-009 | P1 | Validation | 002-E | Add corpus reasoning fixtures that test recurrence, contradiction, duplicate evidence, and stale evidence | evaluation_gate |
| H-P1-010 | P1 | Operations | 002-F | Add idle evaluator using both authenticated user activity and blocking job activity | cost_state_gate |
| H-P1-011 | P1 | Operations | 002-F | Add manual owner controls for wake, sleep, keep-awake, retry wake, cancel job, and maintenance where appropriate | cost_state_gate |
| H-P1-012 | P1 | UX | 002-G | Add Case Evidence Corpus UI surfaces showing included transcripts, versions, evidence counts, recurrence, contradiction, and stale evidence status | ui_language_gate |
| H-P1-013 | P1 | UX | 002-G | Add safety posture UI behavior for elevated/high-risk contexts | safety_ux_gate |
| H-P1-014 | P1 | UX | 002-G | Add cost-state UI language for asleep, waking, active, idle pending, shutting down, failed wake, and maintenance | cost_state_ux_gate |
| H-P1-015 | P1 | UX | 002-G | Add export flow language preserving scope, version basis, limitations, and server-retention behavior | export_boundary_gate |

---

# P2 Backlog

| ID | Priority | Type | Source | Backlog Item | Gate |
|---|---|---|---|---|---|
| H-P2-001 | P2 | Decision | 002-C | Decide whether explicit long-term audio retention is ever supported | retention_gate |
| H-P2-002 | P2 | Decision | 002-D | Decide whether encrypted search or session-only decrypted search is needed for personal mode | privacy_boundary_gate |
| H-P2-003 | P2 | Decision | 002-D | Decide whether future workspace/corpus scopes are needed before enterprise planning | corpus_reasoning_gate |
| H-P2-004 | P2 | Decision | 002-E | Decide whether existing confidence enum values should be renamed or mapped through aliases | confidence_calibration_gate |
| H-P2-005 | P2 | Decision | 002-F | Decide whether FailedShutdown should become a separate state from FailedWake | cost_state_gate |
| H-P2-006 | P2 | Decision | 002-F | Decide maximum keep-awake duration and long-job timeout defaults | cost_state_gate |
| H-P2-007 | P2 | UX | 002-G | Design visual graph exploration for evidence, hypothesis, safety, and corpus edges | ui_language_gate |
| H-P2-008 | P2 | UX | 002-G | Design advanced report export options such as redaction level or encrypted archive | export_boundary_gate |

---

# Suggested Minimum Phase 003 Scope

The smallest safe implementation-starting scope should include:

1. documentation authority cleanup
2. domain terminology mapping
3. lifecycle/retention foundation planning-to-implementation handoff
4. privacy/logging baseline verification
5. analysis boundary contract planning-to-implementation handoff
6. cost-state control-plane replacement planning
7. UI terminology/report-scope audit
8. evaluation gate design

This does not mean all implementation happens in one phase.

It means the first implementation phase should avoid narrow local fixes that make later concept alignment harder.

---

# Backlog Dependency Notes

## Documentation before code

P0 documentation authority tasks should happen before broad implementation so stale terminology does not reassert itself.

## Retention before corpus expansion

Corpus reasoning should not expand until retention, deletion, and owner scope are clear.

## Safety before report polish

Safety posture and validation gates should be defined before user-facing report polish.

## Cost-state before restored deployment automation

Old GitHub Actions workflows were removed intentionally.

Any new automation should be designed from the 002-F control-plane requirements rather than restored by habit.

## UI after concept language

UI work should not invent product wording locally.

It should draw from the 002-G language matrix and report requirements.

---

# Decision

This backlog is ready for 002-I exit review.

002-I should use it to decide which items become the authorized Phase 003 scope and which remain deferred.