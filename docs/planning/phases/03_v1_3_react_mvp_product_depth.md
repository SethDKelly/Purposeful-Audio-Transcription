# 03 — v1.3 React MVP and Product Depth

## Phase Goal

Introduce React as the primary user-facing product shell while continuing to use Streamlit for internal/admin/evaluation workflows.

This phase should prove that React materially improves the user experience for evidence-linked, workflow-heavy, case-based analysis.

---

# Primary Outcomes

By the end of v1.3:

- React app exists alongside Streamlit
- React uses generated or typed API client
- core user flow works end-to-end
- report viewer supports evidence-linked findings
- transcript preparation is more usable
- case model v2 begins
- human feedback workflow is usable
- long-transcript chunking architecture begins

---

# Workstream A — React App Scaffold

## Implementation Tasks

- [ ] Create `frontend-react/`.
- [ ] Use Vite + React + TypeScript.
- [ ] Add routing.
- [ ] Add TanStack Query.
- [ ] Add generated or typed API client.
- [ ] Add Zod validation where useful.
- [ ] Add design system baseline.
- [ ] Add environment config.
- [ ] Add Vitest.
- [ ] Add Playwright.
- [ ] Add Dockerfile for React static serving if using ECS initially.

## Acceptance Criteria

- React app builds.
- React app can call API health endpoint.
- React app has CI checks.
- Basic smoke E2E test passes.

---

# Workstream B — Core React Vertical Slice

## Required MVP Flow

```text
transcript upload or paste
→ transcript review/prep
→ workflow selection
→ workflow run creation
→ job status polling
→ report summary
→ evidence-linked finding cards
→ export
```

## Implementation Tasks

- [ ] Transcript upload/paste screen.
- [ ] Transcript detail screen.
- [ ] Workflow selection screen.
- [ ] Workflow run status screen.
- [ ] Report summary screen.
- [ ] Finding cards.
- [ ] Evidence drawer or side panel.
- [ ] Export button.
- [ ] Basic error states.
- [ ] Loading/progress states.
- [ ] Empty states.

## Acceptance Criteria

- A user can complete the core analysis flow in React.
- React does not directly call analysis logic.
- All backend access goes through API client.
- Evidence quote IDs are clickable or inspectable.

---

# Workstream C — Evidence-Linked Report Viewer

## UI Pattern

```text
Finding card
  - claim
  - confidence
  - source modules
  - cited quote IDs
  - alternatives/limitations
  - click evidence
      → transcript side panel scrolls to quote
```

## Implementation Tasks

- [ ] Finding list with confidence filters.
- [ ] Evidence quote side panel.
- [ ] Module/source filter.
- [ ] Construct type filter.
- [ ] Confidence filter.
- [ ] Alternative explanation display.
- [ ] Unsupported/low-confidence warning display.
- [ ] Copy/export selected finding.

## Acceptance Criteria

- Users can trace each claim to cited transcript text.
- Confidence is visually clear.
- Findings without evidence are visually flagged or hidden depending on policy.
- Report exploration feels materially better than Streamlit.

---

# Workstream D — Transcript Preparation Workspace v2

## Features

- turn-by-turn editing
- speaker relabeling
- split turn
- merge turns
- delete irrelevant turn
- mark section excluded from analysis
- edit original vs cleaned transcript
- unsaved changes warning
- transcript quality warnings
- regenerate evidence index after edits

## Acceptance Criteria

- User can correct speaker labels before analysis.
- Evidence IDs are regenerated or preserved according to documented rules.
- Analysis cannot start if transcript is invalid.

---

# Workstream E — Case Model v2 Foundation

## Suggested Entities

```text
Case
CaseParticipant
CaseTranscript
CaseWorkflowRun
CaseTheme
CaseTimelineEvent
CaseNote
CaseExport
PinnedFinding
```

## Implementation Tasks

- [ ] Case dashboard in React.
- [ ] Add transcript to case.
- [ ] Show case transcripts.
- [ ] Show prior reports.
- [ ] Pin important findings.
- [ ] Add case notes.
- [ ] Add basic timeline events.
- [ ] Add case-level export placeholder.

## Acceptance Criteria

- Users can manage multiple transcripts in a case.
- Users can see report history per case.
- Users can pin findings for later review.

---

# Workstream F — Human Feedback Workflow

## Feedback Labels

- helpful
- not helpful
- unsupported
- wrong speaker
- wrong evidence
- too speculative
- too clinical
- too vague
- actionably useful
- unsafe framing

## Acceptance Criteria

- Users/reviewers can provide structured feedback.
- Feedback is tied to module and version metadata.
- Feedback can guide module evaluation.

---

# Workstream G — Long Transcript Chunking Foundation

## Initial Architecture

```text
long transcript
→ chunk by time/topic/speaker turns
→ create chunk evidence indexes
→ run selected modules per chunk
→ consolidate chunk findings
→ run synthesis over consolidated findings
```

## v1.3 Scope

- [ ] Define chunk model.
- [ ] Define quote ID preservation strategy.
- [ ] Add transcript length warning.
- [ ] Add chunking design doc.
- [ ] Implement simple chunking prototype if feasible.
- [ ] Do not claim full long-transcript support until consolidation exists.

---

# Workstream H — React Deployment

## Options

Initial: containerized React static server in ECS.

Later: S3 + CloudFront.

## Acceptance Criteria

- React can be deployed separately from API/worker.
- React deployment does not disrupt Streamlit/internal UI if retained.

---

# v1.3 Exit Criteria

v1.3 is complete when React MVP core flow works, React uses API client only, evidence-linked report viewer is usable, transcript prep is better than Streamlit, feedback workflow exists, case model v2 begins, long-transcript architecture is documented/scaffolded, and Streamlit remains available for admin/eval or is clearly demoted.
