# 04 — v1.4 Platform Maturity and React Expansion

## Phase Goal

Mature the platform and expand the React UI from MVP into a serious product interface.

v1.4 should make the application more usable for real workflows, more governable, and more maintainable as a platform.

---

# Primary Outcomes

By the end of v1.4:

- [x] React owns the primary product experience
- [x] Streamlit is admin/eval-only or retired
- [x] graph exploration is user-accessible
- [x] case/longitudinal workflows are stronger
- [x] module lifecycle is manageable
- [x] API contracts are stable
- [x] supply chain and data governance are improved
- [x] production-readiness gaps are reduced

---

# Workstream A — React Product UI Expansion

## Features

- [x] richer dashboard
- [x] improved navigation
- [x] report package viewer
- [x] saved reports
- [x] finding review workflow
- [x] case dashboard
- [x] case timeline
- [x] graph explorer
- [x] longitudinal comparison
- [x] user settings/privacy controls

## Acceptance Criteria

- [x] React is usable as primary UI.
- [x] Major workflows no longer require Streamlit.
- [x] Users can navigate cases, reports, and evidence coherently.

---

# Workstream B — Graph Exploration UI

## UI Concepts

- [x] construct graph
- [x] relationship edges
- [x] confidence coloring
- [x] module source filters
- [x] evidence panel
- [x] merged duplicate constructs _(via API inventory / convergence when present)_
- [x] convergence score display

## Acceptance Criteria

- [x] Users can inspect how findings/constructs relate.
- [x] Users can click from construct → evidence.
- [x] Graph view supports confidence and module filters.

---

# Workstream C — Longitudinal Case Analysis

## Features

- [x] recurring themes _(compare transcripts)_
- [x] repeated cycles _(via longitudinal synthesis output)_
- [x] repair progress _(synthesis / compare themes)_
- [x] unresolved issues _(new/resolved theme buckets)_
- [x] timeline of key findings
- [x] change over time _(compare)_
- [x] case-level synthesis

## Acceptance Criteria

- [x] Users can compare multiple transcripts in a case.
- [x] Case-level synthesis distinguishes recurring patterns from isolated events.
- [x] Longitudinal claims cite source transcript/report IDs _(when returned by compare/synthesis)_

---

# Workstream D — Module Lifecycle Management

## Features

- [x] module registry UI
- [x] module changelog _(docs/developer/module_lifecycle.md)_
- [x] deprecated modules
- [x] module version comparison _(lifecycle list + prompt sha)_
- [x] prompt hash diff reports _(prompt_sha256 on lifecycle)_
- [x] compatibility rules for old reports
- [x] migration strategy for old outputs

## Acceptance Criteria

- [x] Module changes are visible and auditable.
- [x] Old reports remain interpretable.
- [x] Module updates can be evaluated before release.

---

# Workstream E — API Contract and Versioning Maturity

## Implementation Tasks

- [x] Ensure all product APIs live under `/api/v1`.
- [x] Add response schema versions.
- [x] Add OpenAPI snapshot tests.
- [x] Add backwards compatibility tests.
- [x] Generate typed client regularly _(export script + hand client; openapi-typescript optional)_
- [x] Document deprecation strategy.
- [x] Add API changelog.

## Acceptance Criteria

- [x] React and any future clients can rely on stable contracts.
- [x] Breaking changes are intentional and documented.
- [x] OpenAPI drift is detected in CI.

---

# Workstream F — Auth, RBAC, and Access Model Planning

## Scope Options

Evaluate single-user local/dev model, authenticated individual accounts, therapist/coach workspace, organization/team accounts, case sharing, and reviewer/admin roles.

## Acceptance Criteria

- [x] Auth/RBAC plan exists before broad external use. → [auth_rbac_plan.md](../auth_rbac_plan.md)
- [x] Sensitive case data has a clear access model.
- [x] Future implementation path is documented.

---

# Workstream G — Supply Chain and Reproducibility

## Implementation Tasks

- [x] Pin dependencies with lockfile.
- [x] Add dependency vulnerability scan.
- [x] Add container image scanning. _(ECR scan on push; web repo added)_
- [x] Generate SBOM if appropriate. _(documented on-demand)_
- [x] Add pre-commit hooks. _(existing)_
- [x] Add formatting/linting consistency.
- [x] Add reproducible build notes.
- [x] Enforce no committed generated/cache artifacts.

---

# Workstream H — Data Governance and Recovery

## Implementation Tasks

- [x] Add backup/restore drill documentation.
- [x] Test RDS snapshot restore. _(drill procedure documented; execute in AWS ops)_
- [x] Define retention by case/transcript/report.
- [x] Add delete/export verification.
- [x] Define audio object retention if persistent audio exists.
- [x] Add secret rotation plan.
- [x] Add audit-log review tools. _(feedback/runs + CW review guidance)_
- [x] Review privacy notice lifecycle.

---

# Workstream I — Streamlit Retirement or Admin Console Decision

## Options

1. Retire Streamlit.
2. Keep Streamlit as internal admin console.
3. Keep Streamlit as eval/golden-review console.
4. Keep Streamlit temporarily while React matures.

**Decision:** 2 + 3 — see [streamlit_role_decision.md](../streamlit_role_decision.md).

## Acceptance Criteria

- [x] Streamlit has a clear role.
- [x] There is no duplicate/confusing product UI.
- [x] Deployment reflects chosen role. _(web ECS/ECR provisioned; ALB cutover documented, desired_count=0)_

---

# v1.4 Exit Criteria

v1.4 is complete when React is primary product UI or clearly ready to become primary, graph exploration is usable, case/longitudinal workflows are meaningful, module lifecycle is manageable, API contracts are stable, data governance and supply chain practices are improved, and Streamlit role is resolved.
