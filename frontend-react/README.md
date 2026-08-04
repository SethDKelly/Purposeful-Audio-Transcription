# RRE React frontend

Vite + React + TypeScript product UI for `/api/v1`. Routing uses **react-router-dom** (`BrowserRouter` in `src/App.tsx`).

Stack: React 19, TanStack Query, Zod, Tailwind 4, Vitest, Playwright. Planning context: [docs/planning/react_frontend_plan.md](../docs/planning/react_frontend_plan.md). Boundary rules: [docs/developer/ui-api-boundary.md](../docs/developer/ui-api-boundary.md).

## Local

```bash
cd frontend-react
cp .env.example .env
npm ci
npm run dev
```

With API on `:8000`, leave `VITE_API_BASE_URL` empty so Vite proxies `/api` (see `vite.config.ts`). Product calls use `credentials: 'include'` (session cookie).

| Variable | Role |
|----------|------|
| `VITE_API_BASE_URL` | Absolute API origin at build/runtime. Empty → same-origin `/api` (dev proxy or ALB). |
| `VITE_API_PROXY` | Dev proxy target (default `http://127.0.0.1:8000`). |
| `VITE_API_KEY` | Break-glass `X-API-Key` only — not for real users. |
| `VITE_SESSION_AUTH_REQUIRED` | When `true`, `AppShell` redirects unsigned users to `/login`. **Forced on in production builds** (`import.meta.env.PROD`). |

There is no supported local Bedrock/Transcribe stack. Use unit/e2e smoke locally; validate product flows after **Deploy to AWS dev**.

## Routes (`src/App.tsx`)

| Path | Page | Notes |
|------|------|--------|
| `/login` | `LoginPage` | Outside `AppShell`; email OTP / wake handoff |
| `/` | `DashboardPage` | Index under `AppShell` |
| `/ingest` | `IngestPage` | Paste/upload entry |
| `/transcripts/:transcriptId` | `PreparePage` | Turn edit / ready |
| `/transcripts/:transcriptId/analyze` | `AnalyzePage` | Start/poll workflow |
| `/runs/:runId/report` | `ReportPage` | Evidence-linked report |
| `/runs/:runId/graph` | `GraphPage` | Run-scoped graph |
| `/graph` | `GraphPage` | Graph without run id |
| `/cases` | `CasesPage` | Cases / session assign |
| `/modules` | `ModulesPage` | Module catalog |
| `/evaluations` | `EvaluationsPage` | Nav link only when `me.is_admin` |
| `/settings` | `SettingsPage` | Client prefs / auth notes |
| `*` | → `/` | Unknown paths redirect home |

`AppShell` wraps authenticated product routes: loads `/api/v1/auth/me`, gates on session when required, and still accepts legacy `?handoff=` (exchanges via `POST /api/v1/ops/power/handoff`) as defense in depth after wake.

## Scripts

| Command | Purpose |
|---------|---------|
| `npm run dev` | Vite on `:5173` |
| `npm run build` | `tsc -b` + production bundle |
| `npm run lint` | oxlint |
| `npm run test` | Vitest (jsdom) |
| `npm run test:e2e` | Playwright smoke |
| `npm run preview` | Serve `dist/` |

Component tests that use `Link` / `useNavigate` / `useParams` must wrap with `MemoryRouter` (see `src/pages/IngestPage.test.tsx`).

## Docker / SPA hosting

```bash
docker build -t rre-dev-web ./frontend-react
```

nginx serves `dist/` and falls back to `index.html` for client routes (`nginx.conf` `try_files`). Deep links like `/transcripts/<id>` require that SPA fallback — do not use a static host that 404s unknown paths.

`location /api/` returns 404 inside the web container on purpose: route `/api` on the ALB to the API service (or set `VITE_API_BASE_URL` at image build).

## Common pitfalls

- **Patch bumps of `react-router-dom`** — keep `package-lock.json` from `npm ci` / Dependabot; no app code change expected for 7.x patches unless the release notes say otherwise.
- **Missing router in tests** — hooks from react-router throw outside a router context; use `MemoryRouter`.
- **Hard refresh 404 in prod** — missing SPA `try_files` / equivalent rewrite.
- **CORS / empty session** — browser calls need same-site cookies (`credentials: 'include'`) and ALB routing that keeps UI + API on the shared site model used in deploy.
- **`VITE_API_KEY` in the browser** — internal/emergency only; product auth is email OTP + `rre_session`.

## Related

- Typed client: `src/api/client.ts` (hand-maintained; see [api_changelog.md](../docs/developer/api_changelog.md))
- Supply chain / lockfile: [supply_chain.md](../docs/developer/supply_chain.md)
