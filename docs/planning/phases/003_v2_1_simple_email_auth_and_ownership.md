# 003 — Simple Email Auth and Ownership

## Phase Goal

Add simple user login through email and basic ownership checks for sensitive resources.

This enables controlled pilots without jumping directly to Google, Okta, SAML, OIDC, or enterprise SSO.

**Status:** Complete · Tests: `tests/test_phase_003_email_auth.py`

**Design:** [../../security/simple_email_auth_plan.md](../../security/simple_email_auth_plan.md) · [ADR 001](../../developer/architecture_decisions/adr_001_simple_email_auth_before_enterprise_sso.md) · [../auth_rbac_plan.md](../auth_rbac_plan.md)

---

# Recommended Auth Model

Use passwordless email login:

```text
email address
→ one-time code or magic link
→ secure session cookie
→ authenticated API requests
```

Preferred initial implementation:

```text
email + one-time code
```

---

# Implementation Tasks

## Backend

- [x] Add `User` model.
- [x] Add `LoginCode` model.
- [x] Add `UserSession` model.
- [x] Add auth service.
- [x] Add email delivery abstraction (`DevLogEmailDelivery`).
- [x] Add dev-mode email/code logging.
- [x] Add rate limiting for login code requests.
- [x] Add session cookie support.
- [x] Add current-user dependency / auth context.
- [x] Add ownership checks to protected `/api/v1` routes.
- [x] Add audit events for login/logout (and ownership denials).
- [x] Alembic `013_email_auth_and_ownership`.

## React

- [x] Add login page.
- [x] Add code verification step.
- [x] Add `/auth/me` startup check (AppShell).
- [x] Add logout.
- [x] Add account display (Settings).
- [x] Remove user-facing reliance on shared API key (docs + settings copy).
- [x] Preserve internal/dev API-key path only where appropriate (`VITE_API_KEY` optional).

## Tests

- [x] Login code request test.
- [x] Verify code test.
- [x] Expired code test.
- [x] Reused code test.
- [x] Logout test.
- [x] Ownership denial test.
- [x] Cross-user transcript access denied.
- [x] Cross-user report/run access denied.
- [x] Cross-user case access denied.

---

# Acceptance Criteria

- [x] A user can log in by email.
- [x] React can identify the current user.
- [x] Protected API routes require authentication when `SESSION_AUTH_REQUIRED=true`.
- [x] Users cannot access another user's transcripts, reports, cases, or exports.
- [x] Sessions can be revoked by logout.
- [x] Existing API-key auth is limited to internal/dev/admin usage.
- [x] Docs clearly state that Google/Okta/enterprise SSO is future work.

## Ops notes

- Set `SESSION_AUTH_REQUIRED=true` for product React deployments.
- Login codes are logged via `DevLogEmailDelivery` until a real mailer is wired.
- Cookie: `rre_session` (HttpOnly).
