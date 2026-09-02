# 003-C Lifecycle Artifact Implementation Matrix

## Status

Accepted as the Phase 003-C lifecycle artifact implementation matrix.

---

# Purpose

Map accepted lifecycle/retention concepts to current implementation artifacts, proposed implementation targets, default retention behavior, and gates.

This matrix is implementation planning only.

---

# Matrix Legend

| Status | Meaning |
|---|---|
| `existing_foundation` | Useful implementation exists and should be preserved |
| `existing_but_incomplete` | Useful implementation exists but lacks accepted lifecycle semantics |
| `new_or_equivalent` | Needs a new object, field set, config registry, or service contract |
| `policy_only_initially` | May begin as documented/configured policy before schema |
| `defer` | Valid but not needed for current implementation foundation |

---

# Artifact Matrix

| Artifact / Concept | Current Implementation Surface | Status | Required Implementation Target | Default Retention | Primary Gates |
|---|---|---|---|---|---|
| Recording / audio upload | `saved_upload`, `/api/transcribe`, temp file path, `SourceType.AUDIO` | existing_but_incomplete | `SourceArtifact` / `RecordingArtifact` lifecycle metadata | Ephemeral; delete after successful transcription | retention_gate, lifecycle_event_redaction_gate |
| Failed transcription audio | temp file/provider job behavior | new_or_equivalent | failed-state TTL and retry/debug window, max 24h | Temporary | retention_gate, log_redaction_gate |
| Transcription result | `TranscribeResponse`, segments, language/duration metadata | existing_foundation | non-durable output unless saved/ingested | Temporary until transcript save/ingest decision | retention_gate, privacy_boundary_gate |
| Transcript draft | `Transcript.analysis_ready`, `skip_review`, `ready_at` | existing_but_incomplete | explicit draft / review / saved lifecycle state | Temporary; recommended 7 days | retention_gate, retention_visibility_gate |
| Saved transcript | `TranscriptRow`, `Transcript`, `owner_user_id` | existing_foundation | durable retention marker or rule inheritance | Durable until user deletion | privacy_boundary_gate, deletion_cascade_gate |
| Case-retained transcript | `case_id`, `Case`, `CaseDetail` | existing_but_incomplete | case assignment as retention and corpus promotion | Durable until transcript/case deletion | corpus_reasoning_gate, retention_gate |
| Transcript version | `TranscriptVersion`, `TranscriptVersionRow`, `current_version_id` | existing_foundation | version dependency tracking and stale/current semantics | Retain while evidence/report/corpus depends on it | analysis_boundary_gate, corpus_staleness_gate |
| Evidence quote | `EvidenceQuote`, `EvidenceQuoteRow` | existing_foundation | required version binding for retained analysis | Inherit transcript version/report/corpus retention | analysis_boundary_gate, deletion_cascade_gate |
| Reflection run / workflow run | `WorkflowRun`, `WorkflowRunRow` | existing_but_incomplete | retention inheritance from `AnalysisScope` and evidence basis | Inherit source scope | report_scope_gate, deletion_cascade_gate |
| Lens execution / module run | `ModuleRun`, `ModuleRunRow` | existing_but_incomplete | retention inheritance and content-safety constraints for raw/parsed output | Inherit reflection run/source scope | privacy_boundary_gate, log_redaction_gate |
| Finding | `Finding`, `FindingRow` | existing_foundation | retained only with evidence basis; evidence dependency visible | Inherit evidence basis | analysis_boundary_gate, deletion_cascade_gate |
| Psychological hypothesis | `FindingType.HYPOTHESIS` | existing_but_incomplete | bounded object or structured subobject with retention inheritance | Inherit evidence basis | hypothesis_boundary_gate, deletion_cascade_gate |
| Reflection point | `FindingType.INTERVENTION`, report interventions | existing_but_incomplete | non-prescriptive reflection object with source evidence | Inherit report/evidence basis | reflection_point_gate, safety_override_gate |
| Reasoning graph node/edge | `Construct`, `ConstructRelationship`, rows | existing_foundation | staleness and evidence-dependency rules | Inherit evidence basis/corpus scope | corpus_staleness_gate, deletion_cascade_gate |
| Corpus pattern assessment | graph/report summaries | new_or_equivalent | explicit corpus object with source transcript versions and quote IDs | Inherit case/selected scope | corpus_reasoning_gate, corpus_staleness_gate |
| Reflection report | `SynthesisReport`, `SynthesisReportRow` | existing_but_incomplete | report scope/version basis and retention inheritance | Inherit source transcript/case scope | report_scope_gate, export_boundary_gate |
| Export artifact | no clear first-class model | new_or_equivalent | explicit export lifecycle metadata and server-retention rule | Download-only by default | export_boundary_gate, privacy_boundary_gate |
| Retention rule | `transcript_retention_days` setting only | existing_but_incomplete | explicit per-artifact policy registry or model | Artifact-specific | retention_gate |
| Artifact lifecycle event | auth audit exists; lifecycle-specific gap | new_or_equivalent | content-free artifact state-transition events | Operational retention only | lifecycle_event_redaction_gate, log_redaction_gate |
| Logs/telemetry | app logs, audit events, telemetry fields | existing_but_incomplete | content-free lifecycle and operational telemetry | Operational only | log_redaction_gate |

---

# Implementation Target Set

The minimum target set for a later lifecycle implementation phase should include:

```text
SourceArtifact / RecordingArtifact equivalent
RetentionRule equivalent
TranscriptLifecycleState equivalent
ArtifactLifecycleEvent equivalent
ExportArtifact equivalent
DeletionCascadeContract equivalent
CorpusStalenessPolicy equivalent
```

Equivalent means a clearly documented field/config/service contract may be acceptable before a dedicated database table, as long as gates pass.

---

# Decisions

## Transcript aggregate

Keep `Transcript` as the practical aggregate for retained text, speakers, turns, versions, and evidence quotes.

## Source artifact boundary

Represent audio lifecycle outside `Transcript.raw_text` and avoid treating `SourceType.AUDIO` as a retention policy.

## Retention rule posture

Move from global/coarse retention settings toward artifact-specific rules with explicit promotion and deletion behavior.

## Case corpus posture

Case membership should become both retention-significant and corpus-significant.

## Derived artifacts

Derived artifacts must either inherit source retention or be represented as explicit exports.

---

# Handoff

Use this matrix to populate the 003-C work packages and later 003-D privacy/encryption planning.
