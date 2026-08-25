# 002-G — UI/UX Concept Alignment Plan

## Status

Complete.

This subgroup translates accepted product concepts and architecture decisions into UI/UX planning requirements.

---

# Purpose

002-G defines how future user-facing surfaces should preserve product meaning.

It answers:

- How should the product be framed in the UI?
- Which terms should appear or be avoided?
- How should transcript/case/corpus scope be shown?
- How should reports preserve evidence, confidence, hypotheses, alternatives, safety posture, and limitations?
- How should retention, deletion, export, and cost-state behavior be explained?
- Which user flows need concept-boundary acceptance gates?

---

# Outputs

| Output | Document |
|---|---|
| UI/UX concept alignment plan | `../architecture/002g_ui_ux_concept_alignment_plan.md` |
| UI/UX language matrix | `../inventories/002g_ui_ux_language_matrix.md` |
| User flow alignment inventory | `../inventories/002g_user_flow_alignment_inventory.md` |

---

# Accepted Decisions

## 1. Product UX should be reflection-first, transcript-enabled

The product should feel like a secure evidence-linked conversation reflection system.

It should not feel like only an audio transcription utility.

## 2. Evidence scope must be visible

Analysis and reports should show whether they are based on:

```text
single transcript version
selected transcript set
case evidence corpus
```

## 3. Case Evidence Corpus needs UI presence

A case is not merely a folder.

Case assignment should be shown as retention-significant, privacy-significant, and corpus-reasoning significant.

## 4. Report UX must preserve non-diagnostic boundaries

Reports should show evidence, confidence, support levels, alternatives, limitations, safety posture, and reflection points.

Reports should not read like diagnosis, treatment, legal adjudication, or hidden-intent proof.

## 5. Reflection Point should replace recommendation/intervention language

User-facing guidance should be non-prescriptive and evidence-linked.

Future UI copy should prefer `Reflection Point` over `Recommendation` or `Intervention` by default.

## 6. Safety posture must affect the UI

Elevated/high-risk safety posture should be visible and should modify report framing, section ordering, suppressed prompts, and support-category language.

## 7. Retention and deletion must be understandable

The user should understand draft expiration, saved transcript durability, case-retained corpus effects, deletion cascades, and export boundaries.

## 8. Cost State must feel intentional

Asleep/waking/idle/shutdown behavior should appear as intentional personal cost control, not silent application failure.

---

# Handoff to 002-H

002-H should convert 002-G into backlog items and acceptance gates for:

- terminology replacement
- UI copy audit
- report scope headers
- evidence quote display
- hypothesis section structure
- safety posture banner/section behavior
- case evidence corpus surfaces
- retention/delete/export flows
- cost-state status and controls
- legacy UI refactor sequencing

---

# Non-goals

002-G does not implement:

- React components
- layouts
- routing
- visual design
- report rendering
- graph UI
- copy changes
- cost-state UI
- deletion/export UI

Implementation remains blocked until Phase 002-I exit review authorizes the next phase.

---

# Exit Criteria

002-G is complete when:

- UI/UX concept alignment plan exists
- user-facing terminology guidance exists
- user flow inventory exists
- report UX requirements are documented
- safety UX requirements are documented
- retention/delete/export UX requirements are documented
- cost-state UX requirements are documented
- 002-H handoff is explicit

All criteria are satisfied.

---

# Next Phase

Proceed to:

```text
002-H — Refactor Backlog, Sequencing, and Acceptance Gates
```
