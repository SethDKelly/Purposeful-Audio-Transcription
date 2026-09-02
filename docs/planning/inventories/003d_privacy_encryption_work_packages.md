# 003-D Privacy and Encryption Work Packages

## Status

Accepted as the Phase 003-D privacy/encryption implementation-planning work package inventory.

These packages are not implementation authorization.

---

# Purpose

Break privacy-boundary and encryption-baseline work into later implementation-ready packages.

Each package must be gated before code, schema, infrastructure, route, worker, export, corpus, or production data migration changes are accepted.

---

# Work Package Legend

| Field | Meaning |
|---|---|
| ID | Stable Phase 003-D work package identifier |
| Priority | P0, P1, or P2 |
| Target | Main implementation area later affected |
| Gate | Acceptance gate that must pass before implementation is accepted |

---

# P0 Work Packages

## PEB-WP-001 — Sensitive route and ownership audit

Priority: P0

Target:

```text
backend/api/routes/
backend/api/deps.py
backend/api/ownership.py
backend/main.py
```

Purpose:

Inventory every sensitive route and classify its auth, owner, admin bypass, legacy `/api` compatibility, and `/api/v1` readiness posture.

Required planning outcomes:

- route list by sensitivity
- route list by current auth behavior
- route list by owner-check behavior
- legacy `/api` route compatibility posture
- admin/API-key use constraints
- owner-check gaps for transcript/case/run/report/export/corpus resources

Gate:

```text
privacy_boundary_gate
owner_scope_gate
route_compatibility_gate
```

---

## PEB-WP-002 — Legacy null-owner transition plan

Priority: P0

Target:

```text
backend/api/deps.py
backend/db/models.py
backend/repositories/
future migration plan
```

Purpose:

Preserve compatibility with existing null-owner rows while preventing null-owner access from becoming the future privacy model.

Required planning outcomes:

- define where null-owner rows are allowed temporarily
- define owner backfill strategy
- define cutover point where new retained sensitive rows require owner scope
- define tests for non-owner access denial
- define admin/break-glass audit behavior

Gate:

```text
legacy_null_owner_gate
owner_scope_gate
regression_gate
```

---

## PEB-WP-003 — Owner inheritance contract

Priority: P0

Target:

```text
transcripts
transcript_versions
speakers
turns
evidence_quotes
workflow_runs
module_runs
findings
constructs
construct_relationships
synthesis_reports
cases
future source/export/lifecycle/corpus objects
```

Purpose:

Define authoritative parentage and inherited owner scope for every sensitive artifact.

Required planning outcomes:

- owner inheritance graph
- direct vs inherited owner-field decision
- cross-artifact join requirements
- access-check helper expansion plan
- deletion/corpus staleness owner-scope handling

Gate:

```text
owner_scope_gate
owner_inheritance_gate
deletion_cascade_gate
```

---

## PEB-WP-004 — Service-purpose access contract

Priority: P0

Target:

```text
transcription services
transcript services
analysis/workflow services
report/export services
retention/deletion workers
corpus/graph services
```

Purpose:

Specify which service can access decrypted sensitive content, for which purpose, under which scope.

Required planning outcomes:

- service-purpose matrix
- decrypted-content access limits
- ID/metadata-only worker rules
- model-provider prompt/log boundary
- export-generation access window
- corpus selected/case-scope rule

Gate:

```text
service_purpose_access_gate
privacy_boundary_gate
log_redaction_gate
```

---

## PEB-WP-005 — Infrastructure encryption baseline verification

Priority: P0

Target:

```text
AWS/database/object storage/secrets/TLS/IAM/deployment docs
```

Purpose:

Define the baseline controls required before retained sensitive use is considered acceptable in personal mode.

Required planning outcomes:

- database storage encryption verification
- object storage encryption verification
- secrets storage verification
- TLS route posture
- private networking / security group posture where practical
- least-privilege IAM review
- log storage access review

Gate:

```text
encryption_baseline_gate
privacy_boundary_gate
release_readiness_gate
```

---

## PEB-WP-006 — Log and telemetry redaction verification

Priority: P0

Target:

```text
backend/core/audit.py
backend/core/log_sanitize.py
backend/core/logging_config.py
backend/services/
backend/api/
tests/
```

Purpose:

Turn existing redaction support into a testable privacy gate across call sites.

Required planning outcomes:

- allowed log field list
- forbidden log field list
- scan of logging call sites
- request/error/auth/model/transcription/export/worker event coverage
- tests for sanitizer and representative failure paths
- policy for email and title metadata in logs

Gate:

```text
log_redaction_gate
metadata_sensitivity_gate
regression_gate
```

---

## PEB-WP-007 — Lifecycle event privacy allowlist

Priority: P0

Target:

```text
future ArtifactLifecycleEvent
AuthAuditEventRow usage
audit_event usage
retention/deletion workers
```

Purpose:

Ensure lifecycle/retention/deletion auditability without storing sensitive content in events.

Required planning outcomes:

- allowed event metadata fields
- forbidden event metadata fields
- reason-code vocabulary
- lifecycle event names
- owner/resource references
- operational retention posture

Gate:

```text
lifecycle_event_redaction_gate
metadata_sensitivity_gate
privacy_boundary_gate
```

---

# P1 Work Packages

## PEB-WP-008 — Field encryption target design

Priority: P1

Target:

```text
backend/db/models.py
future encryption adapters
future migrations
repositories/services
```

Purpose:

Plan application/field-level encryption for retained sensitive content.

Required planning outcomes:

- encrypted field inventory
- key hierarchy candidates
- envelope-encryption direction
- queryability tradeoffs
- encrypted-field adapter design
- additive migration strategy
- rollback plan
- round-trip tests

Gate:

```text
field_encryption_target_gate
regression_gate
release_readiness_gate
```

---

## PEB-WP-009 — Sensitive metadata classification plan

Priority: P1

Target:

```text
users
transcripts
cases
speakers
safety events
evaluation runs
audit metadata
UI/report handoff
```

Purpose:

Classify metadata that can reveal sensitive context even when it is not transcript body text.

Gate:

```text
metadata_sensitivity_gate
privacy_boundary_gate
ui_language_gate
```

---

## PEB-WP-010 — SourceArtifact privacy and encryption plan

Priority: P1

Target:

```text
future source artifact model
backend/services/audio_service.py
backend/api/routes/transcribe.py
object storage lifecycle
```

Purpose:

Plan privacy controls for ephemeral audio and failed-transcription debug/retry windows.

Gate:

```text
privacy_boundary_gate
encryption_baseline_gate
retention_gate
```

---

## PEB-WP-011 — Export privacy and encryption plan

Priority: P1

Target:

```text
future export service
future ExportArtifact
report services
UI/export flow
```

Purpose:

Make exports explicit, owner-scoped, version-bound, encrypted if retained server-side, deletion-aware, and user-visible.

Gate:

```text
export_boundary_gate
field_encryption_target_gate
retention_visibility_gate
```

---

## PEB-WP-012 — Corpus scope privacy enforcement plan

Priority: P1

Target:

```text
case service
corpus/graph services
analysis scope contracts
report services
```

Purpose:

Prevent hidden account-wide inference and enforce selected/case evidence scope for multi-transcript reasoning.

Gate:

```text
corpus_scope_gate
owner_scope_gate
analysis_boundary_gate
```

---

## PEB-WP-013 — Privacy tests and fixtures

Priority: P1

Target:

```text
tests/
evaluation fixtures
future regression gates
```

Purpose:

Define tests for auth/owner denial, null-owner behavior, route gating, log redaction, lifecycle event allowlists, encrypted-field round trips, export privacy, and corpus scope.

Gate:

```text
evaluation_gate
regression_gate
release_readiness_gate
```

---

# P2 Work Packages

## PEB-WP-014 — Future key hierarchy and enterprise readiness

Priority: P2

Target:

```text
future org/workspace/key architecture
```

Purpose:

Keep the encryption design compatible with future organization/workspace/customer-managed-key posture without adding enterprise complexity now.

Gate:

```text
field_encryption_target_gate
future_enterprise_gate
```

---

## PEB-WP-015 — Advanced privacy controls

Priority: P2

Target:

```text
future sharing/redaction/export settings
```

Purpose:

Consider future selective redaction, encrypted archives, and sharing grants only after baseline owner-scoped personal mode is safe.

Gate:

```text
privacy_boundary_gate
ui_language_gate
export_boundary_gate
```

---

# Dependency Order

Recommended order for later implementation:

```text
PEB-WP-001
PEB-WP-002
PEB-WP-003
PEB-WP-004
PEB-WP-005
PEB-WP-006
PEB-WP-007
PEB-WP-008 through PEB-WP-013
```

Do not expand corpus reasoning, report retention, export retention, or automation before PEB-WP-001 through PEB-WP-007 are planned and gated.

---

# Decision

These packages are ready to feed 003-E, 003-G, and the 003-H exit review.
