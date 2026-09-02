# 003-D — Privacy Boundary / Encryption Baseline Implementation Plan

## Status

Complete.

This subgroup converts accepted privacy and encryption architecture into implementation-ready foundation plans.

It does not implement code, schema migrations, encryption, key management, route rewrites, auth changes, RBAC, log pipeline changes, export encryption, corpus enforcement, tests, deployment changes, or production data migrations.

---

# Purpose

003-D prepares privacy and encryption work so later implementation can protect recordings, transcripts, cases, reports, exports, graph objects, and corpus evidence before sensitive retained behavior expands.

It answers:

- Which privacy/security foundations already exist in the prototype?
- Which owner-scope gaps remain?
- How should legacy null-owner data be handled?
- Which sensitive routes and route surfaces need reconciliation?
- Which child artifacts must inherit owner scope?
- Which services may access decrypted content and for what purpose?
- What is the baseline infrastructure encryption posture?
- What is the target application/field-level encryption posture?
- How should logs, telemetry, audit events, lifecycle events, exports, and corpus reasoning be gated?

---

# Outputs

| Output | Document |
|---|---|
| Privacy boundary / encryption baseline implementation plan | `../architecture/003d_privacy_boundary_encryption_baseline_implementation_plan.md` |
| Privacy and encryption surface matrix | `../inventories/003d_privacy_encryption_surface_matrix.md` |
| Privacy and encryption work packages | `../inventories/003d_privacy_encryption_work_packages.md` |
| Encryption and access gate checklist | `../inventories/003d_encryption_and_access_gate_checklist.md` |

---

# Implementation Reference Reviewed

003-D reviewed the accepted Phase 002 privacy architecture, 003-C lifecycle planning, and current implementation references including:

```text
docs/planning/architecture/002d_privacy_boundary_encryption_architecture_plan.md
docs/planning/inventories/002d_artifact_privacy_encryption_matrix.md
docs/planning/architecture/003c_data_lifecycle_retention_foundation_implementation_plan.md
backend/api/deps.py
backend/api/middleware.py
backend/api/ownership.py
backend/api/routes/transcribe.py
backend/api/routes/transcripts.py
backend/api/routes/cases.py
backend/core/audit.py
backend/core/log_sanitize.py
backend/core/logging_config.py
backend/services/auth_service.py
backend/services/audio_service.py
backend/services/transcript_service.py
backend/db/models.py
backend/main.py
config/settings.py
docs/developer/log-redaction.md
```

---

# Current Baseline Findings

The prototype already has useful privacy foundations:

- passwordless email/session auth rows
- hashed login codes and session tokens
- login-code expiry, attempts, and request-rate limit controls
- API-key and session-based request gating
- owner helper functions for transcripts, cases, and workflow runs
- owner fields on several top-level sensitive rows
- audit event helper using sanitized extras
- log sanitizer deny-list for sensitive keys
- central redaction filter and structured log allowlist
- temporary audio upload cleanup
- settings for auth, cookies, redaction, retention, and cost-state operation

The prototype is not yet sufficient for the accepted privacy model because legacy null ownership is still allowed, older `/api` routes remain compatibility surfaces, sensitive child artifacts rely on implicit owner inheritance, retained sensitive fields are not yet application/field-level encrypted, lifecycle events need a strict allowlist, export privacy is not first-class, and corpus reasoning scope still needs enforcement.

---

# Accepted Decisions

## 1. Make privacy enforceable before expanding retained behavior

Corpus reasoning, retained reports, export retention, and automation should not expand until privacy boundaries are explicit and gateable.

## 2. Owner scope is a blocking foundation

Every retained sensitive artifact must have direct or inherited owner scope.

Legacy null-owner behavior is transitional debt, not the future model.

## 3. Future sensitive routes should converge on `/api/v1`

Legacy `/api` routes are compatibility/reference surfaces.

New sensitive retained behavior should use explicitly authenticated and owner-checked routes unless a compatibility plan says otherwise.

## 4. Owner inheritance must cover child artifacts

Transcript versions, speakers, turns, evidence quotes, runs, findings, hypotheses, reflection points, graph objects, reports, lifecycle events, exports, and corpus objects must have direct or inherited owner scope.

## 5. Service-purpose access must be explicit

Services should access decrypted sensitive content only for the active purpose and active scope.

Purge/deletion workers should prefer IDs, timestamps, lifecycle states, and storage references over content bodies.

## 6. Infrastructure encryption is baseline; field encryption is target maturity

Personal-mode retained use requires baseline infrastructure encryption verification.

The target maturity posture remains application/field-level encryption for retained sensitive content.

## 7. Logs, telemetry, and lifecycle events must be content-free by gate

Existing redaction helpers are useful, but later implementation must verify logs and lifecycle events by test and checklist, not convention.

## 8. Export privacy is a first-class boundary

Exports must be explicit, owner-scoped, version-bound, deletion-aware, encrypted if retained server-side, and distinct from downloaded user copies.

## 9. Corpus privacy must prevent hidden account-wide inference

Multi-transcript reasoning must use explicit owner-scoped selected transcript sets, Case Evidence Corpus scope, or future explicit corpus/workspace scope.

Hidden all-account inference remains blocked.

---

# Work Package Summary

003-D defines work packages for:

```text
PEB-WP-001 — Sensitive route and ownership audit
PEB-WP-002 — Legacy null-owner transition plan
PEB-WP-003 — Owner inheritance contract
PEB-WP-004 — Service-purpose access contract
PEB-WP-005 — Infrastructure encryption baseline verification
PEB-WP-006 — Log and telemetry redaction verification
PEB-WP-007 — Lifecycle event privacy allowlist
PEB-WP-008 — Field encryption target design
PEB-WP-009 — Sensitive metadata classification plan
PEB-WP-010 — SourceArtifact privacy and encryption plan
PEB-WP-011 — Export privacy and encryption plan
PEB-WP-012 — Corpus scope privacy enforcement plan
PEB-WP-013 — Privacy tests and fixtures
```

P2 decisions remain for future key hierarchy / enterprise readiness and advanced privacy controls.

---

# Gates Carried Forward

003-D carries forward these gates:

- privacy boundary gate
- owner scope gate
- legacy null-owner gate
- route compatibility gate
- owner inheritance gate
- service-purpose access gate
- encryption baseline gate
- field encryption target gate
- metadata sensitivity gate
- log redaction gate
- lifecycle event redaction gate
- export boundary gate
- corpus scope gate
- deletion cascade gate
- evaluation gate
- regression gate
- release readiness gate

---

# Handoff to 003-E

003-E should prepare analysis-boundary and validation implementation planning for:

- analysis scope owner checks
- transcript-version-bound evidence reads
- corpus scope enforcement
- prompt/context construction without logging sensitive content
- model-output validation without leaking raw completions
- hypothesis, safety, reflection-point, graph, and report outputs that inherit privacy and retention rules
- content-free validation events

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

# Exit Criteria

003-D is complete when:

- privacy/encryption implementation plan exists
- privacy/encryption surface matrix exists
- privacy/encryption work packages exist
- access/encryption gate checklist exists
- current implementation references are reviewed at planning level
- 003-E handoff is explicit
- Phase 003 indexes are updated
- broad implementation remains blocked

All criteria are satisfied.

---

# Next Phase

Proceed to:

```text
003-E — Analysis Boundary / Validation Implementation Plan
```
