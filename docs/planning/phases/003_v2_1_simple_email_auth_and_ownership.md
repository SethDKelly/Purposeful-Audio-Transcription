# 003 — Simple Email Auth and Ownership

## Phase Goal

Add simple user login through email and basic ownership checks for sensitive resources.

This enables controlled pilots without jumping directly to Google, Okta, SAML, OIDC, or enterprise SSO.

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

# Minimal Data Model

```text
User
LoginCode
UserSession
AuditEvent
```

Future, not now:

```text
Organization
Membership
Role
IdentityProviderAccount
```

---

# API Endpoints

Implement:

```text
POST /api/v1/auth/request-code
POST /api/v1/auth/verify-code
POST /api/v1/auth/logout
GET  /api/v1/auth/me
```

Optional:

```text
POST /api/v1/auth/resend-code
GET  /api/v1/auth/sessions
POST /api/v1/auth/revoke-all-sessions
```

---

# Protected Resource Ownership

Add ownership checks for:

- transcripts
- transcript versions, when implemented
- cases
- workflow runs
- reports
- exports
- finding feedback
- evaluation runs where user-specific

Basic rule:

```text
resource.owner_user_id == current_user.id
```

---

# Implementation Tasks

## Backend

- [ ] Add `User` model.
- [ ] Add `LoginCode` or `MagicLinkToken` model.
- [ ] Add `UserSession` model.
- [ ] Add auth service.
- [ ] Add email delivery abstraction.
- [ ] Add dev-mode email/code logging.
- [ ] Add rate limiting for login code requests.
- [ ] Add session cookie support.
- [ ] Add current-user dependency.
- [ ] Add ownership checks to protected routes.
- [ ] Add audit events for login/logout.

## React

- [ ] Add login page.
- [ ] Add code verification page/state.
- [ ] Add `/auth/me` startup check.
- [ ] Add logout.
- [ ] Add account/settings display.
- [ ] Remove user-facing reliance on shared API key.
- [ ] Preserve internal/dev API-key path only where appropriate.

## Tests

- [ ] Login code request test.
- [ ] Verify code test.
- [ ] Expired code test.
- [ ] Reused code test.
- [ ] Logout test.
- [ ] Ownership denial test.
- [ ] Cross-user transcript access denied.
- [ ] Cross-user report access denied.
- [ ] Cross-user case access denied.

---

# Acceptance Criteria

- A user can log in by email.
- React can identify the current user.
- Protected API routes require authentication.
- Users cannot access another user's transcripts, reports, cases, or exports.
- Sessions can be revoked by logout.
- Existing API-key auth is limited to internal/dev/admin usage.
- Docs clearly state that Google/Okta/enterprise SSO is future work.
