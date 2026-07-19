# 001 — v2.1 Phase Sequence Overview

## Purpose

This document decomposes the v2.1 plan into smaller implementation phases.

The application has already completed much of the original post-v1 roadmap. The next work should make the core product tenets enforceable and prepare the app for controlled external usage.

**Active index:** [README.md](README.md) · **Readiness:** [../v2_readiness_assessment.md](../v2_readiness_assessment.md) · **Tenets:** [../../product/core_tenets.md](../../product/core_tenets.md)

---

# Core Product Direction

The application should remain market-agnostic for now.

Do not over-specialize for:

- clinicians
- couples
- enterprise
- mediation
- coaching
- research

Instead, strengthen the shared foundation:

```text
evidence traceability
confidence calibration
multi-lens analysis
non-diagnostic discipline
longitudinal case tracking
professional workflow fit
safety-aware framing
structured reasoning graph
```

---

# Phase Breakdown

| Phase | Document |
|-------|----------|
| **002** — Core Tenets and Governance | [002_v2_1_core_tenets_and_governance.md](002_v2_1_core_tenets_and_governance.md) |
| **003** — Simple Email Auth and Ownership | [003_v2_1_simple_email_auth_and_ownership.md](003_v2_1_simple_email_auth_and_ownership.md) |
| **004** — Evidence Precision | [004_v2_1_evidence_precision.md](004_v2_1_evidence_precision.md) |
| **005** — Evidence Snapshots and Versioning | [005_v2_1_evidence_snapshots_and_versioning.md](005_v2_1_evidence_snapshots_and_versioning.md) |
| **006** — Worker Atomicity and Operational Safety | [006_v2_1_worker_atomicity_and_operational_safety.md](006_v2_1_worker_atomicity_and_operational_safety.md) |
| **007** — Safety Policy and Non-Diagnostic Enforcement | [007_v2_1_safety_policy_and_non_diagnostic_enforcement.md](007_v2_1_safety_policy_and_non_diagnostic_enforcement.md) |
| **008** — Graph Relationship Evidence and Case Correctness | [008_v2_1_graph_relationship_evidence_and_case_correctness.md](008_v2_1_graph_relationship_evidence_and_case_correctness.md) |
| **009** — React API Contract and Release-Candidate Readiness | [009_v2_1_react_api_contract_and_release_candidate_readiness.md](009_v2_1_react_api_contract_and_release_candidate_readiness.md) |

Formalize product tenets and make them part of planning, PR review, evaluation, and architecture documentation → **002**.

Add early passwordless email login and basic resource ownership checks → **003**.

Make evidence snippets concise by default, with expandable context → **004**.

Ensure reports remain linked to the exact transcript/evidence version used during analysis → **005**.

Prevent duplicate job claiming and harden worker queue behavior → **006**.

Make safety-aware behavior configurable and enforce stricter non-diagnostic language → **007**.

Require graph edges to carry evidence/rationale and fix case/longitudinal evidence identity → **008**.

Move React toward generated API contracts and define v2 beta/release-candidate readiness gates → **009**.

---

# Dependency Map

```text
002 Core Tenets
  ↓
003 Auth/Ownership       004 Evidence Precision
  ↓                         ↓
005 Evidence Snapshots ←────┘
  ↓
006 Worker Atomicity
  ↓
007 Safety Policy
  ↓
008 Graph + Case Correctness
  ↓
009 React API Contract + RC Readiness
```

ALB React cutover, Cognito/SSO, split-turn, case package export, and ops drills are **out of this sequence** — see [../deferred_backlog.md](../deferred_backlog.md) (post-RC / GA).

---

# Recommended Release Labels

## Current

```text
post-v1 pre-production / v2 foundation
```

## After 002–005

```text
v2 beta foundation
```

## After 002–009

```text
v2 release candidate
```

## After external UAT and operational validation

```text
v2 GA
```

---

# Global Exit Criteria

The full v2.1 sequence is complete when:

- core tenets are formalized
- simple email login works
- ownership checks protect user resources
- evidence is concise by default
- reports are bound to transcript/evidence versions
- worker job claiming is atomic
- safety-aware mode is stricter and configurable
- graph relationships include evidence/rationale
- case/longitudinal evidence is transcript/version-scoped
- React uses generated or contract-checked API types
- release gates pass golden, safety, evidence, auth, and graph tests
