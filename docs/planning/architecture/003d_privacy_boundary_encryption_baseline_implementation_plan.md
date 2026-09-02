# 003-D Privacy Boundary / Encryption Baseline Implementation Plan

## Status

Accepted as the Phase 003-D privacy boundary and encryption baseline implementation plan.

This document converts the accepted Phase 002 privacy/encryption architecture into implementation-ready work packages and gates.

It does not implement code changes, schema migrations, encryption code, key management infrastructure, auth changes, RBAC, log pipeline changes, export encryption, deployment changes, or production data migrations by itself.

---

# Purpose

Prepare privacy and encryption implementation work so retained conversation artifacts can be protected before corpus reasoning, report retention, export handling, and broader automation expand.

003-D turns the accepted privacy architecture into staged implementation planning for:

- owner scope and access control
- service-purpose access boundaries
- sensitive artifact classification
- application/field-level encryption target design
- key-management readiness
- log and telemetry redaction verification
- lifecycle event privacy
- export privacy and encryption
- corpus reasoning privacy boundaries
- test and acceptance gates

---

# Governing Inputs

Primary authority:

- `docs/concepts/005_security_privacy_retention_concepts.md`
- `docs/concepts/014_retention_and_encryption_decision.md`
- `docs/planning/architecture/002d_privacy_boundary_encryption_architecture_plan.md`
- `docs/planning/inventories/002d_artifact_privacy_encryption_matrix.md`
- `docs/planning/inventories/002d_corpus_reasoning_scope_rules.md`
- `docs/planning/architecture/003c_data_lifecycle_retention_foundation_implementation_plan.md`
- `docs/planning/inventories/003c_lifecycle_artifact_implementation_matrix.md`
- `docs/planning/inventories/003c_deletion_cascade_gate_checklist.md`

Implementation reference inspected:

- `backend/api/deps.py`
- `backend/api/middleware.py`
- `backend/api/ownership.py`
- `backend/api/routes/transcribe.py`
- `backend/api/routes/transcripts.py`
- `backend/api/routes/cases.py`
- `backend/core/audit.py`
- `backend/core/log_sanitize.py`
- `backend/core/logging_config.py`
- `backend/services/auth_service.py`
- `backend/services/audio_service.py`
- `backend/services/transcript_service.py`
- `backend/db/models.py`
- `backend/main.py`
- `config/settings.py`
- `docs/developer/log-redaction.md`

---

# Accepted Privacy Principle

```text
Sensitive conversation data is private by default, owner-scoped, minimized by default, encrypted when retained, never exposed through logs, and never used outside the user's explicit retained/case/corpus scope.
```

---

# Current Implementation Baseline

The prototype already contains useful privacy and security foundations:

1. Passwordless email login and session rows exist.
2. Login codes and session tokens are hashed before storage.
3. Login codes have expiration, attempt count, and request-rate limits.
4. Session cookies can satisfy the API gate when session auth is required.
5. API key access exists as an admin/break-glass path.
6. Middleware gates non-public `/api/v1` routes when API-key or session auth is enabled.
7. Ownership helper functions exist for transcripts, cases, and workflow runs.
8. Database rows include owner fields for users, transcripts, cases, workflow runs, finding feedback, and evaluation runs.
9. Audit events and structured logs have existing content-redaction helpers.
10. The log sanitizer denies common sensitive keys such as transcript, prompt, raw output, parsed output, report JSON, API keys, secrets, passwords, and tokens.
11. Logging has a central redaction filter and a JSON formatter with an allowlisted extra-field set.
12. Audio upload handling uses a temporary file context that removes the local file after transcription.
13. Settings already contain auth, session, cookie, logging, redaction, retention, and cost-state controls.

The baseline is useful, but incomplete for the accepted privacy model.

Current gaps and risks:

- legacy null ownership is still allowed and must not become the future privacy norm
- older `/api` routes may bypass the intended `/api/v1` ownership/resource-access pattern
- several sensitive child artifacts inherit owner only indirectly and need explicit inheritance rules
- sensitive database fields are not yet application/field-level encrypted
- `raw_output`, `parsed_output`, `report_json`, finding summaries, case notes, graph rationales, and evidence text remain sensitive retained fields
- email addresses and case/transcript titles are sensitive metadata and need a metadata-classification posture
- log redaction has helper/filter support but still needs a verification gate across all logging call sites
- lifecycle events need an allowlist so retention/deletion events cannot include content
- service-purpose access is not yet formally represented
- export artifacts do not yet have explicit privacy/encryption lifecycle semantics
- corpus reasoning needs enforcement that selected/case scope is explicit and owner-scoped

---

# Accepted Implementation Principle

```text
Make privacy boundaries enforceable before expanding retained corpus reasoning, report materialization, export retention, or automation.
```

Privacy cannot rely only on developer discipline, prompt wording, or the fact that the near-term deployment is personal use.

---

# Implementation Planning Decisions

## 1. Owner scope must be treated as a blocking foundation

Every retained sensitive artifact must have direct or inherited owner scope.

Near-term personal mode may use one owner/operator, but implementation should not depend on globally accessible rows.

Legacy `owner_user_id = null` compatibility may remain temporarily for migration, but it should be treated as transitional debt with explicit gates.

## 2. `/api/v1` should become the privacy-boundary route surface

Existing legacy `/api` routes are valuable compatibility surfaces, but future sensitive operations should converge on an explicitly authenticated and owner-checked `/api/v1` route pattern.

Do not expand sensitive behavior on legacy routes without an explicit compatibility and ownership plan.

## 3. Child artifacts must inherit owner scope from their evidence basis

Speakers, turns, transcript versions, evidence quotes, reflection runs, lens/module runs, findings, hypotheses, reflection points, graph objects, reports, lifecycle events, and exports should inherit owner scope from transcript, case, or explicit export parentage.

Where performance requires direct owner fields, those fields should be additive and derived from the authoritative parent.

## 4. Service-purpose access should become an explicit contract

A service may access decrypted sensitive content only for the active user-initiated or policy-authorized purpose.

Examples:

- transcription may access staged audio only during transcription
- transcript services may access text for parse/review/save/delete
- analysis workers may access selected transcript versions only for a scoped reflection run
- corpus services may access only selected/case corpus evidence
- export services may access report/source evidence only during export generation
- purge/deletion workers should use IDs, state, timestamps, and storage references rather than content bodies whenever possible

## 5. Infrastructure encryption is baseline; field encryption is target maturity

Baseline implementation readiness requires verifying encrypted database/object/secrets storage and TLS where applicable.

Target maturity requires application-level or field-level encryption for retained sensitive content.

003-D does not decide exact libraries, key providers, or migration commands. It defines the required planning shape and gates.

## 6. Encryption design should be additive and reversible at the planning stage

Later implementation should prefer additive encrypted columns, wrappers, or field adapters before destructive replacement.

Migration should preserve rollback options until the field-encryption gate and regression gate pass.

## 7. Logs and telemetry must be content-free by test, not convention

Existing redaction helpers are useful, but the accepted privacy model requires verification that all log and audit paths exclude transcript bodies, quote text, prompt payloads, raw model completions, report bodies, export content, login codes, session tokens, secrets, and sensitive free-text notes.

## 8. Lifecycle events need a strict metadata allowlist

Lifecycle events should record state transitions without content.

Allowed metadata should be limited to artifact IDs, owner IDs or pseudonymous owner IDs, artifact class, event name, previous/new state, reason code, timestamps, counts, durations, and non-sensitive status.

## 9. Export privacy is a first-class boundary

Exports are explicit portable user artifacts.

Server-retained exports, if supported, must be owner-scoped, encrypted, version-bound, deletion-aware, and governed by an export retention rule.

Downloaded user copies are outside the application boundary and should be described that way in UI/report planning.

## 10. Corpus privacy must prevent hidden account-wide inference

Corpus reasoning may use multiple transcripts only through explicit owner-scoped selected transcript sets, case evidence corpus scope, or a future explicit corpus/workspace scope.

The implementation plan must prevent hidden all-account inference, cross-case inference without confirmation, and use of drafts/deleted/stale/unbound artifacts as active corpus evidence.

---

# Proposed Implementation Sequence

## Stage 0 — Privacy authority lock

Create or update implementation-facing notes that point developers to the current privacy authority documents.

No runtime behavior changes yet.

## Stage 1 — Owner-scope route audit

Inventory sensitive routes, DTOs, services, and repositories by whether they require authentication, owner checks, admin bypass, and null-owner handling.

## Stage 2 — Owner inheritance contract

Define parent/child owner inheritance rules across transcript, version, evidence, case, report, graph, lifecycle event, and export objects.

## Stage 3 — Service-purpose access plan

Define which services may read decrypted content, for what purpose, under which scope, and which services must operate only on IDs/metadata.

## Stage 4 — Encryption baseline verification plan

Document the baseline infrastructure controls that must be true for personal-mode retained use.

This includes database storage, object storage, secrets, TLS, IAM, private networking where practical, and log storage controls.

## Stage 5 — Field encryption target design

Plan encrypted-field adapters, key hierarchy, field classification, query constraints, migration strategy, rollback path, and tests.

## Stage 6 — Redaction verification plan

Define a testable log/audit/event redaction gate across request errors, auth events, lifecycle events, worker logs, model provider errors, transcription errors, export errors, and report generation errors.

## Stage 7 — Export/corpus privacy plan

Define export encryption posture and corpus scope enforcement before expanding export retention or multi-transcript reasoning.

## Stage 8 — Test/evaluation plan

Define tests for owner access, null-owner behavior, redaction, field-classification coverage, encrypted-field round trips, lifecycle event allowlists, export protection, and corpus scope boundaries.

---

# Required Gates

003-D carries forward or introduces these gates for later implementation:

- privacy boundary gate
- owner scope gate
- legacy null-owner gate
- route compatibility gate
- service-purpose access gate
- encryption baseline gate
- field encryption target gate
- metadata sensitivity gate
- log redaction gate
- lifecycle event redaction gate
- export boundary gate
- corpus scope gate
- deletion cascade gate
- regression gate

---

# Handoff to 003-E

003-E should use this plan to prepare analysis-boundary and validation implementation planning for:

- analysis scope owner checks
- transcript-version-bound evidence reads
- corpus scope enforcement
- prompt/context construction without logging sensitive content
- model-output validation without leaking raw completions
- hypothesis, safety, reflection-point, graph, and report outputs that inherit privacy and retention rules
- validation events that are content-free

---

# Non-goals

003-D does not implement:

- auth changes
- route rewrites
- schema migrations
- owner backfill
- encryption code
- KMS/key infrastructure
- log pipeline changes
- report/export encryption
- corpus query enforcement
- privacy tests
- production data migration
- GitHub Actions restoration

---

# Acceptance Result

The privacy boundary and encryption baseline implementation plan is ready to feed 003-E and the Phase 003 exit review.

Proceed next to:

```text
003-E — Analysis Boundary / Validation Implementation Plan
```
