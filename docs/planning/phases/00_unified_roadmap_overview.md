# 00 — Unified Roadmap Overview

## Purpose

This document defines the unified roadmap from the current v1 architecture toward a durable v2 Relationship Reasoning Engine.

It consolidates the prior recommendations around fixing current v1 shortcomings, hardening deployment and operations, improving test/evaluation quality, adding safety red-team coverage, preparing for React, expanding case and longitudinal workflows, and developing a future v2 product architecture.

---

# Current State Assessment

The current application appears to have implemented many core architectural foundations:

- UI/API/worker container split
- DAG-style workflow execution
- durable jobs
- module registry
- workflow registry
- ontology registry
- prompt compiler
- module runner
- structured findings
- constructs and relationships
- graph merge
- convergence scoring
- synthesis
- golden transcript fixtures
- transcript preparation workspace
- safety-aware report mode
- report packages
- cases
- telemetry
- API key middleware
- generic request-ID error handling

This is a strong foundation.

The next phase should focus less on adding analytical breadth and more on making the system safer, more reliable, easier to evaluate, easier to deploy, ready for a production-grade React front end, and capable of deeper case and longitudinal workflows.

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
v1.1 Operational hardening
  ↓
v1.2 Evaluation + API + React readiness
  ↓
v1.3 React MVP + product depth
  ↓
v1.4 Platform maturity + React expansion
  ↓
v2.0 Product/platform architecture
```

---

# Non-Goals for Immediate Next Work

Do not prioritize adding many new analysis modules, rewriting backend architecture from scratch, replacing Streamlit before API contracts are ready, optimizing UI polish before report/evidence correctness, building multi-user collaboration before auth and data governance, or marketing/public launch before safety/eval maturity.

---

# Doc map (canonical)

| Need | Path |
|------|------|
| This overview | `docs/planning/phases/00_unified_roadmap_overview.md` |
| Active phase work | `docs/planning/phases/01` … `05` |
| Deferred (priority) | `docs/planning/deferred_backlog.md` |
| Unprioritized ideas | `docs/planning/general_backlog.md` |
| Completed Phases 1–49 | `docs/archived/planning/phases.md` |
| AWS architecture | `docs/developer/aws-deployment.md` |

When v1.1 ships, append archived phases starting at **Phase 50**.
