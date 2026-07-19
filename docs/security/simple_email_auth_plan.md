# Simple Email Authentication Plan

## Purpose

This document defines the early authentication plan for controlled usage.

The goal is to remove reliance on shared React API keys and introduce simple user identity and ownership controls while preserving an upgrade path to Google, Okta, SAML, OIDC, and enterprise SSO later.

---

# Recommended Approach

Use passwordless email authentication:

```text
User enters email
→ backend sends one-time code or magic link
→ user verifies code/link
→ backend creates session
→ React uses secure session cookie
→ API identifies current user
```

Preferred initial implementation:

```text
email + one-time code
```

---

# Initial Data Model

## User

```text
id
email
display_name
created_at
last_login_at
is_active
is_admin
```

## LoginCode

```text
id
email
code_hash
expires_at
used_at
attempt_count
created_at
request_ip_hash
```

## UserSession

```text
id
user_id
session_token_hash
created_at
expires_at
revoked_at
last_seen_at
user_agent_hash
ip_hash
```

## AuditEvent

```text
id
actor_user_id
event_type
resource_type
resource_id
metadata_json
created_at
```

Future entities:

```text
Organization
OrganizationMembership
Role
IdentityProviderAccount
```

---

# API Endpoints

Recommended endpoints:

```text
POST /api/v1/auth/request-code
POST /api/v1/auth/verify-code
POST /api/v1/auth/logout
GET  /api/v1/auth/me
```

Optional:

```text
POST /api/v1/auth/resend-code
POST /api/v1/auth/revoke-all-sessions
GET  /api/v1/auth/sessions
```

---

# Session Strategy

For React/browser usage, prefer an HTTP-only secure cookie.

Recommended cookie attributes:

```text
HttpOnly
Secure
SameSite=Lax or Strict
Path=/
Max-Age=<session duration>
```

Avoid storing long-lived tokens in localStorage.

---

# Early Access Control

Protected resources should include ownership checks:

- transcripts
- transcript versions
- evidence
- workflow runs
- module runs
- reports
- cases
- exports
- finding feedback
- evaluation runs if user-specific

Basic rule:

```text
resource.owner_user_id == current_user.id
```

---

# Future Enterprise Auth Path

Design the user model so external providers can be added later.

Future providers:

- Google
- Microsoft Entra ID
- Okta
- Auth0
- SAML/OIDC enterprise identity providers

Future features:

- organization accounts
- domain-based membership
- RBAC
- SSO enforcement
- SCIM provisioning
- audit exports

---

# Acceptance Criteria

- User can request a login code by email.
- User can verify code and create a session.
- React can identify the current user.
- Protected API routes require authentication.
- Users cannot access resources owned by another user.
- Sessions can be revoked/logout works.
- Existing API-key auth is limited to internal/dev/admin usage.
- Future SSO integration path is documented.
