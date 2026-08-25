# 002-D Artifact Privacy and Encryption Matrix

## Status

Accepted as the Phase 002-D artifact privacy and encryption matrix.

---

# Purpose

Classify lifecycle artifacts by privacy sensitivity, owner scope, encryption target, logging restrictions, and corpus-use rules.

This matrix is governed by:

- `docs/concepts/005_security_privacy_retention_concepts.md`
- `docs/concepts/014_retention_and_encryption_decision.md`
- `docs/planning/architecture/002c_data_lifecycle_retention_architecture_plan.md`
- `docs/planning/architecture/002d_privacy_boundary_encryption_architecture_plan.md`

---

# Sensitivity Legend

| Level | Meaning |
|---|---|
| Very high | Direct conversation content, mental/relational analysis, or portable content export |
| High | Derived sensitive meaning, metadata that can reveal context, or operational linkage to sensitive artifacts |
| Medium | Operational metadata that may still reveal activity or timing |
| Low | Content-free operational counters/status only |

---

# Matrix

| Artifact | Sensitivity | Owner Scope | Encryption Target | Logging Rule | Corpus Use |
|---|---|---|---|---|---|
| Recording/audio upload | Very high | Direct owner scope | Encrypted temporary object storage; delete quickly | Never log content, filename text should be reviewed | Not used directly after transcription |
| Failed transcription audio | Very high | Direct owner scope | Encrypted temporary object storage; max retry/debug TTL | No content in logs | Not corpus-eligible |
| Transcription provider artifact | Very high if content-bearing | Owner via source artifact | Encrypted temporary storage; purge after reconciliation | Provider/job IDs only; no transcript bodies | Not corpus-eligible |
| Transcript draft | Very high | Owner via transcript | Application-level encryption target if persisted | No body text in logs | Not durable corpus evidence unless saved/promoted |
| Saved transcript | Very high | Direct owner scope | Application-level encryption target | IDs/counts/status only | Corpus-eligible only through explicit scope/case |
| Transcript version | Very high | Owner via transcript | Application-level encryption target | Version IDs only | Corpus-eligible as evidence basis |
| Speaker | High | Owner via transcript | Encrypt display names if sensitive | No names in logs unless sanitized | Corpus metadata; caution with identity labels |
| Turn | Very high | Owner via transcript version | Application-level encryption target | No turn text in logs | Corpus-eligible through transcript version |
| Evidence quote | Very high | Owner via transcript version | Application-level encryption target | No quote text in logs | Corpus-eligible; must preserve lineage |
| Reflection run / workflow run | High | Owner via source transcript/version | Sensitive fields encrypted; operational fields may remain queryable | Run IDs/status/durations only | May reference corpus scope but not contain all content unencrypted |
| Module/lens run | High | Owner via reflection run | Sensitive prompts/outputs encrypted or not persisted | No prompt bodies or raw completions | Lens output may feed corpus graph if retained |
| Finding | High to very high | Owner via evidence basis | Application-level encryption target | Finding text not logged | Corpus-eligible if evidence-linked |
| Psychological hypothesis | Very high | Owner via evidence basis | Application-level encryption target | No hypothesis text in logs | Corpus-eligible only as evidence-limited hypothesis |
| Reflection point | High to very high | Owner via finding/report | Application-level encryption target | No reflection text in logs | May summarize corpus evidence if lineage preserved |
| Reasoning graph node | High to very high | Owner via evidence basis/case | Application-level encryption target for labels/rationales | Node IDs/types only | Corpus graph object if scope explicit |
| Reasoning graph edge | High to very high | Owner via evidence basis/case | Application-level encryption target for rationale | Edge IDs/types only | Corpus graph object if evidence lineage preserved |
| Report | Very high | Owner via source transcript/version/case | Application-level encryption target | Report body never logged | May be transcript-level or corpus-level |
| Case | Very high | Direct owner scope | Encrypt notes/summaries; metadata sensitivity review | Case ID/status only | Primary near-term corpus boundary |
| Case evidence corpus | Very high | Owner via case | Application-level encryption target | Corpus IDs/counts only | Explicit multi-transcript reasoning boundary |
| Longitudinal/corpus summary | Very high | Owner via case/corpus | Application-level encryption target | Summary text never logged | Allowed only with evidence lineage |
| Export | Very high | Direct owner scope | Encrypt if retained server-side | Export ID/status only | May include transcript/corpus evidence; source versions required |
| Artifact lifecycle event | Medium | Owner or operational scope | Usually metadata only; review reason fields | No content bodies | May record corpus/staleness events without content |
| Logs/telemetry | Low only if content-free | Operational scope | Log storage encryption | No sensitive bodies | Not evidence source |
| Evaluation fixture from real data | Very high | Owner/test scope | Application-level encryption or synthetic-only preferred | No content in logs | Not production corpus unless explicitly imported as user data |

---

# Corpus Eligibility Rules

## Corpus-eligible artifacts

Only retained, owner-scoped, version-bound artifacts may become corpus evidence.

Eligible:

- saved transcript versions
- case transcript versions
- evidence quotes
- findings linked to evidence quotes
- hypotheses linked to evidence quotes
- graph nodes/edges linked to evidence quotes
- reports bound to transcript versions or case corpus

Not eligible by default:

- recordings/audio bytes
- failed transcription audio
- transcription provider artifacts
- expired drafts
- deleted transcript versions
- logs/telemetry
- unbound model outputs
- raw prompt/completion payloads

---

# Encryption Requirements by Maturity

## Baseline

Required before sensitive retained use:

- encrypted storage
- encrypted secrets
- TLS where available
- least-privilege IAM
- redacted logs
- no sensitive content in telemetry

## Target personal maturity

Application-level or field-level encryption for:

- transcript text
- transcript versions
- turn text
- evidence quotes
- findings
- hypotheses
- reflection points
- graph labels/rationales where sensitive
- report bodies
- case notes
- corpus summaries
- retained export content

## Future enterprise maturity

Future enterprise may add:

- organization/workspace key hierarchy
- customer-managed keys
- per-workspace retention policy
- decrypt-access audit
- export encryption options
- legal hold only if deliberately supported

---

# Logging Restrictions

The following must never be logged:

- audio content
- transcript bodies
- turn text
- evidence quote text
- finding body text
- hypothesis text
- reflection point text
- report body
- export content
- prompt payloads
- raw model completions
- login codes
- session tokens
- secrets

---

# 002-E Handoff

002-E should use this matrix to define analysis-output schemas and validators that prevent sensitive, diagnosis-like, or unsupported claims from leaking into logs, prompts, reports, exports, and corpus-level graph objects.
