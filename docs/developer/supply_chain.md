# Supply chain and reproducibility (v1.4)

## Lockfiles

| Ecosystem | Lockfile |
|-----------|----------|
| Python | `uv.lock` (preferred) / project metadata in `pyproject.toml` |
| React | `frontend-react/package-lock.json` |
| Terraform | provider constraints in `infra/dev/versions.tf` |

Always commit lockfiles. Do not commit `node_modules/`, `dist/`, `.terraform/`, `__pycache__/`, or Playwright `test-results/`.

## Scanning

- **Dependabot** — `.github/dependabot.yml` for npm, pip, and GitHub Actions.
- **CI** — `.github/workflows/supply-chain.yml` runs `npm audit` (frontend) and `pip-audit` when available.
- **ECR** — image scanning on push enabled for API/UI (and web when provisioned).

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
2. Build React with locked deps: `npm ci && npm run build`.
3. Build API/UI from repo Dockerfiles without floating `latest` base tags when possible.
4. Record Bedrock model IDs and module prompt sha256 (see `/api/v1/modules/lifecycle`) for eval reproducibility.
