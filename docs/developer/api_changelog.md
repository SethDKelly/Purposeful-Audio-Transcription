# API changelog and deprecation (v1)

Canonical product contract: **`/api/v1/*`**.  
Legacy **`/api/*`** remains for Streamlit admin/eval until retired.

## Schema version

Envelope fields use `schema_version: "1"` where present. Breaking response shape changes require a new major (`/api/v2`) or an explicit migration note below.

## Deprecation strategy

1. Announce in this changelog (minimum one release band).
2. Keep legacy path working with `deprecated: true` in OpenAPI and/or `X-Deprecated-Endpoint` headers where already used.
3. React must not call deprecated legacy-only paths for new features.
4. Remove only after Streamlit/admin consumers are migrated or retired.

## Changelog

### v1.4

- Added: `GET /api/v1/modules`, `GET /api/v1/modules/lifecycle`
- Added: `GET /api/v1/workflow-runs/{run_id}/knowledge-graph`
- Added: `GET /api/v1/workflow-runs/{run_id}/structured-graph`
- Added: `POST /api/v1/cases/{case_id}/longitudinal-synthesis`
- Added: `POST /api/v1/exploration/compare-transcripts`
- Added: `GET /api/v1/transcripts/{transcript_id}/workflow-runs`
- Added: `DELETE /api/v1/cases/{case_id}`
- CI: OpenAPI `/api/v1` path snapshot + legacy coexistence test

### v1.3

- Expanded transcripts prepare surface, cases CRUD/assign, workflows/reports/feedback under `/api/v1`

### v1.2

- Introduced `/api/v1` for React readiness; error envelope `{ error_code, message, request_id, details }`

## Typed client

Hand-maintained TypeScript client: `frontend-react/src/api/client.ts`.  
Optional regeneration: export OpenAPI and run `openapi-typescript` (see [supply_chain.md](supply_chain.md)). Snapshot path list: `tests/snapshots/openapi_v1_paths.json`.
