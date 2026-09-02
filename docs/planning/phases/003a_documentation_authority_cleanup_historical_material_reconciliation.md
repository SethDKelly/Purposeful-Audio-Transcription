# 003-A — Documentation Authority Cleanup and Historical Material Reconciliation

## Status

Complete.

This subgroup verifies Phase 003 division, creates the Phase 003 overview, and classifies living, historical, legacy, reference, and implementation materials for future refactor planning.

---

# Purpose

003-A prevents authority drift before Phase 003 begins implementation-ready planning.

It answers:

- Is Phase 003 appropriately divided?
- Which documents are current authority?
- Which documents are active planning authority?
- Which documents are reference material pending reconciliation?
- Which documents are historical and should not be rewritten as current status?
- Which implementation materials can inform later work without overriding concepts?
- What should 003-B use as its starting authority?

---

# Outputs

| Output | Document |
|---|---|
| Phase 003 division verification | `../inventories/003_phase_division_verification.md` |
| Phase 003 overview | `003_foundation_refactor_planning_authority_cleanup.md` |
| Documentation authority cleanup plan | `../architecture/003a_documentation_authority_cleanup_plan.md` |
| Living authority surface audit | `../inventories/003a_living_authority_surface_audit.md` |
| Historical material reconciliation inventory | `../inventories/003a_historical_material_reconciliation_inventory.md` |

---

# Verification Result

```text
Phase 003 is appropriately divided.
Proceed with 003-A.
```

The sequence is appropriate because it:

- places documentation authority cleanup first
- separates domain, lifecycle, privacy, analysis, cost-state, and UI/report work
- preserves dependency order from Phase 002
- avoids a broad rewrite
- includes the mandatory 003-H exit review

---

# Accepted Decisions

## 1. Phase 003 is properly divided

The authorized Phase 003 grouping from 002-I is accepted without modification.

The groups are coherent, dependency-aware, and gate-aligned.

## 2. Phase 003 now has an explicit overview

The project no longer relies only on 002-I to describe Phase 003.

A dedicated Phase 003 overview has been added.

## 3. Current authority stack is explicit

Current authority now flows through:

```text
docs/concepts/
→ Phase 002 exit review and authorized Phase 003 scope
→ Phase 003 overview
→ accepted Phase 003 subgroup outputs
→ reconciled implementation plans
→ code
```

## 4. Living indexes should show Phase 003 active

Root and documentation indexes should show:

```text
Phase 001 complete
Phase 002 complete
Phase 003 active
003-A complete
003-B next
003-H mandatory exit gate
```

## 5. Legacy docs remain useful but not current authority

User docs, developer docs, design-package docs, and older planning backlogs remain available as reference pending reconciliation.

They do not override accepted concepts or Phase 002 architecture decisions.

## 6. Release notes remain historical

Release notes should not be edited to match current product status.

They record previous project states.

## 7. Code remains implementation reference

Existing code, migrations, scripts, and infrastructure files may inform planning, but they do not define product authority when they conflict with accepted concepts.

---

# Reconciliation Labels Accepted

Use these labels in future audits:

```text
current_authority
active_planning
reference_pending_reconciliation
historical
superseded
implementation_reference
deferred
```

---

# Handoff to 003-B

003-B should use 003-A to inspect domain terminology and produce implementation-ready mapping plans.

It should reconcile useful existing implementation names without allowing them to override accepted concepts.

003-B should focus on:

- Transcript / TranscriptVersion / EvidenceQuote / Finding / Case / graph concepts
- WorkflowRun to ReflectionRun mapping
- modules to ReflectionLens mapping
- Recommendation / Intervention to ReflectionPoint replacement plan
- SafetyMode to SafetyPosture mapping
- SourceType.AUDIO to Recording / SourceArtifact boundary
- RetentionRule, PrivacyBoundary, CostState, AnalysisScope, PsychologicalHypothesis, and CorpusPatternAssessment planning targets

---

# Non-goals

003-A does not implement:

- code changes
- schema migrations
- prompt rewrites
- validator implementation
- report rendering changes
- UI changes
- deployment changes
- GitHub Actions restoration
- release note rewrites
- full user/developer documentation rewrites

---

# Exit Criteria

003-A is complete when:

- Phase 003 division is verified
- Phase 003 overview exists
- documentation authority cleanup plan exists
- living authority surface audit exists
- historical material reconciliation inventory exists
- living indexes are updated to Phase 003 status
- 003-B handoff is explicit
- broad implementation remains blocked

All criteria are satisfied.

---

# Next Phase

Proceed to:

```text
003-B — Domain Terminology and Concept Mapping Implementation Plan
```