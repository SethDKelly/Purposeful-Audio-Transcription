# RRE React frontend

Vite + React + TypeScript client for `/api/v1`.

## Local

```bash
cd frontend-react
cp .env.example .env
npm install
npm run dev
```

With API on `:8000`, leave `VITE_API_BASE_URL` empty so Vite proxies `/api`.

## Scripts

- `npm run dev` — Vite
- `npm run build` — production build
- `npm run test` — Vitest
- `npm run test:e2e` — Playwright smoke

## Docker

```bash
docker build -t rre-dev-web ./frontend-react
```

Serve static assets on port 80 (nginx). Route ALB `/` to this service and `/api` to the API service, or set `VITE_API_BASE_URL` to the public API origin at build time.
