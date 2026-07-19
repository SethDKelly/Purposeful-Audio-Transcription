# 06 — React Transition Plan

## Summary Recommendation

React will benefit the application, but it should be introduced after API contracts and operational foundations are stable.

Recommended strategy:

```text
v1.1: Make Streamlit API-client-only          ✓
v1.2: Stabilize API and prepare React        ✓
v1.3: Build React MVP alongside Streamlit    ✓
v1.4: Expand React and decide Streamlit's role ✓
v2.0 foundation: safety/evals/packages       ✓
v2.1: React ALB primary + auth MVP           ← next
v2.x: React primary at scale / optional Streamlit retire
```

---

# Why React Is Worth It

The application is becoming interactive, stateful, evidence-linked, case-based, graph-driven, review-oriented, and workflow-heavy.

React is especially valuable for transcript editing, evidence-linked report exploration, graph visualization, case dashboards, longitudinal comparison, finding feedback workflows, and polished export/report UX.

---

# Why Not Switch Immediately

Do not switch immediately if API contracts are unstable, Streamlit still imports backend internals, backend/worker hardening is incomplete, deployment is not stable, safety/eval harness is not mature, or the core product flow is still changing rapidly.

Switching too early will create rework.

---

# Preferred React Stack

```text
Vite
React
TypeScript
TanStack Query
React Router
Zod
Tailwind or shadcn/ui
OpenAPI-generated API client
React Flow or Cytoscape.js
Vitest
Playwright
```

Avoid Next.js unless SSR, public SEO, or framework-specific routing/server needs emerge.

---

# Streamlit Transition Strategy

## Current

Streamlit is the product UI.

## v1.1

Streamlit becomes API-client-like.

## v1.2

Streamlit is treated as temporary product UI plus internal tool.

## v1.3

React covers core user flow; Streamlit remains admin/eval console.

## v1.4

React covers most product workflows.

## v2

Streamlit is either retired or retained only as internal eval/admin console.

---

# React MVP Scope

Do not start with graph visualization.

Start with one vertical slice:

```text
upload/paste transcript
→ review transcript
→ choose workflow
→ launch workflow run
→ poll job status
→ view report summary
→ inspect finding evidence
→ export report
```

This proves the client/API architecture.

---

# React Screen Inventory

## v1.3 MVP Screens

- Home / Dashboard
- Transcript Upload
- Transcript Review
- Workflow Selection
- Workflow Run Progress
- Report Summary
- Finding Detail / Evidence Panel
- Basic Export

## v1.4 Expansion Screens

- Case Dashboard
- Case Timeline
- Graph Explorer
- Report Package Viewer
- Finding Feedback Review
- Settings / Privacy
- Module Registry / Admin if needed
- Golden Eval Review if replacing Streamlit admin

---

# API Requirements Before React MVP

React needs stable endpoints for:

```text
POST   /api/v1/transcripts
GET    /api/v1/transcripts/{id}
PATCH  /api/v1/transcripts/{id}/turns
GET    /api/v1/workflows
POST   /api/v1/workflow-runs
GET    /api/v1/workflow-runs/{id}/status
GET    /api/v1/reports/{id}
GET    /api/v1/reports/{id}/findings
GET    /api/v1/reports/{id}/evidence
POST   /api/v1/findings/{id}/feedback
POST   /api/v1/exports
```

---

# React Deployment Options

## Initial Option — ECS Static Server

Useful if current deployment is ECS-centric.

Pros: fits current service model, simple transition, same deployment machinery.

Cons: more expensive than static hosting, still requires a UI service.

## Long-Term Option — S3 + CloudFront

Preferred mature deployment.

Pros: cheap, fast, scalable, no UI container needed.

Cons: requires auth/API integration and CloudFront setup.

Recommended path:

```text
v1.3: React container
v1.4/v2: evaluate S3 + CloudFront
```

---

# Migration Risks

## Risk: Duplicate UI complexity

Mitigation: React owns new product flows. Streamlit remains admin/eval only. Avoid maintaining two product UIs long-term.

## Risk: API churn

Mitigation: stabilize `/api/v1` before React. Use generated API client. Use OpenAPI contract tests.

## Risk: Product scope creep

Mitigation: React MVP must be a narrow vertical slice. Do not start with graph/case mega-dashboard.

## Risk: Auth complexity

Mitigation: decide minimal auth/session model before React external use. Avoid hardcoding API keys in client-visible code for real deployment.

---

# React Success Criteria

React is worth continuing when users can complete the core workflow faster or more clearly than Streamlit, evidence navigation feels better, transcript editing is materially better, frontend code remains API-client-only, React does not force backend logic duplication, and Playwright can cover the happy path.
