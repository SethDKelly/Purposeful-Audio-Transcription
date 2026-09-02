# 003-H Phase 004 Authorized Scope

## Status

Accepted as the Phase 003 exit-review authorization for Phase 004.

---

# Authorization Decision

Phase 004 is authorized as:

```text
Phase 004 — Controlled Foundation Refactor Implementation
```

Phase 004 may begin controlled implementation work.

It may not begin a broad rewrite.

---

# Authorization Boundary

Phase 004 is authorized to implement foundation changes that execute accepted Phase 003 work packages in dependency order.

Every implementation subgroup must identify:

1. the Phase 003 work packages being executed
2. the gates that apply
3. the compatibility posture
4. the tests or verification needed
5. any migration posture
6. any deferred decisions
7. the subgroup exit result

Implementation should remain incremental, reversible where practical, and protective of existing prototype behavior unless a change is explicitly accepted.

---

# Recommended Phase 004 Division

| Subphase | Status | Purpose |
|---|---|---|
| 004-A — Implementation Authority Lock, Agent Rules, and Documentation Guardrails | Next | Install contributor/agent guardrails before code implementation begins |
| 004-B — Domain Terminology Compatibility and Concept Contract Implementation | Planned | Add aliases/contracts/DTO posture for accepted domain language without destructive rename-first refactor |
| 004-C — Lifecycle, Retention, SourceArtifact, and Deletion-Cascade Foundation | Planned | Implement lifecycle/retention foundations and deletion cascade contracts incrementally |
| 004-D — Privacy Boundary, Owner Scope, Route, Redaction, and Encryption Baseline | Planned | Harden owner scope, route access, redaction, lifecycle events, and baseline encryption verification |
| 004-E — AnalysisScope, ValidationResult, SafetyPosture, Hypothesis, and Corpus Gates | Planned | Implement analysis-boundary contracts and validators before expanding reports/corpus/export behavior |
| 004-F — Cost-State Control Plane, Blocking Jobs, Idle, Wake, and Shutdown Safety | Planned | Implement or reconcile control-plane contracts and job-safe shutdown behavior |
| 004-G — UI/Report Alignment, Scope Display, Export/Delete Previews, and Status Surfaces | Planned | Align user-facing surfaces after supporting contracts/gates exist |
| 004-H — Evaluation, Regression, Release Readiness, and Implementation Backlog Closure | Planned | Consolidate tests, regressions, release gates, and implementation backlog status |
| 004-I — Phase 004 Exit Review and Consolidation | Mandatory gate | Decide whether implementation phase passes and whether another phase is authorized |

---

# Required First Step

Proceed first to:

```text
004-A — Implementation Authority Lock, Agent Rules, and Documentation Guardrails
```

004-A is required before implementation because the repository needs clear contributor and agent instructions that prevent future work from bypassing Phase 003 gates.

---

# Phase 004 Allowed Work

Phase 004 may implement or prepare implementation for:

- documentation authority guardrails
- contributor / Cursor / Codex / agent guidance
- concept-to-code mapping references
- domain terminology compatibility aliases and contracts
- lifecycle state and retention foundations
- SourceArtifact / RecordingArtifact equivalent planning-to-code bridge
- RetentionRule equivalent planning-to-code bridge
- deletion cascade contract implementation
- owner scope hardening
- route compatibility cleanup
- redaction and content-free event verification
- infrastructure encryption baseline verification
- field-encryption target design artifacts, if migration-safe
- AnalysisScope / ReportScope / ValidationResult foundations
- ReflectionLensContract compatibility layer
- SafetyPosture structure
- PsychologicalHypothesis and HypothesisSupportAssessment structure
- ReflectionPoint compatibility migration
- CorpusPatternAssessment and corpus staleness gates
- cost-state vocabulary reconciliation
- CostStateRecord / BlockingJobRecord equivalent contracts
- idle evaluator and shutdown preflight foundations
- UI/report scope, evidence, safety, corpus, export, deletion, and cost-state display planning-to-code bridges
- acceptance tests and regression gates tied to the above

---

# Phase 004 Blocked Work

The following remain blocked unless specifically authorized by a Phase 004 subgroup and gated:

- wholesale backend rewrite
- wholesale frontend rewrite
- destructive class/table renames without compatibility and migration plan
- production data migration execution without explicit migration gate
- production cloud changes without control-plane/shutdown gates
- GitHub Actions restoration without cost-state, privacy, job-safety, and release-readiness gates
- prompt replacement without analysis validation gates
- report renderer replacement without ReportScope and validation gates
- broad corpus expansion without privacy/retention/scope/staleness gates
- export expansion without export-readiness/privacy gates
- long-term retained audio behavior
- enterprise org/workspace/RBAC/SSO/compliance/billing features
- always-on enterprise availability
- advanced corpus visualization before corpus semantics and UI gates pass

---

# Phase 004 Gate Requirements

Phase 004 subgroups must carry forward the gates from 003-H, including:

```text
documentation authority gate
terminology drift gate
domain compatibility gate
retention gate
deletion cascade gate
privacy boundary gate
owner scope gate
owner inheritance gate
service-purpose access gate
encryption baseline gate
log redaction gate
analysis scope gate
evidence linkage gate
hypothesis boundary gate
safety posture gate
reflection point gate
corpus scope gate
corpus staleness gate
report scope gate
export readiness gate
cost state contract gate
blocking job registry gate
job-safe shutdown gate
UI terminology gate
case evidence corpus gate
evaluation gate
regression gate
release readiness gate
```

A subgroup may not claim completion if its applicable gates are not addressed.

---

# Recommended Dependency Order

Phase 004 should proceed in this dependency order unless a later accepted subgroup changes it:

```text
1. Authority / guardrails
2. Domain compatibility / contracts
3. Lifecycle / retention / deletion foundations
4. Privacy / owner scope / redaction / encryption baseline
5. Analysis / validation / safety / corpus contracts
6. Cost-state / control-plane / blocking jobs / shutdown safety
7. UI/report alignment over stable contracts
8. Evaluation / regression / release readiness
9. Phase 004 exit review
```

Reason:

User-facing and automation changes are safer after domain, lifecycle, privacy, analysis, and cost-state contracts exist.

---

# Phase 004 Success Criteria

Phase 004 succeeds only if:

- implementation guardrails exist and are followed
- accepted concepts map to code through documented contracts
- legacy terminology is either reconciled, aliased, or explicitly isolated
- lifecycle and retention behavior becomes more enforceable
- privacy/owner scope/redaction baseline is stronger
- analysis validation boundaries are more enforceable than prompt-only rules
- cost-state/control-plane behavior is safer and more explicit
- UI/report surfaces align with scope/evidence/safety/retention/corpus/cost-state semantics
- tests and regression gates exist for critical boundaries
- the 004-I exit review consolidates what was actually implemented, deferred, or blocked

---

# Decision

Phase 004 is authorized with controlled foundation implementation scope.

Proceed next to:

```text
004-A — Implementation Authority Lock, Agent Rules, and Documentation Guardrails
```
