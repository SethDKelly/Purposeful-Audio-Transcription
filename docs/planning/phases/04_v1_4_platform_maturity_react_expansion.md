# 04 — v1.4 Platform Maturity and React Expansion

## Phase Goal

Mature the platform and expand the React UI from MVP into a serious product interface.

v1.4 should make the application more usable for real workflows, more governable, and more maintainable as a platform.

---

# Primary Outcomes

By the end of v1.4:

- React owns the primary product experience
- Streamlit is admin/eval-only or retired
- graph exploration is user-accessible
- case/longitudinal workflows are stronger
- module lifecycle is manageable
- API contracts are stable
- supply chain and data governance are improved
- production-readiness gaps are reduced

---

# Workstream A — React Product UI Expansion

## Features

- richer dashboard
- improved navigation
- report package viewer
- saved reports
- finding review workflow
- case dashboard
- case timeline
- graph explorer
- longitudinal comparison
- user settings/privacy controls

## Acceptance Criteria

- React is usable as primary UI.
- Major workflows no longer require Streamlit.
- Users can navigate cases, reports, and evidence coherently.

---

# Workstream B — Graph Exploration UI

## UI Concepts

- construct graph
- relationship edges
- confidence coloring
- module source filters
- evidence panel
- merged duplicate constructs
- convergence score display

## Acceptance Criteria

- Users can inspect how findings/constructs relate.
- Users can click from construct → evidence.
- Graph view supports confidence and module filters.

---

# Workstream C — Longitudinal Case Analysis

## Features

- recurring themes
- repeated cycles
- repair progress
- unresolved issues
- timeline of key findings
- change over time
- case-level synthesis

## Acceptance Criteria

- Users can compare multiple transcripts in a case.
- Case-level synthesis distinguishes recurring patterns from isolated events.
- Longitudinal claims cite source transcript/report IDs.

---

# Workstream D — Module Lifecycle Management

## Features

- module registry UI
- module changelog
- deprecated modules
- module version comparison
- prompt hash diff reports
- compatibility rules for old reports
- migration strategy for old outputs

## Acceptance Criteria

- Module changes are visible and auditable.
- Old reports remain interpretable.
- Module updates can be evaluated before release.

---

# Workstream E — API Contract and Versioning Maturity

## Implementation Tasks

- [ ] Ensure all product APIs live under `/api/v1`.
- [ ] Add response schema versions.
- [ ] Add OpenAPI snapshot tests.
- [ ] Add backwards compatibility tests.
- [ ] Generate typed client regularly.
- [ ] Document deprecation strategy.
- [ ] Add API changelog.

## Acceptance Criteria

- React and any future clients can rely on stable contracts.
- Breaking changes are intentional and documented.
- OpenAPI drift is detected in CI.

---

# Workstream F — Auth, RBAC, and Access Model Planning

## Scope Options

Evaluate single-user local/dev model, authenticated individual accounts, therapist/coach workspace, organization/team accounts, case sharing, and reviewer/admin roles.

## Acceptance Criteria

- Auth/RBAC plan exists before broad external use.
- Sensitive case data has a clear access model.
- Future implementation path is documented.

---

# Workstream G — Supply Chain and Reproducibility

## Implementation Tasks

- [ ] Pin dependencies with lockfile.
- [ ] Add dependency vulnerability scan.
- [ ] Add container image scanning.
- [ ] Generate SBOM if appropriate.
- [ ] Add pre-commit hooks.
- [ ] Add formatting/linting consistency.
- [ ] Add reproducible build notes.
- [ ] Enforce no committed generated/cache artifacts.

---

# Workstream H — Data Governance and Recovery

## Implementation Tasks

- [ ] Add backup/restore drill documentation.
- [ ] Test RDS snapshot restore.
- [ ] Define retention by case/transcript/report.
- [ ] Add delete/export verification.
- [ ] Define audio object retention if persistent audio exists.
- [ ] Add secret rotation plan.
- [ ] Add audit-log review tools.
- [ ] Review privacy notice lifecycle.

---

# Workstream I — Streamlit Retirement or Admin Console Decision

## Options

1. Retire Streamlit.
2. Keep Streamlit as internal admin console.
3. Keep Streamlit as eval/golden-review console.
4. Keep Streamlit temporarily while React matures.

## Acceptance Criteria

- Streamlit has a clear role.
- There is no duplicate/confusing product UI.
- Deployment reflects chosen role.

---

# v1.4 Exit Criteria

v1.4 is complete when React is primary product UI or clearly ready to become primary, graph exploration is usable, case/longitudinal workflows are meaningful, module lifecycle is manageable, API contracts are stable, data governance and supply chain practices are improved, and Streamlit role is resolved.
