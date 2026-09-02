# 004-A Agent Rule Checklist

## Status

Accepted as the Phase 004-A agent and contributor checklist.

---

# Purpose

Define the minimum checks future agents and contributors must satisfy before and during Phase 004 implementation work.

This checklist is intentionally operational. It should be used by Codex, Cursor, AI assistants, human contributors, pull requests, and subgroup exit reviews.

---

# Pre-Work Checklist

Before changing implementation files, answer:

1. What Phase 004 subgroup am I executing?
2. Which Phase 003 work packages does this change execute?
3. Which gates apply?
4. Is the change allowed by the current subgroup?
5. Is the change additive/compatible, or does it require migration planning?
6. Could the change expose transcript, audio, prompt, report, export, token, code, secret, or raw model output content?
7. Could the change introduce diagnosis, treatment, adjudication, hidden-intent certainty, surveillance, or unsafe reconciliation pressure?
8. Could the change alter retention, deletion, export, corpus scope, owner scope, or job-safe shutdown behavior?
9. What tests or verification are required?
10. What work is explicitly deferred or not touched?

If any answer is unknown, pause and inspect the relevant Phase 003 plan and checklist before editing.

---

# Required Change Header

For every non-trivial implementation change, record:

```text
Phase 004 subgroup:
Phase 003 work packages executed:
Applicable gates:
Compatibility posture:
Migration posture:
Tests / verification:
Deferred or explicitly not touched:
```

---

# Scope Checks

## Documentation authority gate

- Does the change preserve `docs/concepts/` as top design authority?
- Does it avoid creating a new independent status source?
- Are living indexes updated if current phase/subgroup status changes?
- Are historical/reference docs preserved unless explicitly reconciled?

## Terminology drift gate

- Does product-facing language use accepted concepts?
- Is `Purposeful Audio Transcription` treated as historical repo shell?
- Is `RRE` treated as internal engine identity or shorthand, not sole product authority?
- Are workflow/module terms kept internal or deliberately aliased?

## Domain compatibility gate

- Are destructive class/table/API/route renames avoided unless explicitly authorized and migrated?
- Are aliases/adapters/additive contracts preferred first?
- Is legacy behavior preserved unless the subgroup explicitly changes it?

## Lifecycle/retention gate

- Does the change preserve audio-ephemeral, draft-temporary, saved/case-durable principles?
- Does it avoid expanding retention without visibility and deletion semantics?
- Are deletion cascade implications considered?

## Privacy/owner scope gate

- Does retained sensitive content have direct or inherited owner scope?
- Are legacy null-owner paths avoided or explicitly handled?
- Is service-purpose access limited?
- Are logs and events content-free?

## Analysis boundary gate

- Is AnalysisScope explicit or preserved?
- Is evidence linkage preserved?
- Are hypotheses bounded and non-diagnostic?
- Are support level and confidence kept distinct?
- Is safety posture respected?
- Are corpus claims scoped and lineage-bound?

## UI/report gate

- Does the UI/report surface show scope, evidence, uncertainty, safety, validation, retention, corpus, export, and cost-state semantics where relevant?
- Are recommendations/interventions avoided as default product-facing language?
- Are export/delete boundaries visible?

## Cost-state/job-safe shutdown gate

- Could the change create work that should block sleep?
- Does it require BlockingJobRecord or equivalent handling?
- Does shutdown remain safe, idempotent, and content-free?

## Evaluation/regression gate

- Are tests or verification recorded?
- Are boundary-failing cases considered, not only happy paths?
- Does the change preserve existing prototype behavior unless explicitly changed?

---

# Blockers Requiring Explicit Later Authorization

Do not proceed if the change requires any of these and the current subgroup has not authorized it:

- broad backend rewrite
- broad frontend rewrite
- destructive class/table/API/route rename
- production schema/data migration
- prompt replacement
- report renderer rewrite
- broad corpus expansion
- export expansion
- GitHub Actions restoration
- production cloud automation changes
- field-level encryption migration
- long-term retained audio
- enterprise org/workspace/RBAC/SSO/compliance/billing
- always-on enterprise availability

---

# Sensitive Content Checklist

Do not add or expose sensitive content in:

- application logs
- telemetry
- audit extras
- lifecycle events
- operational events
- worker status
- queue status
- power/cost-state status
- error messages
- debug UI
- test snapshots based on real content

Sensitive content includes:

```text
audio bodies
transcript bodies
evidence quote bodies beyond intended evidence UI
prompt payloads
raw completions
report bodies in operational logs
export contents in operational logs
secrets
session tokens
login codes
API keys
```

---

# Completion Checklist

A Phase 004 subgroup or implementation package may claim completion only when:

1. Scope is identified.
2. Phase 003 work packages are named.
3. Applicable gates are named and addressed.
4. Compatibility posture is explicit.
5. Migration posture is explicit.
6. Tests or verification are recorded.
7. Documentation updates are included when behavior, concepts, or status changes.
8. Deferred work is explicit.
9. Next subgroup or next package is named.
10. Broad rewrite remains blocked unless a later exit review explicitly changes that boundary.

---

# Decision

This checklist is mandatory for future Phase 004 implementation sessions.
