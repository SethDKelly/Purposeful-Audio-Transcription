# 003-D Privacy and Encryption Surface Matrix

## Status

Accepted as the Phase 003-D privacy and encryption surface implementation matrix.

---

# Purpose

Map accepted privacy/encryption concepts to current implementation surfaces, remaining risks, target implementation posture, and gates.

This matrix is implementation planning only.

---

# Matrix Legend

| Status | Meaning |
|---|---|
| `existing_foundation` | Useful implementation exists and should be preserved |
| `existing_but_incomplete` | Useful implementation exists but lacks accepted privacy/encryption semantics |
| `new_or_equivalent` | Needs a new object, field set, config registry, or service contract |
| `policy_only_initially` | May begin as documented/configured policy before schema/code |
| `defer` | Valid but not needed for current implementation foundation |

---

# Surface Matrix

| Surface / Concept | Current Implementation Surface | Status | Required Implementation Target | Primary Gates |
|---|---|---|---|---|
| Identity / owner | `UserRow`, `AuthUser`, passwordless OTP | existing_foundation | personal owner/operator identity with future stronger-provider compatibility | privacy_boundary_gate, owner_scope_gate |
| Login code | `LoginCodeRow`, hashed code, expiry, attempts | existing_foundation | keep non-content auth storage; classify email metadata | metadata_sensitivity_gate, log_redaction_gate |
| Session | `UserSessionRow`, hashed session token, expiry/revocation | existing_foundation | cookie/security hardening by deployment mode | privacy_boundary_gate, regression_gate |
| API auth gate | `APIKeyMiddleware`, `require_auth_context` | existing_but_incomplete | consistent sensitive-route gate; converge future work on `/api/v1` | route_compatibility_gate, owner_scope_gate |
| Admin/API key path | `X-API-Key`, admin bypass | existing_but_incomplete | break-glass-only posture; avoid normal sensitive workflows relying on admin bypass | privacy_boundary_gate, audit_gate |
| Ownership helpers | `assert_transcript_access`, `assert_case_access`, `assert_run_access` | existing_foundation | expand owner checks to all sensitive resource reads/writes | owner_scope_gate |
| Legacy null owner | `assert_resource_owner` allows null owner | existing_but_incomplete | transitional compatibility policy, backfill plan, and sunset gate | legacy_null_owner_gate |
| Legacy `/api` routes | `transcribe`, `transcripts`, `cases` route modules | existing_but_incomplete | compatibility map; no expansion of sensitive behavior without auth/ownership plan | route_compatibility_gate |
| Transcript owner scope | `TranscriptRow.owner_user_id`, ingest accepts optional owner | existing_but_incomplete | owner required for retained personal-mode sensitive artifacts after migration | owner_scope_gate, privacy_boundary_gate |
| Case owner scope | `CaseRow.owner_user_id` | existing_but_incomplete | case corpus owner inheritance and case access checks | owner_scope_gate, corpus_scope_gate |
| Workflow/reflection run owner | `WorkflowRunRow.owner_user_id` | existing_but_incomplete | owner inheritance from analysis scope / transcript version / case | owner_scope_gate, service_purpose_access_gate |
| Sensitive child artifacts | speaker, turn, version, evidence, finding, graph, report rows | existing_but_incomplete | inherited owner contract; optional denormalized owner fields if needed | owner_inheritance_gate, deletion_cascade_gate |
| Source artifact / recording | temp upload context, `SourceType.AUDIO` | existing_but_incomplete | owner-scoped ephemeral source artifact metadata; encrypted temp storage posture | privacy_boundary_gate, encryption_baseline_gate |
| Retained transcript text | `TranscriptRow.raw_text`, `TurnRow.text` | existing_but_incomplete | field-level/application encryption target | field_encryption_target_gate |
| Evidence text | `EvidenceQuoteRow.text`, `context_before`, `context_after`, `span_text` | existing_but_incomplete | field-level/application encryption target; no log exposure | field_encryption_target_gate, log_redaction_gate |
| Model outputs | `ModuleRunRow.raw_output`, `parsed_output`, report JSON | existing_but_incomplete | minimize raw persistence; encrypt retained sensitive outputs | field_encryption_target_gate, service_purpose_access_gate |
| Findings / graph | finding summaries, construct labels/rationales | existing_but_incomplete | encrypt sensitive text; preserve evidence lineage | field_encryption_target_gate, corpus_scope_gate |
| Safety events | `SafetyEventRow.details_json`, categories | existing_but_incomplete | classify as sensitive; redact/free-text allowlist | metadata_sensitivity_gate, log_redaction_gate |
| Lifecycle events | auth audit exists; lifecycle-specific gap | new_or_equivalent | content-free lifecycle event model / allowlist | lifecycle_event_redaction_gate |
| Audit logs | `audit_event`, `AuthAuditEventRow` | existing_but_incomplete | event allowlists, no sensitive free text, metadata classification | lifecycle_event_redaction_gate, metadata_sensitivity_gate |
| Log sanitizer | `safe_extra`, deny-list, redaction filter | existing_foundation | expand deny/allow coverage and test across call sites | log_redaction_gate |
| JSON logs | `JsonLogFormatter` standard extra keys | existing_foundation | keep allowlisted operation metadata only | log_redaction_gate |
| Settings | auth, cookie, log, retention, AWS, worker controls | existing_foundation | deployment-mode privacy baseline checklist | encryption_baseline_gate, privacy_boundary_gate |
| Export artifact | no clear first-class object | new_or_equivalent | owner-scoped, version-bound, encrypted if retained server-side | export_boundary_gate, field_encryption_target_gate |
| Corpus scope | case/corpus planning docs; partial case rows | existing_but_incomplete | explicit owner-scoped selected/case corpus scope contract | corpus_scope_gate, owner_scope_gate |
| Evaluation fixtures | tests/fixtures, golden results | existing_but_incomplete | synthetic-by-default or owner/test-scoped real data with encryption | metadata_sensitivity_gate, regression_gate |

---

# Sensitive Field Families

Application/field-level encryption target fields include:

```text
TranscriptRow.raw_text
TurnRow.text
EvidenceQuoteRow.text
EvidenceQuoteRow.context_before
EvidenceQuoteRow.context_after
EvidenceQuoteRow.span_text
ModuleRunRow.raw_output
ModuleRunRow.parsed_output
SynthesisReportRow.report_json
FindingRow.title
FindingRow.summary
FindingRow.limitations_json
FindingAlternativeExplanationRow.text
ConstructRow.label
ConstructRow.description
ConstructRow.convergence_rationale_json
ConstructRelationshipRow.rationale
ConstructRelationshipRow.alternative_explanations_json
CaseRow.notes
SafetyEventRow.details_json
future ReflectionPoint / Hypothesis fields
future ExportArtifact content or storage references
future CorpusPatternAssessment summaries/rationales
```

Metadata requiring classification review:

```text
UserRow.email
TranscriptRow.title
TranscriptRow.session_label
TranscriptRow.session_date
SpeakerRow.display_name
CaseRow.title
SafetyEventRow.risk_level
SafetyEventRow.categories_json
AuthAuditEventRow.metadata_json
EvaluationRunRow.summary_json
```

---

# Owner Inheritance Target

Target inheritance should follow:

```text
owner -> transcript -> transcript version -> evidence quote -> finding/report/graph
owner -> case -> case evidence corpus -> longitudinal graph/report
owner -> source artifact -> transcription artifact -> transcript draft
owner -> export artifact -> retained export bytes/metadata
```

Child rows may either inherit owner through joins or carry denormalized owner fields, but implementation must define the authoritative parent.

---

# Decision

This matrix is ready to feed the 003-D work-package inventory, 003-E analysis validation planning, and 003-H exit review.
