# 005 — Security, Privacy, and Retention Concepts

## Purpose

Define security, privacy, and retention as product concepts rather than implementation details.

This application may process deeply personal recordings, therapy sessions, relationship conversations, and business meetings. Security is therefore part of the product’s meaning.

---

# Security Posture

## Principle

Sensitive conversation data is private by default, minimized by default, encrypted when retained, and never exposed through logs or accidental exports.

## Sensitive Data Types

- recordings
- audio staging objects
- transcripts
- transcript versions
- evidence quotes
- findings
- psychological hypotheses
- reflection points
- reports
- cases
- exports
- evaluation fixtures if derived from real data
- user identity/session metadata

---

# Recording Retention

Default:

```text
ephemeral
```

Recommended behavior:

- keep only long enough to transcribe
- delete after transcription success
- delete after failure unless needed for retry
- allow short TTL for retry/debug only
- explicit save required for long-term retention

---

# Transcript Retention

Recommended near-term default:

```text
transcripts are retained only when explicitly saved or assigned to a case
```

Alternative:

```text
transcripts are retained by default but can be deleted
```

This remains an open product question.

---

# Case Retention

Cases are durable by intent.

Assigning a transcript to a case should imply that the user wants longitudinal retention, subject to encryption and deletion controls.

---

# Encryption Concepts

## Baseline

Infrastructure encryption is expected:

- encrypted database storage
- encrypted object storage
- encrypted secrets
- TLS in transit where available

## Stronger Product Direction

For retained transcripts and reports, consider application-level encryption.

Potential model:

```text
owner key
→ encrypt transcript text
→ encrypt analysis output
→ decrypt only during authenticated session / analysis run
```

## Phased Approach

Phase 1:

- AWS/RDS/S3 encryption
- strict IAM
- redacted logs
- owner access control
- deletion workflows

Phase 2:

- application-level field encryption for transcript text and analysis outputs

Phase 3:

- customer-managed keys or enterprise key management

---

# Privacy Boundary

## Principle

Only the owner and authorized services should access sensitive content.

Near-term:

```text
single owner/admin
```

Future:

```text
organization
workspace
role
sharing grant
audit review
```

---

# Logs

Logs must never contain:

- transcript bodies
- audio content
- prompt payloads
- raw model completions
- secrets
- session tokens
- login codes

Logs may contain:

- request IDs
- workflow IDs
- module IDs
- counts
- durations
- status
- error categories

---

# Invariants

- Recordings are not retained silently.
- Retained transcripts are protected.
- Evidence must remain valid.
- Logs must be redacted.
- Ownership must be enforced.
- Exports must be explicit.
- Deletion must be meaningful.
- Longitudinal value must be opt-in or clearly disclosed.
