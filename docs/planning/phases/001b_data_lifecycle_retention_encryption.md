# Phase 001-B — Data Lifecycle, Retention, and Encryption Decisions

## Status

Completed for concept design.

This phase closes the core lifecycle, retention, and encryption decisions needed before implementation refactoring.

---

# Purpose

Phase 001-B defines what happens to sensitive conversation data over time.

It resolves the core tension identified in the concept foundation:

```text
Longitudinal reflection needs retained transcripts.
Privacy argues for deletion and minimization.
```

The phase determines which artifacts are ephemeral, which are durable, which inherit retention from other artifacts, and which require encryption.

---

# Scope

This phase covers:

- recording lifecycle
- transcription artifact lifecycle
- transcript draft lifecycle
- saved transcript lifecycle
- transcript version lifecycle
- evidence quote lifecycle
- reflection run lifecycle
- finding/hypothesis/reflection point lifecycle
- report lifecycle
- case lifecycle
- export lifecycle
- deletion semantics
- encryption posture
- logging boundaries

This phase does not implement these decisions in code.

---

# Decision Documents

| Document | Purpose |
|---|---|
| [../../concepts/013_data_lifecycle_decision.md](../../concepts/013_data_lifecycle_decision.md) | Defines artifact lifecycle and deletion semantics |
| [../../concepts/014_retention_and_encryption_decision.md](../../concepts/014_retention_and_encryption_decision.md) | Defines retention defaults and encryption posture |

---

# Decisions Closed

## 1. Audio Retention

Audio is ephemeral by default.

After successful transcription, audio should be deleted automatically.

Failed transcription audio may be retained only for a short retry/debug TTL, with a recommended maximum of 24 hours.

## 2. Transcript Draft Retention

Transcript drafts are temporary.

Recommended default:

```text
7 days unless saved or assigned to a case
```

## 3. Saved Transcript Retention

Saved transcripts are durable until user deletion.

Saving a transcript is a user intent signal.

## 4. Case Retention

Assigning a transcript to a case implies durable retention because longitudinal analysis requires stable history.

Case assignment is privacy-significant.

## 5. Analysis Output Retention

Findings, hypotheses, reflection points, graph nodes, graph edges, synthesis, and reports inherit the retention policy of their evidence basis.

Analysis output should not outlive its transcript version unless deliberately exported.

## 6. Export Retention

Exports are explicit user actions.

Default behavior should be download-oriented, not silent long-term server retention.

## 7. Encryption

Infrastructure encryption is required immediately.

Application-level or field-level encryption is the target for retained transcript text, evidence quote text, findings, hypotheses, reflection points, reports, and case summaries.

---

# Acceptance Criteria

This phase is complete when:

- audio retention is defined as ephemeral by default
- failed transcription audio has a short retry/debug TTL
- transcript drafts have an expiration model
- saved transcripts are durable by user intent
- case assignment implies longitudinal retention
- analysis output inherits source retention
- deletion semantics are defined
- exports are explicit and not silently retained
- infrastructure encryption is required immediately
- application-level encryption is identified as the mature target
- logs are prohibited from containing transcript, prompt, audio, evidence, or raw model bodies

---

# Result

Phase 001-B is accepted as concept-level closure.

The next recommended phase is:

```text
Phase 001-C — Hypothesis-Aware Reflection and Non-Diagnostic Boundary
```

That phase should close the rules around user-provided diagnoses, psychological hypotheses, therapeutic lens language, safety-aware overrides, and prohibited claims.
