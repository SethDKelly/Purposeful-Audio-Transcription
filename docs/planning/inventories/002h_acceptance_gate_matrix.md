# 002-H Acceptance Gate Matrix

## Status

Accepted as the Phase 002-H acceptance gate matrix.

This matrix defines the gates that later implementation phases should satisfy before work is merged, released, or used as a new authority surface.

---

# Purpose

Make the Phase 002 architecture work enforceable.

The project should not rely only on intent or prompt instructions.

Implementation should be gated by documentation authority, domain alignment, retention, privacy, analysis boundaries, safety, corpus evidence, cost-state behavior, UI language, and evaluation coverage.

---

# Gate Matrix

| Gate | Purpose | Applies To | Pass Criteria | Critical Failure Examples |
|---|---|---|---|---|
| Documentation authority gate | Prevent stale docs from driving implementation | Docs, plans, README, phase indexes | Current authority surfaces point to accepted concepts and Phase 002 outputs | Old v2.1 phase or prototype docs presented as current authority |
| Terminology drift gate | Preserve accepted product language | Docs, UI, reports, APIs where user-facing | Uses Reflection Lens, Reflection Run, Reflection Point, Case Evidence Corpus, Cost State where appropriate | UI says clinical lens, diagnosis report, recommendation/intervention by default, or audio transcription app as product identity |
| Domain mapping gate | Keep implementation aligned with accepted concepts | Domain model, schemas, services | Existing useful entities retained and mapped; gaps tracked | Local schema work invents conflicting concept names or semantics |
| Retention gate | Ensure artifact lifecycle is explicit | Recording, drafts, transcripts, reports, cases, exports | Artifact has retention default, promotion trigger, expiration/delete path | Audio retained silently; drafts become durable without user intent |
| Deletion cascade gate | Ensure deletion is meaningful | Deletion services, UI, graph, reports | Dependent artifacts are deleted, invalidated, or marked stale according to policy | Deleted transcript still supports active corpus claim |
| Lifecycle event redaction gate | Keep lifecycle audit useful and safe | Events, logs, audit records | Events contain IDs/status/reasons but no sensitive content bodies | Lifecycle log stores transcript text, quote text, prompt, or model output |
| Privacy boundary gate | Enforce owner scope and service-purpose access | Data access, services, corpus, exports | Retained sensitive artifacts carry or inherit owner scope | Global unowned transcript/case/report data |
| Encryption baseline gate | Maintain required infrastructure protection | Storage, secrets, transport | Baseline encryption and secret handling are verified before expansion | New sensitive retention without encrypted storage or secret hygiene |
| Encryption target gate | Preserve mature field-level direction | Sensitive retained fields | Application/field-level encryption target is designed or tracked | Architecture assumes plaintext sensitive rows are the mature target |
| Log redaction gate | Prevent content leakage | App logs, worker logs, deployment logs | Logs are content-free and token/secret-free | Logs include transcript bodies, prompt payloads, evidence quotes, raw completions, or secrets |
| Export boundary gate | Keep exports explicit and bounded | Export generation and retention | Export has scope, owner, source version, retention, deletion, encryption posture | Export retained server-side silently or without version basis |
| Analysis boundary gate | Enforce evidence-limited reflection | Prompts, schemas, reports, graph | Output has evidence scope, version binding, evidence linkage, limitations | Claim appears without evidence or scope |
| Hypothesis boundary gate | Prevent diagnosis/label drift | Hypotheses, reports, prompts | Hypotheses include source, support level, evidence for/against, alternatives, limitations | Output says user has a disorder or diagnosis is confirmed |
| Confidence calibration gate | Match confidence to evidence and inference depth | Findings, hypotheses, corpus claims | Confidence and support levels reflect scope and evidence | High certainty about motive from ambiguous single quote |
| Safety override gate | Ensure safety posture modifies output | Safety detection, prompts, report rendering, UI | Elevated/high-risk posture changes framing and suppresses unsafe guidance | Threats treated as ordinary mutual communication problem |
| Safety mutualization gate | Prevent false equivalence | Safety-aware reports and reflection points | Output avoids unsupported equal-responsibility framing | Coercion/intimidation framed as both people need to communicate better |
| Corpus reasoning gate | Bound multi-transcript reasoning | Case/corpus analysis, graph, reports | Corpus scope explicit; claims cite versions and quote IDs; contradictions handled | Hidden account-wide analysis; recurrence claim from one transcript |
| Corpus staleness gate | Keep graph claims evidence-valid | Graph, corpus summaries, deletion | Deleted/stale evidence updates dependent graph objects | Unsupported corpus summary survives deletion unchanged |
| Reflection point gate | Keep guidance non-prescriptive | Reports, UI, prompts | Reflection points are evidence-linked, self-review oriented, safety-bounded | Treatment-like directive or unsafe confrontation prompt |
| Report scope gate | Make report basis visible | Report renderer, exports | Report shows scope, transcript versions, lenses, safety posture, limitations | Report hides whether it used one transcript or corpus |
| UI language gate | Keep UX within product boundary | Frontend, help text, button labels | UI uses accepted terminology and avoids authority drift | UI presents AI therapist, clinical assessment, or surveillance framing |
| Retention visibility gate | Make privacy-significant actions clear | Intake, save, case, delete, export flows | User sees retention/deletion/corpus implications before action | Case assignment looks like ordinary folder add with no retention warning |
| Cost state gate | Keep sleep/wake intentional and inspectable | Control plane, status API, UI | States are represented; wake/sleep/idle behavior is explicit | App appears broken when asleep or waking |
| Job-safe shutdown gate | Prevent shutdown corruption | Workers, jobs, control plane | Active blocking jobs prevent, delay, safe-cancel, or checkpoint shutdown | Shutdown kills report/export/deletion/encryption job unsafely |
| Workflow replacement gate | Avoid restoring stale deployment assumptions | CI/CD, cloud automation, scripts | New automation follows 002-F control-plane requirements | Deleted GitHub Actions restored without design review |
| Evaluation gate | Add fixtures for concept boundaries | Tests, evals, report outputs | Non-diagnostic, safety, corpus, retention, and language fixtures exist | No tests prevent diagnosis, unsafe advice, or corpus overreach |
| Regression gate | Preserve concept behavior over time | CI, manual checks, release review | Changes include relevant regression checks | Later change reintroduces old language or unsafe report behavior |
| Release readiness gate | Consolidate readiness before release | Phase exits, release candidates | Required gates pass or deferrals are explicit | Release proceeds with untracked P0 gate failures |

---

# Gate Ordering Recommendation

Implementation phases should apply gates in this rough order:

```text
1. Documentation authority
2. Terminology and domain mapping
3. Retention and deletion
4. Privacy, encryption, logs, and export
5. Analysis scope, hypothesis, safety, and corpus reasoning
6. Cost state and job-safe shutdown
7. UI/report language and visibility
8. Evaluation and regression
9. Release readiness
```

Reason:

Later UI/report polish should not occur before the underlying scope, evidence, privacy, and safety semantics are stable.

---

# Minimum P0 Gate Set for Phase 003

002-I should decide the exact Phase 003 scope, but the minimum P0 gates for any implementation-starting phase should include:

- documentation authority gate
- terminology drift gate
- domain mapping gate
- retention gate
- deletion cascade gate
- privacy boundary gate
- log redaction gate
- analysis boundary gate
- hypothesis boundary gate
- safety override gate
- corpus reasoning gate
- cost state gate
- job-safe shutdown gate
- workflow replacement gate
- evaluation gate

---

# Gate Failure Handling

When a gate fails, later implementation phases should classify the failure as:

| Severity | Meaning | Required Response |
|---|---|---|
| Critical | Violates safety, privacy, diagnostic, deletion, or evidence basis | Block merge/release until resolved |
| Major | Causes product authority drift or user-facing misunderstanding | Fix before release or explicitly defer with owner acceptance |
| Minor | Documentation/copy/detail mismatch without immediate safety/privacy impact | Track and resolve before phase exit |

---

# Critical Failure Examples

Critical failures include:

1. Diagnosing or labeling a participant.
2. Confirming a user-provided diagnosis from transcript evidence.
3. Treating direct threats or coercion as ordinary communication difficulty.
4. Suggesting reconciliation/confrontation in high-risk safety contexts.
5. Using hidden account-wide corpus inference.
6. Making corpus claims without transcript version and quote lineage.
7. Retaining audio or drafts silently.
8. Logging sensitive content, prompts, completions, secrets, or tokens.
9. Leaving deleted evidence as active support for graph claims.
10. Shutting down in a way that corrupts active jobs.
11. Restoring deployment workflows without new cost-state/control-plane design.

---

# Decision

Phase 002 has enough architecture material to define acceptance gates for later implementation.

002-I should use this matrix to decide whether Phase 003 may begin and which gates are mandatory for that phase.