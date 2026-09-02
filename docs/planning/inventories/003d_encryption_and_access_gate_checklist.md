# 003-D Encryption and Access Gate Checklist

## Status

Accepted as the Phase 003-D privacy, access, redaction, and encryption gate checklist.

---

# Purpose

Define the minimum questions later implementation must answer before privacy, owner-scope, logging, encryption, export, corpus, or sensitive-route changes are accepted.

This checklist is not code.

---

# Gate Principle

```text
A sensitive artifact is not safe merely because it exists in a personal deployment; it is safe only when owner scope, purpose-limited access, content-free telemetry, retention/deletion behavior, and encryption posture are explicit and tested.
```

---

# Universal Privacy Checklist

Every sensitive feature or artifact implementation must answer:

1. What sensitive artifact class is involved?
2. Who owns the artifact?
3. Is owner scope direct, inherited, or transitional-null?
4. Which route/service/worker may access it?
5. What purpose justifies access?
6. Does the operation require authentication?
7. Does the operation require an owner check?
8. Can admin/API-key bypass occur, and is it audited?
9. Is sensitive content ever logged?
10. Is sensitive metadata classified?
11. Is retained content encrypted at the required maturity level?
12. Does deletion or expiry remove, invalidate, or stale-mark dependent artifacts?
13. Does export create a separate privacy boundary?
14. Does corpus reasoning use only explicit selected/case scope?
15. Are tests defined for misuse or accidental leakage?

---

# Operation-Specific Checks

## Auth and sessions

Required checks:

- login codes are hashed and expire
- session tokens are hashed and expire
- session revocation is supported
- cookie security settings are deployment-mode appropriate
- login code and session token values never enter logs
- email addresses are classified as sensitive metadata

Blocking failure examples:

- login code logged or stored in plaintext after issuance
- session token logged, persisted raw, or returned in a place not intended for auth
- auth audit metadata stores avoidable sensitive free text

---

## Sensitive route access

Required checks:

- route sensitivity is classified
- sensitive route requires auth when deployed for retained personal use
- route enforces owner access for resource reads/writes
- route is either `/api/v1`-aligned or explicitly documented as legacy compatibility
- route does not expose transcript/case/report/export content through admin-only bypass by default

Blocking failure examples:

- legacy route exposes retained transcript content without owner check
- new sensitive feature is added only to unaudited legacy `/api` route
- admin/API-key path becomes ordinary user access pattern

---

## Owner inheritance

Required checks:

- every child artifact has an authoritative parent owner
- inherited ownership can be checked without exposing content
- direct owner fields, when added, are derived consistently
- null-owner rows are migration exceptions, not new default
- deletion/corpus behavior respects owner scope

Blocking failure examples:

- evidence quote or report can be fetched without checking the parent transcript owner
- corpus object combines transcripts owned by different users without explicit future multi-user policy
- new rows are created with null owner in retained sensitive workflows

---

## Service-purpose access

Required checks:

- service can access decrypted content only for the active purpose
- workers use IDs/metadata where content is unnecessary
- model-provider calls do not cause prompts/completions to enter logs
- export generation limits content access to generation window
- corpus service only accesses explicit selected/case scope

Blocking failure examples:

- purge worker reads transcript body when only IDs are needed
- failed model call logs prompt or completion body
- corpus job silently queries all retained transcripts

---

## Logging and telemetry

Required checks:

- log field allowlist is defined
- forbidden keys are denied/redacted
- long free-text messages are redacted or avoided
- exception logs do not include request bodies or transcript content
- auth/lifecycle/model/transcription/export events use IDs/status/counts only
- tests cover representative error paths

Blocking failure examples:

- transcript text, quote text, report JSON, prompt, raw completion, login code, session token, secret, or export body appears in logs
- metadata fields such as email/title/session label appear without classification decision

---

## Lifecycle events

Required checks:

- lifecycle event schema uses an allowlist
- reason fields are reason codes, not free-text content dumps
- lifecycle events do not contain audio/transcript/report/export bodies
- lifecycle events are operationally retained according to policy
- deletion and purge events are content-free but auditable

Blocking failure examples:

- delete event stores transcript title/body/quote text as explanation
- failed transcription event stores transcript content for debugging

---

## Encryption baseline

Required checks:

- database storage encryption is verified for deployed retained use
- object storage encryption is verified for uploads/exports when used
- secrets are stored in encrypted secret infrastructure
- TLS is used where available
- IAM/service permissions are least-privilege
- log storage access is restricted
- local/dev posture is clearly separate from deployed sensitive posture

Blocking failure examples:

- retained sensitive production data stored in unencrypted infrastructure
- object bucket permits broad public or cross-service access
- secrets copied into logs, files, or environment dumps

---

## Field encryption target

Required checks:

- sensitive field inventory is complete
- fields that must remain queryable are explicitly identified
- key hierarchy and envelope-encryption direction are documented
- encryption/decryption adapters are centralized
- migration is additive first
- rollback is possible until gate pass
- tests cover round-trip, wrong-key, missing-key, and redaction behavior

Blocking failure examples:

- transcript body remains plaintext in retained production store after field-encryption gate is declared passed
- encryption is scattered through services without consistent adapters
- key loss or rotation behavior is undefined

---

## Export privacy

Required checks:

- export is explicitly requested by user
- export source scope and transcript versions are recorded
- server-retained export content is encrypted
- export expiry/deletion path exists
- downloaded user copies are described as outside app boundary
- export lifecycle event excludes content

Blocking failure examples:

- export retained server-side silently
- export body or transcript excerpts written to logs/audit metadata
- exported report loses evidence/version lineage

---

## Corpus scope privacy

Required checks:

- corpus scope is explicit: selected transcript set, case evidence corpus, or future explicit corpus/workspace
- corpus scope is owner-scoped
- drafts/deleted/expired/stale/unbound artifacts are excluded from active corpus evidence
- corpus claims preserve transcript/version/evidence lineage
- cross-case inference requires future explicit policy

Blocking failure examples:

- analysis silently uses all retained account transcripts
- corpus claim uses deleted evidence
- case/corpus query crosses owner boundary

---

# Required Test Families

Later implementation should add tests for:

```text
sensitive_route_auth_required
transcript_owner_access_allowed
transcript_owner_access_denied
case_owner_access_denied
legacy_null_owner_transition
admin_bypass_audit
owner_inheritance_for_evidence_report_graph
log_redaction_transcript_prompt_report_secret
lifecycle_event_content_free
metadata_classification_email_title_speaker_case
service_purpose_access_denied
export_requires_owner_scope
server_retained_export_encrypted
corpus_scope_explicit
corpus_cross_owner_denied
field_encryption_round_trip
field_encryption_wrong_key
field_encryption_missing_key
```

---

# Decision

This checklist carries forward to later implementation phases as part of the privacy boundary gate, owner scope gate, service-purpose access gate, encryption baseline gate, field encryption target gate, log redaction gate, lifecycle event redaction gate, export boundary gate, corpus scope gate, and regression gate.
