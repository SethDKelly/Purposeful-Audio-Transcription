# UI / API boundary

Streamlit and React are **HTTP clients** of the FastAPI service. Neither may execute analysis,
import worker/engine modules, open DB connections, touch RDS, or call Bedrock/Transcribe directly.

React (`frontend-react/`) is the **primary product UI**. Streamlit (`ui/`) remains for
admin/eval/internal workflows.

## React client (`frontend-react/`)

| Layer | OK? | Notes |
|-------|-----|-------|
| `src/api/client.ts` | Yes | Sole network boundary; `fetch` + `credentials: 'include'` |
| `src/pages/*`, `src/components/*` | Yes | Presentation + routing; call `api.*` only |
| `react-router-dom` routes in `src/App.tsx` | Yes | SPA paths; see [../../frontend-react/README.md](../../frontend-react/README.md) |
| Env `VITE_API_BASE_URL` / `VITE_API_KEY` | Yes | Base URL + break-glass key only |
| `backend.*` / RDS / Bedrock / Transcribe | **No** | Server-side only |

### Contract

- Prefer **`/api/v1/*`** for product flows (auth, transcripts, workflows, reports, cases, power handoff).
- Session cookie auth is the product path; optional `X-API-Key` via `VITE_API_KEY` is internal/dev break-glass.
- Errors follow `{ error_code, message, request_id, details }` (plus legacy `detail`).

### Local API base

| Env var | Role |
|---------|------|
| `VITE_API_BASE_URL` | Absolute API origin. Empty → relative `/api` (Vite proxy or ALB). |
| `VITE_API_PROXY` | Dev proxy target when base URL is empty (default `http://127.0.0.1:8000`). |

Production web image: `frontend-react/Dockerfile` → ECR `rre-dev-web` (nginx SPA). ALB should send `/` to web and `/api` to API.

## Streamlit client (`ui/`)

### Allowed dependencies

| Layer | OK? | Notes |
|-------|-----|-------|
| `ui/api_client.py` | Yes | Sole network boundary to the API |
| `ui/components/*` | Yes | Presentation only; call `api_client` for data |
| `config.settings` | Yes | `RRE_API_BASE_URL` / `BACKEND_API_URL`, `API_KEY`, display defaults |
| `backend.services` / `backend.repositories` / `backend.db` | **No** | Use API routes instead |
| `backend.api` / workflow engine / providers | **No** | Server-side only |

### Base URL

| Env var | Role |
|---------|------|
| `RRE_API_BASE_URL` | Canonical (ECS UI task sets this) |
| `BACKEND_API_URL` | Accepted alias (same setting) |

Resolved via `settings.api_base_url` in `ui/api_client.py` (`API_BASE`).

Local default when unset: `http://{api_host}:{api_port}`.

### Auth

When `API_KEY` is set, the UI sends `X-API-Key` on every request. The UI execution
role may inject `API_KEY` only — not `DATABASE_URL` (see `infra/dev/iam.tf`).

## Runtime images

| Image | Contains | Calls |
|-------|----------|-------|
| `frontend-react/Dockerfile` | React static build + nginx | HTTP → `/api/v1` (via ALB or build-time base URL) |
| `Dockerfile.ui` | Streamlit + `ui/` + shared `config` package | HTTP → API |
| `Dockerfile.cloud` | FastAPI + worker entrypoint | Bedrock, Transcribe, RDS, S3 |

The Streamlit image may still *install* the `backend` package for packaging layout, but
UI **source** must not import backend internals. Guard: `scripts/check_ui_api_boundary.py`.

## Related

- React routes and SPA pitfalls: [../../frontend-react/README.md](../../frontend-react/README.md)
- API surface: [api-reference.md](api-reference.md)
- React plan: [../planning/react_frontend_plan.md](../planning/react_frontend_plan.md)
