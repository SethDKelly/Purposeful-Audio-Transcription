# 003-B Domain Concept Mapping Inventory

## Status

Accepted as the Phase 003-B implementation-facing domain concept mapping inventory.

---

# Purpose

Map accepted product concepts to current implementation artifacts, transitional terminology, and later implementation targets.

This inventory is not a schema migration.

---

# Mapping Legend

| Status | Meaning |
|---|---|
| `retain` | Existing artifact is a strong foundation and should stay |
| `retain_and_harden` | Existing artifact is useful but needs stricter rules |
| `alias_then_migrate` | Keep current implementation name initially; introduce concept-safe alias/contract |
| `split_or_promote` | Current artifact partially covers a concept but needs separate representation |
| `new_or_equivalent` | Accepted concept needs a new object, field set, or explicit equivalent |
| `defer` | Valid concept, but not current implementation scope |

---

# Core Mapping Inventory

| Accepted Concept | Current Artifact(s) | 003-B Status | Implementation Planning Direction | Primary Gate |
|---|---|---|---|---|
| Secure Conversation Analysis and Reflection System | Product/docs frame | retain_and_harden | Keep as product identity; avoid transcription-only framing | terminology_drift_gate |
| Relationship Reasoning Engine / RRE | Engine wording in docs/code | retain | Use as internal engine identity, not sole product name | terminology_drift_gate |
| Conversation Record | `Transcript` plus source metadata | defer | Keep conceptual umbrella; do not add separate object yet | domain_mapping_gate |
| Recording | `SourceType.AUDIO`, upload/transcription path | new_or_equivalent | Plan `SourceArtifact` / `RecordingArtifact` in 003-C | retention_gate |
| Transcript | `backend/domain/transcript.py::Transcript` | retain | Keep practical aggregate root for now | domain_mapping_gate |
| Transcript Version | `TranscriptVersion`, `current_version_id`, workflow version refs | retain_and_harden | Make retained analysis version-bound | domain_mapping_gate |
| Speaker | `Speaker` | retain | Keep supporting evidence/speaker attribution object | domain_mapping_gate |
| Turn | `Turn` | retain | Keep supporting evidence anchoring object | domain_mapping_gate |
| Evidence Quote | `EvidenceQuote` | retain_and_harden | Require version binding for retained analysis | analysis_boundary_gate |
| Reflection Run | `WorkflowRun` | alias_then_migrate | Treat `WorkflowRun` as internal orchestration; expose ReflectionRun product meaning | terminology_drift_gate |
| Reflection Lens | `ModuleDefinition`, `ModuleRun` | alias_then_migrate | Map modules to lens contracts before rename | analysis_boundary_gate |
| Therapeutic Reflection Lens | `primary_lens`, module metadata | split_or_promote | Add lens-family/source-framework authority boundaries | analysis_boundary_gate |
| Diagnostic-framework-informed concept | none explicit | new_or_equivalent | Represent as lens/hypothesis metadata, not diagnosis authority | hypothesis_boundary_gate |
| Psychological Hypothesis | `FindingType.HYPOTHESIS`, report exploratory hypotheses | split_or_promote | Add `PsychologicalHypothesis` / support assessment or schema convention | hypothesis_boundary_gate |
| Hypothesis Support Assessment | finding evidence/alternatives/limitations | new_or_equivalent | Separate support level from confidence | confidence_calibration_gate |
| Finding | `Finding` | retain_and_harden | Keep evidence-backed claim object; avoid using it for all hypothesis semantics | analysis_boundary_gate |
| Confidence | `Confidence` enum | retain_and_harden | Keep transitional enum; map support separately | confidence_calibration_gate |
| Reflection Point | `FindingType.INTERVENTION`, `interventions`, recommendations | alias_then_migrate | Replace product-facing intervention/recommendation language | reflection_point_gate |
| Reasoning Graph | `Construct`, `ConstructRelationship`, relationship enum | retain_and_harden | Add edge semantics for corpus, safety, limitation, strengthening/weakening | corpus_reasoning_gate |
| Case | `Case`, `CaseDetail`, transcript `case_id` | retain_and_harden | Present as retention/corpus boundary, not only grouping | corpus_reasoning_gate |
| Case Evidence Corpus | `Case` plus linked transcripts | new_or_equivalent | Add explicit scope using retained transcript versions and evidence quote lineage | corpus_reasoning_gate |
| Retention Rule | none explicit in domain package | new_or_equivalent | Plan in 003-C before expanding retention/corpus behavior | retention_gate |
| Privacy Boundary | ownership/auth/security code/docs | new_or_equivalent | Plan in 003-D as owner scope and service-purpose access | privacy_boundary_gate |
| Analysis Scope | workflow transcript/version fields | new_or_equivalent | Add explicit scope before corpus reasoning and reports | analysis_boundary_gate |
| Safety Posture | `WorkflowRun.safety_mode`, `ModuleRun.safety_flags`, report safety flags | split_or_promote | Move beyond boolean/list into structured posture | safety_override_gate |
| Corpus Pattern Assessment | graph/reports partially | new_or_equivalent | Add recurrence/contradiction/temporal-change representation | corpus_reasoning_gate |
| Reflection Report | `SynthesisReport` | alias_then_migrate | Product-facing alias for synthesis output | report_scope_gate |
| Export | report ZIP/export behavior | new_or_equivalent | Plan explicit export artifact lifecycle in 003-C/003-D | export_boundary_gate |
| Cost State | deployment/AWS ops concepts | new_or_equivalent | Plan separately in 003-F, not core analysis domain | cost_state_gate |
| Personal Mode | deployment/policy posture | defer | Policy layer; do not complicate core domain | cost_state_gate |
| Future Enterprise Policy Layer | deferred enterprise concepts | defer | Do not introduce org/RBAC/workspace domain unless later authorized | documentation_authority_gate |

---

# Existing Domain Artifacts to Preserve

These are strong enough to serve as implementation foundations:

```text
Transcript
TranscriptVersion
Speaker
Turn
EvidenceQuote
Finding
Construct
ConstructRelationship
WorkflowRun
ModuleRun
Case
SynthesisReport
Confidence
```

Preservation does not mean their current names are always product-facing.

---

# Transitional Alias Map

| Current Implementation Name | Product / Concept Alias | Migration Notes |
|---|---|---|
| `WorkflowRun` | `ReflectionRun` | Alias first; defer destructive rename |
| `Workflow` | `ReflectionWorkflow` or internal orchestration | Product may not need visible workflow concept |
| `ModuleDefinition` | `ReflectionLensContract` source | Add contract metadata before rename |
| `ModuleRun` | `LensExecution` / lens run | Internal detail within ReflectionRun |
| `SynthesisReport` | `ReflectionReport` | User-facing report term should shift first |
| `FindingType.INTERVENTION` | `ReflectionPoint` | Requires safety-bounded semantics |
| report `interventions` | `reflection_points` | Defer field rename until report compatibility plan |
| `safety_mode` | `SafetyPosture` / safety override | Boolean remains transitional only |
| `safety_flags` | safety indicators / trigger evidence | Should link to evidence and posture |
| `SourceType.AUDIO` | Recording source marker | Lifecycle needs SourceArtifact/RecordingArtifact |
| `RelationshipType.INTERVENTION_FOR` | supports/reflection_point_for replacement | Avoid treatment-like relationship language |

---

# Deferred Naming Decisions

These decisions should not be forced inside 003-B:

1. Whether to introduce a physical `ConversationRecord` table/class.
2. Whether to rename `WorkflowRun` in code or keep it as internal orchestration forever.
3. Whether `ReflectionLensContract` becomes a table, Pydantic model, registry config, or metadata convention.
4. Whether `PsychologicalHypothesis` is a separate persisted model or structured report subobject first.
5. Whether `ReflectionPoint` replaces `FindingType.INTERVENTION` immediately or through compatibility aliases.
6. Whether `SafetyPosture` replaces `safety_mode` in one migration or through staged fields.
7. Whether confidence enum values are renamed or concept aliases are layered over them.

---

# Decision

Use this inventory as the 003-B mapping baseline.

Later implementation phases should not introduce domain names or semantics that conflict with this mapping unless a later phase exit review explicitly supersedes it.
