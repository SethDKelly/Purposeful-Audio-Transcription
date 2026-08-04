# RRE React frontend

Vite + React + TypeScript client for `/api/v1`.

## Prerequisites

- **Node.js 22** — matches CI (`node-version: "22"`) and this image (`FROM node:22-bookworm-slim`).
- Commit lockfile changes with `package-lock.json`. Prefer `npm ci` when matching CI.

## Local

```bash
cd frontend-react
cp .env.example .env
npm ci          # or npm install when bootstrapping
npm run dev
```

With API on `:8000`, leave `VITE_API_BASE_URL` empty so Vite proxies `/api`.

## Scripts

- `npm run dev` — Vite
- `npm run build` — production build (`tsc -b` + Vite)
- `npm run lint` — oxlint
- `npm run test` — Vitest
- `npm run test:e2e` — Playwright smoke

## CI

Path-filtered workflow: [`.github/workflows/frontend-react.yml`](../.github/workflows/frontend-react.yml) — `npm ci`, Vitest, production build, Playwright e2e.

Dependency audit: [`.github/workflows/supply-chain.yml`](../.github/workflows/supply-chain.yml) (`npm audit --audit-level=high`).

See [docs/developer/supply_chain.md](../docs/developer/supply_chain.md) for lockfiles, Node pins, and Actions Dependabot review notes.

## Docker

```bash
docker build -t rre-dev-web ./frontend-react
```

Serve static assets on port 80 (nginx). Route ALB `/` to this service and `/api` to the API service, or set `VITE_API_BASE_URL` to the public API origin at build time.
