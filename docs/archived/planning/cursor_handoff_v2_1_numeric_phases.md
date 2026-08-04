# Cursor Handoff — v2.1 Numeric Phase Plan

## Objective

Use this package to update the repository planning docs with numeric phase files.

This reproduces the previous next-phase package while replacing the single large phase plan with decomposed numeric phase documents.

---

# Files to Add

Copy these files into the repository:

```text
docs/product/core_tenets.md
docs/security/simple_email_auth_plan.md
docs/developer/evidence_precision_design.md
docs/developer/evidence_snapshot_versioning_design.md
docs/developer/architecture_decisions/adr_001_simple_email_auth_before_enterprise_sso.md
docs/developer/architecture_decisions/adr_002_concise_evidence_spans.md
docs/evaluation/tenet_compliance_evaluation_plan.md
docs/planning/v2_readiness_assessment.md
docs/developer/pr_review_tenet_checklist.md
docs/planning/phases/001_v2_1_phase_sequence_overview.md
docs/planning/phases/002_v2_1_core_tenets_and_governance.md
docs/planning/phases/003_v2_1_simple_email_auth_and_ownership.md
docs/planning/phases/004_v2_1_evidence_precision.md
docs/planning/phases/005_v2_1_evidence_snapshots_and_versioning.md
docs/planning/phases/006_v2_1_worker_atomicity_and_operational_safety.md
docs/planning/phases/007_v2_1_safety_policy_and_non_diagnostic_enforcement.md
docs/planning/phases/008_v2_1_graph_relationship_evidence_and_case_correctness.md
docs/planning/phases/009_v2_1_react_api_contract_and_release_candidate_readiness.md
```

---

# Existing File Handling

If the repository contains:

```text
docs/planning/phases/11_v2_1_tenet_hardening_auth_and_evidence_precision.md
```

or decomposed files using names like:

```text
11a_v2_1_...
11b_v2_1_...
11h_v2_1_...
```

replace or archive them.

Recommended archive path:

```text
docs/planning/phases/archive/
```

Use the numeric phase files as the active plan.

---

# Implementation Order

Implement in this order:

1. `001` — sequence overview
2. `002` — core tenets and governance
3. `003` — simple email auth and ownership
4. `004` — evidence precision
5. `005` — evidence snapshots/versioning
6. `006` — worker atomicity
7. `007` — safety policy and non-diagnostic enforcement
8. `008` — graph relationship evidence and case correctness
9. `009` — React API contract and release-candidate readiness

---

# Backlog Rule

Do not delete existing backlog items.

If an item is not covered by these phase files:

- keep it in backlog
- move it to future considerations
- mark it as superseded if obsolete
- mark it complete if already implemented

---

# Market-Agnostic Rule

Do not specialize the core application for any one market yet.

The current strategy is to strengthen:

```text
evidence
confidence
multi-lens reasoning
non-diagnostic discipline
safety-aware framing
structured graph reasoning
professional workflow support
longitudinal cases
```

Market-specific workflows can come later through templates, presets, exports, and language packs.

---

# Definition of Done

This planning update is complete when:

- numeric phase files exist
- old combined or lettered phase docs are archived/replaced
- the overview links to each numeric sub-phase
- each sub-phase has clear scope and acceptance criteria
- implementation order is obvious
- existing backlog items are preserved
- v2 beta / RC / GA distinction is documented
