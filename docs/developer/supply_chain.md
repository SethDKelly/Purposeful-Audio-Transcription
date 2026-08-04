# Supply chain and reproducibility (v1.4)

## Lockfiles

| Ecosystem | Lockfile |
|-----------|----------|
| Python | `uv.lock` (preferred) / project metadata in `pyproject.toml` |
| React | `frontend-react/package-lock.json` |
| Terraform | provider constraints in `infra/dev/versions.tf` |

Always commit lockfiles. Do not commit `node_modules/`, `dist/`, `.terraform/`, `__pycache__/`, or Playwright `test-results/`.

## Node and Python versions in CI

| Surface | Version | Source of truth |
|---------|---------|-----------------|
| React (CI + Docker) | **Node 22** | `.github/workflows/frontend-react.yml`, `supply-chain.yml` (`node-version: "22"`), `frontend-react/Dockerfile` (`node:22-bookworm-slim`) |
| Python (CI) | **3.12** | `supply-chain.yml`, `deploy-dev.yml`, `eval-release-gates.yml` (`python-version: "3.12"`) |
| Local Python tooling | **3.11+** | [development.md](development.md) / `pyproject.toml` |

There is no `engines` field in `frontend-react/package.json`. Treat CI and the frontend Dockerfile as the Node pin. Use `npm ci` (not bare `npm install`) when reproducing CI.

### Frontend CI workflow

`.github/workflows/frontend-react.yml` runs on changes under `frontend-react/**` (and its own workflow file):

1. `actions/setup-node` with npm cache keyed on `frontend-react/package-lock.json`
2. `npm ci`
3. `npm run test` (Vitest)
4. `npm run build`
5. Playwright Chromium install + `npm run test:e2e`

### Supply-chain workflow

`.github/workflows/supply-chain.yml` runs on lockfile/manifest changes and weekly (`cron: "0 14 * * 1"`):

| Job | What it does |
|-----|----------------|
| `npm-audit` | Node 22 + `npm ci`, then `npm audit --audit-level=high` |
| `pip-audit` | Python 3.12; prefers `uv export` from `uv.lock`, else editable install + `pip-audit` |

## Scanning

- **Dependabot** — `.github/dependabot.yml` for npm (`/frontend-react`), pip (`/`), and GitHub Actions (`/`), weekly, max 5 open PRs each.
- **CI** — `supply-chain.yml` as above; frontend quality gates in `frontend-react.yml`.
- **ECR** — image scanning on push enabled for API/UI (and web when provisioned).

### Reviewing GitHub Actions Dependabot bumps

Actions majors (for example `actions/setup-node`, `actions/checkout`, `actions/setup-python`) are bumped by Dependabot. When reviewing:

1. Confirm the PR only touches workflow `uses:` pins (or expected action inputs).
2. Re-read release notes for breaking input/output changes — especially cache keys and auth-related env vars.
3. Keep `node-version: "22"` / `python-version: "3.12"` unless the bump explicitly requires a runtime change.
4. Rely on `actionlint` (pre-commit) plus the path-filtered workflow runs on the PR.
5. Do not mix Actions bumps with application code in the same PR.

Document Node/Python **runtime** pins here; do not hard-code Actions major tags in docs — Dependabot owns those.

## SBOM

Generate on demand for release candidates:

```bash
# Python (example)
pip install cyclonedx-bom
cyclonedx-py environment -o sbom-python.json

# Frontend
cd frontend-react && npx @cyclonedx/cyclonedx-npm --output-file sbom-frontend.json
```

Do not commit generated SBOMs unless attaching to a release artifact.

## Pre-commit / lint

`.pre-commit-config.yaml` enforces EOF, YAML, ruff, actionlint, registry checks.  
Frontend: `npm run lint` (oxlint), Vitest, Playwright smoke.

## Reproducible builds

1. Pin image tags to git SHA in deploy (`image_tag`).
2. Build React with locked deps on Node 22: `npm ci && npm run build` (same as CI / `frontend-react/Dockerfile`).
3. Build API/UI from repo Dockerfiles without floating `latest` base tags when possible.
4. Record Bedrock model IDs and module prompt sha256 (see `/api/v1/modules/lifecycle`) for eval reproducibility.
