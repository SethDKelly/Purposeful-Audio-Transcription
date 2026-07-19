# React frontend plan (v1.2)

Canonical product decision for starting React after API stabilization.
Companion detail: [phases/06_react_transition_plan.md](phases/06_react_transition_plan.md).

## Stack (selected)

```text
Vite + React + TypeScript
TanStack Query
React Router
Zod
Tailwind CSS + shadcn/ui
OpenAPI-generated API client (from /openapi.json, prefer /api/v1 paths)
React Flow (graph views; Cytoscape optional later)
Vitest + Playwright
```

Avoid Next.js unless SSR/SEO requirements appear.

## API client approach

1. Treat **`/api/v1/*`** as the React contract (legacy `/api/*` remains for Streamlit).
2. Generate TypeScript types/client from OpenAPI (`openapi-typescript` or `orval`).
3. Snapshot `/api/v1` path list in CI (`tests/snapshots/openapi_v1_paths.json`).
4. Errors use `{ error_code, message, request_id, details }` (+ legacy `detail`).

## Auth

- Dev/UAT: shared `X-API-Key` (same as Streamlit / ECS Secrets Manager).
- Session cookies / Cognito: deferred until external multi-user UAT (see deferred backlog).
- Never embed AWS credentials or DB URLs in the frontend.

## Deployment target

1. **Near term (v1.3):** ECS service `rre-dev-web` (static nginx or Vite preview) behind the existing ALB, or replace Streamlit path gradually.
2. **Later:** S3 + CloudFront for static assets; API remains ECS/ALB.

## Streamlit long-term role

| Phase | Role |
|-------|------|
| v1.2 | Temporary product UI; HTTP client only |
| **v1.3 (now)** | Core product flows in React (`frontend-react/`); Streamlit demoted to admin/eval/internal console |
| v1.4+ | React primary; Streamlit optional internal tooling |
| v2 | Retire or keep eval-only |

**v1.3 demotion note:** New user journeys (ingest → prepare → analyze → evidence-linked report → feedback/cases) ship in React via `/api/v1`. Keep Streamlit for golden eval review, ops debugging, and any admin surfaces not yet ported. Do not add new product features only in Streamlit.

## Screen inventory (MVP)

1. Ingest (paste / upload / transcribe status)
2. Prepare transcript (turns, speakers, ready)
3. Analyze (workflow select, run, progress)
4. Report (synthesis, findings, evidence quotes)
5. Cases list + case detail timeline
6. Finding feedback

## Component inventory (MVP)

- `TranscriptEditor`, `TurnRow`, `SpeakerChip`
- `WorkflowRunner`, `JobStatusBadge`
- `FindingCard`, `EvidenceQuoteViewer`, `ConfidenceBadge`
- `CaseTimeline`, `ReportExportMenu`
- Generated `apiClient` + TanStack Query hooks

## Product flows

```text
ingest → prepare → ready → start workflow (/api/v1/workflow-runs)
  → poll status → open report → review findings/evidence → optional feedback
```

Case flow: create/open case → assign sessions → timeline → longitudinal later (v1.3+).

## Exit for React start (v1.3)

- `/api/v1` paths stable + OpenAPI snapshot green
- Streamlit remains API-only (boundary CI check)
- Golden + safety eval harness exists for regression gates
- No React code required in v1.2
