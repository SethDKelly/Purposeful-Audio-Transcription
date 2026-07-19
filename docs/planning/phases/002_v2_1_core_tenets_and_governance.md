# 002 — Core Tenets and Governance

## Phase Goal

Formalize the core product tenets and make them part of the application’s development process.

This phase comes first because the rest of v2.1 depends on a clear definition of what the application must preserve.

**Status:** Complete · Tests: `tests/test_phase_002_tenet_governance.py`

---

# Scope

Create and integrate:

```text
docs/product/core_tenets.md
docs/developer/pr_review_tenet_checklist.md
docs/evaluation/tenet_compliance_evaluation_plan.md
```

Reference these documents from planning, architecture, safety, and evaluation docs.

---

# Product Tenets

The application should optimize for:

1. Evidence traceability
2. Confidence calibration
3. Multi-lens analysis
4. Non-diagnostic discipline
5. Longitudinal case tracking
6. Professional workflow fit
7. Safety-aware framing
8. Structured reasoning graph

---

# Implementation Tasks

## Documentation

- [x] Add `docs/product/core_tenets.md`.
- [x] Add `docs/developer/pr_review_tenet_checklist.md`.
- [x] Add `docs/evaluation/tenet_compliance_evaluation_plan.md`.
- [x] Update `docs/planning/README.md` to reference the tenets.
- [x] Update `docs/developer/architecture.md` to reference the tenets.
- [x] Update `docs/product/safety_aware_report_mode.md` to reference safety-aware framing and non-diagnostic discipline.
- [x] Update evaluation docs to reference tenet compliance.
- [x] Ensure `docs/README.md` indexes tenets, security plan, and ADRs.

## Planning

- [x] Adopt numeric v2.1 sequence (`001`–`009`) as canonical; archive superseded band `10`.
- [x] Rehome cutover / Cognito / ops leftovers into [deferred_backlog.md](../deferred_backlog.md).
- [x] Spot-check remaining backlog rows against tenets; demote non-fitting items to [general_backlog.md](../general_backlog.md) if needed.
- [x] Keep the roadmap market-agnostic.

## PR Governance

- [x] Add tenet checklist to PR template if one exists (or document checklist path in contributing.md). → [`.github/pull_request_template.md`](../../../.github/pull_request_template.md)
- [x] Add documentation stating that new features should preserve evidence, confidence, safety, and graph integrity. → [contributing.md](../../developer/contributing.md)

---

# Acceptance Criteria

- [x] Core tenets document exists.
- [x] Planning docs reference the tenets.
- [x] PR review checklist exists.
- [x] Evaluation plan includes tenet compliance categories.
- [x] Future work can be judged against the tenets.
- [x] No market-specific assumptions are introduced into the core engine.
