# 00 — Unified Roadmap Overview

## Purpose

This document defines the unified roadmap from the current v1 architecture toward a durable v2 Relationship Reasoning Engine.

It consolidates the prior recommendations around fixing current v1 shortcomings, hardening deployment and operations, improving test/evaluation quality, adding safety red-team coverage, preparing for React, expanding case and longitudinal workflows, and developing a future v2 product architecture.

---

# Current State Assessment

Post-**v1.0.0**, the program completed **v1.1–v1.4** and a **v2.0 foundation** slice (archived Phases **50–54**).

In place today:

- UI/API/worker (+ provisioned React web) container split
- DAG-style workflow execution and durable jobs
- Module / workflow / ontology registries
- Structured findings, constructs, relationships, graph merge, convergence
- Golden + safety eval harnesses and CI release gates
- `/api/v1` product API with OpenAPI snapshots
- React product shell (`frontend-react/`) for core and expanded flows
- Streamlit role: admin/eval (ALB still Streamlit-default until cutover)
- SafetyEvent / EvaluationRun persistence; server report packages
- Auth/RBAC **plan** (implementation outstanding)
- Supply-chain + data-governance documentation

**Active next band:** [10_v2_1_cutover_auth_and_graph_depth.md](10_v2_1_cutover_auth_and_graph_depth.md) — live React cutover, Cognito/auth MVP, deeper graph/case work, ops drills.

Avoid expanding analytical module breadth; prefer cutover, auth, evidence/graph depth, and platform maturity.

---

# Roadmap Philosophy

## Do Not Big-Bang Rewrite

The roadmap should be evolutionary.

Prefer:

```text
stabilize existing architecture
→ harden contracts
→ add quality gates
→ migrate UI gradually
→ deepen product workflows
```

Avoid:

```text
rewrite everything in React immediately
replace Streamlit before API contracts stabilize
add more modules before evaluation exists
expand product surface before worker reliability
```

---

# Phase Summary

## v1.1 — Operational Hardening

Primary goal: make the existing system reliable, deployable, secure at the service boundary, and operationally observable.

Focus:

- test invocation and repo hygiene
- stale docs cleanup
- service-specific IAM
- selective deploys
- worker queue/backpressure
- health checks and alarms
- deployment smoke tests
- Streamlit/API boundary cleanup

## v1.2 — Evaluation, Safety, API Contracts, React Readiness

Primary goal: make the system measurable, safer, and ready for a future React client.

Focus:

- golden evaluation harness
- safety red-team fixtures
- forbidden-claim scoring
- prompt/module version comparisons
- API v1 contract stabilization
- OpenAPI checks
- frontend DTOs
- Streamlit as API-only client
- React architecture decisions

## v1.3 — React MVP and Product Depth

Primary goal: introduce React as the primary user-facing product shell while keeping Streamlit as an internal/admin/eval tool.

Focus:

- Vite + React + TypeScript app
- generated API client
- transcript upload/prep
- workflow launcher and progress
- report summary
- evidence-linked finding cards
- basic export
- case model v2
- human feedback workflow
- long-transcript chunking foundation

## v1.4 — Platform Maturity and React Expansion

Primary goal: mature React into the primary product UI and harden the platform for broader usage.

Focus:

- graph exploration
- longitudinal case dashboard
- report package viewer
- finding review workflow
- module lifecycle UI
- auth/RBAC planning or implementation
- supply-chain hardening
- backup/restore drills
- observability maturity

## v2.0 — Future State Architecture

Primary goal: establish the Relationship Reasoning Engine as a platform with durable knowledge architecture, multi-user workflows, professional-grade reporting, and extensible modules.

Focus:

- React primary UI
- Streamlit retired or admin-only
- API/worker platform maturity
- robust ontology/graph reasoning
- case longitudinal analysis
- module lifecycle management
- evaluation release gates
- safety governance
- professional workflows
- scalable deployment model

---

# Cross-Cutting Priorities

## 1. Evidence Traceability

Every important claim should maintain:

```text
claim
→ quote IDs
→ evidence relevance
→ confidence
→ module source
→ alternatives/limitations
```

## 2. Confidence Calibration

The system must not overstate diagnoses, abuse determinations, manipulation intent, personality traits, attachment styles, trauma history, or relationship prognosis.

## 3. API Stability

React success depends on stable API contracts. API contracts should be treated as product interfaces, not internal implementation details.

## 4. Evaluation Before Expansion

Do not expand modules, workflows, or clinical language without evaluation coverage.

## 5. Safety-Aware UX

Safety concerns should shift product framing away from mutual communication coaching and toward cautious, evidence-limited reflection and external support.

## 6. Streamlit Role Transition

Streamlit should gradually move from primary product UI to dev console, eval review console, admin tool, or debugging interface.

---

# Suggested Phase Order

```text
v1.1 Operational hardening          ✓ Phase 50
  ↓
v1.2 Evaluation + API + React readiness ✓ Phase 51
  ↓
v1.3 React MVP + product depth      ✓ Phase 52
  ↓
v1.4 Platform maturity + React expansion ✓ Phase 53
  ↓
v2.0 Foundation (readiness slice)   ✓ Phase 54
  ↓
v2.1 Cutover + auth + graph depth   ← active (Phase 55 when done)
  ↓
v2.x Full platform maturity         (vision: 05)
```

---

# Non-Goals for Immediate Next Work

Do not prioritize adding many new analysis modules, rewriting backend architecture from scratch, marketing/public launch before auth and safety maturity, or building multi-user collaboration before Cognito (v2.1).

---

# Doc map (canonical)

| Need | Path |
|------|------|
| This overview | `docs/planning/phases/00_unified_roadmap_overview.md` |
| Active phase work | `docs/planning/phases/10` (then `05` vision) |
| Deferred (priority) | `docs/planning/deferred_backlog.md` |
| Unprioritized ideas | `docs/planning/general_backlog.md` |
| Completed Phases 1–54 | `docs/archived/planning/phases.md` |
| AWS architecture | `docs/developer/aws-deployment.md` |

When v2.1 ships, append archived **Phase 55**.
