# Auth and idle power control

Operational runbook for passwordless email sessions, ownership RBAC, and middle-depth idle power control.

> Documents the v2.1 auth/power deploy path landing via `pre-production` (PR #16). Verified against that codebase (`backend/api/routes/auth.py`, `power.py`, `infra/lambda/power_control/`, deploy/pause workflows).

## Intent

- Identify real users without shipping public React API keys.
- Scope case/transcript/run access by ownership (`owner_user_id`).
- Keep a cheap idle footprint: tear down ECS, RDS compute, and VPC endpoints while leaving the ALB up so `/login` can wake the stack.

## Auth model (when awake)

| Mode | Who | Mechanism |
|------|-----|-----------|
| Session (product) | Invite-only users | Email OTP → HTTP-only `rre_session` cookie |
| Break-glass | Worker / ops | Shared `X-API-Key` (Secrets Manager on ECS) |
| Admin RBAC | `users.is_admin=true` | Normal user capabilities **plus** ownership bypass and admin routes |

Seeded admin (migration `017`): `ollioxenhomefree@gmail.com` (`is_admin=true`, also a normal user).

**Invite-only:** `AUTH_INVITE_ONLY=true` (AWS default). Unknown or inactive emails get a generic OK on code request (anti-enumeration); no code is sent.

### Session endpoints (API / ECS)

| Method | Path | Notes |
|--------|------|-------|
| `POST` | `/api/v1/auth/request-code` | Body `{ "email" }` — public |
| `POST` | `/api/v1/auth/verify-code` | Body `{ "email", "code" }` — sets session cookie |
| `POST` | `/api/v1/auth/logout` | Revokes session; clears cookie |
| `GET` | `/api/v1/auth/me` | Current user or `401` |

### Gate behavior

When `SESSION_AUTH_REQUIRED=true` and/or `API_KEY` is set (`backend/api/middleware.py`):

- Public: `/`, `/docs`, `/openapi.json`, `/api/live`, `/api/health`, `/api/v1/auth/*`, `/api/v1/ops/power/status`, `/api/v1/ops/power/handoff`
- Everything else needs a valid session cookie **or** matching `X-API-Key`
- Authenticated traffic touches the idle activity clock (`power_state_store.touch_activity`)

Ownership helpers: `backend/api/ownership.py` — session admins and API-key admins bypass; legacy rows with `owner_user_id=null` remain readable.

### Local / pytest

| Variable | Typical local / pytest | AWS ECS |
|----------|------------------------|---------|
| `SESSION_AUTH_REQUIRED` | `false` | `true` |
| `AUTH_INVITE_ONLY` | forced `false` in tests | `true` |
| `EMAIL_DELIVERY` | `dev_log` | `ses` |
| `SES_FROM_EMAIL` | unused | verified SES identity |
| `API_KEY` | empty or test value | Secrets Manager |

See `.env.example`. Coverage: `tests/test_phase_003_email_auth.py`, `tests/test_auth_rbac_and_power.py`.

## Power control (middle idle depth)

### States

`asleep` → `waking` → `awake` → (`sleeping`) → `asleep`

Stored in DynamoDB `rre-dev-power-state` (`pk=POWER#STATE`).

| Mode | What happens |
|------|----------------|
| **Sleep** | ECS desired **0**; **delete** Interface + S3 gateway VPC endpoints; **stop** RDS; **keep ALB** |
| **Wake** | CodeBuild orchestrator: start RDS → recreate endpoints → scale ECS |
| **Idle timer** | After **2h** with no active jobs and no authenticated activity → sleep (EventBridge idle checker) |
| **Kill mode** | `KILL_LONG_JOBS_ENABLED=true` (default): any job > **3h** cancels all jobs and starts the idle timer |

### Asleep path (ALB → Lambda)

While ECS is down, ALB priority rules forward these to the power-control Lambda (`infra/lambda/power_control/handler.py`):

| Method | Path | Role |
|--------|------|------|
| `GET` | `/login` | HTML wake / sign-in page |
| `GET` | `/api/v1/ops/power/status` | Power state (DynamoDB) |
| `POST` | `/api/v1/ops/power/auth/request-code` | OTP via SES (DynamoDB invite list) |
| `POST` | `/api/v1/ops/power/auth/verify-code` | Starts CodeBuild wake; returns `handoff_token` |
| `POST` | `/api/v1/ops/power/wake` | Idempotent wake |

### Awake path (API)

| Method | Path | Auth | Role |
|--------|------|------|------|
| `GET` | `/api/v1/ops/power/status` | Public | Status + idle fields |
| `GET` | `/api/v1/ops/power/idle-status` | Admin | Idle checker payload |
| `POST` | `/api/v1/ops/power/heartbeat` | Session / API key | Touch activity |
| `POST` | `/api/v1/ops/power/handoff` | Public (signed token) | Exchange wake handoff → Postgres session cookie |
| `POST` | `/api/v1/ops/power/start-idle-timer` | Admin | Begin idle countdown |

Handoff tokens are HMAC-signed with `POWER_HANDOFF_SECRET` (TTL ~15 minutes). After wake, the UI redirects with `?handoff=` and the API mints a normal session.

### Operator actions

| Action | How |
|--------|-----|
| Wake | Open ALB `/login`, complete OTP |
| Sleep (manual) | Actions → **Pause AWS dev** (also deletes VPC endpoints) |
| Resume (break-glass) | **Deploy to AWS dev** or push `v*.*.*` |

Cold start is often **5–15+ minutes**. Next full terraform apply recreates VPC endpoints if sleep deleted them.

## Deploy configuration

| Knob | Where | Notes |
|------|-------|-------|
| `ses_from_email` | Terraform / Deploy workflow | Must be a **verified SES** identity in `us-east-2` |
| `SES_FROM_EMAIL` | GitHub Actions variable (optional) | Deploy passes `-var=ses_from_email=…`; default/CI fallback `ollioxenhomefree@gmail.com` |
| `enable_power_control` | Terraform | DynamoDB, Lambda, CodeBuild, ALB rules |
| `SESSION_AUTH_REQUIRED` | ECS task env | `true` on API |
| `EMAIL_DELIVERY=ses` | ECS task env | API OTP when awake |

## Troubleshooting

| Symptom | Likely cause | Check |
|---------|--------------|-------|
| No OTP email | Unverified / wrong `ses_from_email`; invite-only miss | SES identity; DynamoDB `USER#email` + RDS `users` row; CloudWatch Lambda logs |
| Generic “code sent” but nothing arrives | Invite-only skip (by design) | Seed user in Postgres **and** power-state table for asleep wake |
| Stuck on `waking` | CodeBuild / RDS / endpoints | CodeBuild `rre-dev-power-orchestrator` logs; RDS status; VPC endpoints present |
| `401` after wake | Handoff expired or secret mismatch | Complete `/login` again; confirm API `POWER_HANDOFF_SECRET` matches Lambda |
| Idle never sleeps | Active jobs or activity heartbeats | `GET /api/v1/ops/power/status` → `active_jobs`, `idle_for_seconds` |
| VPC endpoint charges while paused | Pause didn’t delete endpoints | Re-run **Pause AWS dev**; confirm no `rre-dev-*` endpoints |

## Related

- Ops summary: [aws-operations.md](aws-operations.md)
- Infra notes: [../../infra/dev/README.md](../../infra/dev/README.md)
- API tables: [api-reference.md](api-reference.md)
- AWS architecture: [../planning/aws-deployment.md](../planning/aws-deployment.md)
