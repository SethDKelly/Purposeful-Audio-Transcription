# CI and GitHub Actions

Map of automated checks and operator workflows in `.github/workflows/`. Verified against the workflow YAML and `.github/dependabot.yml`.

## Workflow inventory

| Workflow file | Actions name | Triggers | What it does |
|---------------|--------------|----------|--------------|
| `deploy-dev.yml` | **Deploy to AWS dev** | `workflow_dispatch` (`component`), tags `v*.*.*` | Full pytest + config guards → OIDC Terraform/ECS deploy + smoke |
| `pause-dev.yml` | **Pause AWS dev** | `workflow_dispatch` | ECS desired 0, delete `rre-dev-*` VPC endpoints, stop RDS, mark power state asleep |
| `eval-release-gates.yml` | Eval release gates | PR, push to `main` / `post-v1.0/**`, tags, manual | OpenAPI v1 contract, golden offline, safety red-team, safety mode |
| `frontend-react.yml` | Frontend React CI | Push/PR when `frontend-react/**` changes | `npm ci`, unit tests, build, Playwright e2e |
| `supply-chain.yml` | Supply chain | Lockfile/package changes, weekly cron | `npm audit --audit-level=high`, `pip-audit` via `uv export` when present |

Ordinary pushes to `main` **do not** deploy. Deploy is tags or manual only (see [aws-deployment.md](aws-deployment.md) §8).

## Local equivalents

| Gate | Local command |
|------|---------------|
| Config / YAML | `python scripts/validate_yaml.py` · `python scripts/validate_config.py` |
| UI/API boundary | `python scripts/check_ui_api_boundary.py` |
| Full pytest (Deploy job) | `python -m pytest tests/ -q` |
| Eval release gates | `python -m pytest tests/test_v1_2_evaluation_api.py tests/test_safety_red_team.py tests/test_safety_mode.py -q` and `python -m pytest tests/ -m "golden and not live_model" -q` |
| Frontend | `cd frontend-react && npm ci && npm run test && npm run build && npm run test:e2e` |
| Supply chain | `cd frontend-react && npm audit --audit-level=high`; `pip-audit` against exported/locked deps |
| Actionlint | via `pre-commit run --all-files` |

## Dependabot

`.github/dependabot.yml` opens weekly PRs (limit 5 each) for:

| Ecosystem | Directory |
|-----------|-----------|
| `npm` | `/frontend-react` |
| `pip` | `/` |
| `github-actions` | `/` |

### Reviewing GitHub Actions bumps

- Prefer major/minor bumps that keep workflows on supported Node runners (checkout / setup-* majors track that).
- This repo’s workflows use `pull_request`, `push`, `workflow_dispatch`, and `schedule` only — **not** `pull_request_target` or `workflow_run`.
- **`actions/checkout` v7** blocks checking out fork PR heads for `pull_request_target` / `workflow_run` unless explicitly opted in. That hardening does **not** change this repo’s current triggers; merging checkout v6→v7 (e.g. Dependabot) is expected to be behavior-neutral here.
- Sibling Dependabot PRs may bump `actions/setup-node` / `actions/setup-python` separately; keep versions consistent across workflows when landing several at once.
- After Actions bumps: confirm `actionlint` (pre-commit) and a green run of Eval release gates + Frontend CI (path-filtered) / Deploy dry paths as applicable.

## Deploy / Pause notes

- Deploy passes Terraform `ses_from_email` from Actions variable `SES_FROM_EMAIL` when set (verified SES identity required for OTP).
- Pause is the manual sleep path for middle idle depth; product wake is ALB `/login` — see [auth-and-power.md](auth-and-power.md).
- OIDC role: `arn:aws:iam::521018312783:role/dev-github-deploy` (`us-east-2`).

## Related

- Lockfiles / SBOM: [supply_chain.md](supply_chain.md)
- Deploy architecture: [aws-deployment.md](aws-deployment.md)
- Day-to-day ops: [aws-operations.md](aws-operations.md)
- Auth wake path: [auth-and-power.md](auth-and-power.md)
