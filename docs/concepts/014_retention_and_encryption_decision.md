# 014 — Retention and Encryption Decision

## Status

Accepted as the current retention and encryption decision for concept design and refactor planning.

This document closes the core privacy decisions needed before implementation refactoring.

---

# Decision Summary

The application should use a data-minimizing retention model and a phased encryption model.

## Retention Principle

```text
Audio is ephemeral.
Transcript drafts are temporary.
Saved transcripts are durable until deleted.
Case assignment implies durable longitudinal retention.
Derived analysis inherits the retention of its evidence basis.
```

## Encryption Principle

```text
Infrastructure encryption is required immediately.
Application-level encryption is the target for retained transcripts, transcript versions, evidence quotes, analysis outputs, reports, and cases.
```

---

# Retention Defaults

| Artifact | Default Retention | Decision |
|---|---:|---|
| Recording / audio upload | Delete after successful transcription | Ephemeral input only |
| Failed transcription audio | Short retry TTL, max 24 hours | Temporary retry artifact |
| Transcription provider output | Purge after transcript reconciliation | Intermediate artifact |
| Transcript draft | 7 days unless saved/promoted | Temporary working artifact |
| Saved transcript | Until user deletion | Durable reflection artifact |
| Transcript version | While dependent evidence/report/case exists | Evidence integrity artifact |
| Evidence quote | With transcript version/report dependency | Evidence artifact |
| Reflection run | With source transcript/report policy | Derived artifact |
| Finding / hypothesis / reflection point | With report/case/source policy | Derived artifact |
| Report | With retained source transcript/case | User-facing analysis view |
| Case | Until user deletion | Durable longitudinal artifact |
| Export | Download-only by default; server retention optional/explicit | Portable user artifact |
| Logs | Operational retention only; no content bodies | Operational artifact |

---

# Audio Retention Decision

Audio should not be retained long-term by default.

## Default

```text
Delete audio after successful transcription.
```

## Failure/Retry

If transcription fails, audio may be retained for retry/debug only within a short TTL.

Recommended maximum:

```text
24 hours
```

## Explicit Retention

Long-term audio retention is deferred and should not be enabled by default.

If added later, it must require a clear explicit user action.

---

# Transcript Retention Decision

Transcripts are the durable basis for reflection, but they should not become permanent silently.

## Draft Transcript

A draft transcript is temporary.

Recommended default:

```text
Expire after 7 days unless saved or assigned to a case.
```

## Saved Transcript

A saved transcript is durable until the user deletes it.

Saving a transcript means the user has chosen to preserve it for later reflection.

## Case Transcript

Assigning a transcript to a case implies durable retention.

Reason:

```text
Longitudinal analysis requires stable history.
```

Case assignment must be treated as a privacy-significant action.

---

# Analysis Output Retention Decision

Analysis outputs should not outlive their evidence basis.

Findings, hypotheses, reflection points, graph nodes, graph edges, synthesis, and reports inherit the retention policy of the transcript version or case that produced them.

If the transcript is deleted, dependent analysis artifacts should be deleted or rendered inaccessible according to deletion policy.

---

# Export Retention Decision

Exports should be deliberate and portable.

Default:

```text
Generate for download; do not retain long-term server-side unless explicitly configured.
```

If server-side export retention is supported later, exports require:

- owner scoping
- retention policy
- deletion path
- encryption
- audit event

---

# Encryption Target

## Phase 1 — Required Baseline

The application must use infrastructure-level protections:

- encrypted RDS storage
- encrypted S3 buckets
- encrypted Secrets Manager values
- TLS for user/API access where available
- least-privilege IAM
- redacted logs
- no transcript bodies in logs
- no prompt payloads in logs
- no raw model completions in ordinary logs

This is acceptable for early personal development, but it is not the mature target.

## Phase 2 — Target Personal-Use Maturity

Retained sensitive content should use application-level or field-level encryption.

Target encrypted fields include:

- transcript text
- transcript version text
- evidence quote text
- findings
- psychological hypotheses
- reflection points
- synthesis/report body
- case notes or longitudinal summaries

Metadata may remain queryable when needed, but metadata should be reviewed for sensitivity.

## Phase 3 — Future Enterprise Maturity

Future enterprise mode may add:

- customer-managed keys
- per-organization keys
- key rotation policy
- audit trails for decrypt access
- export encryption options
- workspace-level retention policies
- legal hold support, if appropriate

---

# Key Management Direction

Do not hard-code encryption secrets in application code or frontend bundles.

Recommended long-term direction:

```text
KMS-managed master key
→ envelope encryption data key
→ encrypted sensitive fields
```

Near-term implementation may begin with infrastructure encryption while the field-level encryption model is designed.

---

# Search and Analysis Tradeoff

Application-level encryption may reduce ordinary database search over transcript bodies.

This is acceptable.

The product should prefer privacy over casual full-text search in the personal-use phase.

Future options:

- decrypt-on-demand for owner session
- encrypted search index only if needed
- derived non-sensitive metadata
- local/session-only search over decrypted transcript

---

# Logs and Telemetry

Logs may include:

- IDs
- counts
- durations
- status
- error categories
- event names

Logs must not include:

- audio content
- transcript bodies
- evidence quote text
- prompt bodies
- raw model output
- login codes
- session tokens
- secrets

---

# Retention and Encryption Invariants

- Audio is ephemeral by default.
- Transcript retention requires user intent.
- Case assignment implies retention.
- Analysis output does not outlive its evidence basis.
- Reports identify transcript version.
- Exports are explicit.
- Retained sensitive content is encrypted at rest.
- Application-level encryption is the target for mature personal use.
- Enterprise encryption expands policy, not core concepts.

---

# Deferred Decisions

The following are deferred to implementation design:

- exact TTL durations by environment
- field encryption library
- KMS key naming
- migration strategy for existing plaintext rows
- whether unsaved draft transcripts can be analyzed
- whether analysis on unsaved drafts can be saved independently
- whether explicit audio save is ever supported
