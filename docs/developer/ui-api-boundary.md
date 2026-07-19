# UI / API boundary (v1.1 Workstream F)

Streamlit is an **HTTP client** of the FastAPI service. It must not execute analysis,
touch RDS, or call Bedrock/Transcribe directly.

## Allowed UI dependencies

| Layer | OK? | Notes |
|-------|-----|-------|
| `ui/api_client.py` | Yes | Sole network boundary to the API |
| `ui/components/*` | Yes | Presentation only; call `api_client` for data |
| `config.settings` | Yes | `RRE_API_BASE_URL` / `BACKEND_API_URL`, `API_KEY`, display defaults |
| `backend.services` / `backend.repositories` / `backend.db` | **No** | Use API routes instead |
| `backend.api` / workflow engine / providers | **No** | Server-side only |

## Base URL

| Env var | Role |
|---------|------|
| `RRE_API_BASE_URL` | Canonical (ECS UI task sets this) |
| `BACKEND_API_URL` | Accepted alias (same setting) |

Resolved via `settings.api_base_url` in `ui/api_client.py` (`API_BASE`).

Local default when unset: `http://{api_host}:{api_port}`.

## Auth

When `API_KEY` is set, the UI sends `X-API-Key` on every request. The UI execution
role may inject `API_KEY` only — not `DATABASE_URL` (see `infra/dev/iam.tf`).

## Runtime images

| Image | Contains | Calls |
|-------|----------|-------|
| `Dockerfile.ui` | Streamlit + `ui/` + shared `config` package | HTTP → API |
| `Dockerfile.cloud` | FastAPI + worker entrypoint | Bedrock, Transcribe, RDS, S3 |

The UI image may still *install* the `backend` package for packaging layout, but
UI **source** must not import backend internals. Guard: `scripts/check_ui_api_boundary.py`.

## React readiness

A future React app should reuse the same HTTP contracts (`/api/*`) and auth header.
No Streamlit-specific server APIs are required beyond what `ui/api_client.py` already calls.
