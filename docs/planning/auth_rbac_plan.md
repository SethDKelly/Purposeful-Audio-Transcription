# Auth and RBAC plan

Living access-model plan. **Near-term implementation:** [phases/003](phases/003_v2_1_simple_email_auth_and_ownership.md) · [simple_email_auth_plan.md](../security/simple_email_auth_plan.md) · [ADR 001](../developer/architecture_decisions/adr_001_simple_email_auth_before_enterprise_sso.md).

## Current model (dev / UAT)

| Layer | Mechanism |
|-------|-----------|
| Edge | Optional ACM HTTPS on ALB |
| API | Shared `X-API-Key` from Secrets Manager |
| React | `VITE_API_KEY` at build/runtime (same key) |
| Streamlit admin | Same API key via env / Secrets |

This is a **single shared secret**, not per-user identity. Adequate for private UAT; **not** for external multi-user or shared practice workspaces.

## Near-term target (v2.1 phase 003) — email OTP first

Per **ADR 001**, implement passwordless email login before Cognito/enterprise SSO:

```text
email → one-time code → secure session cookie → authenticated API
```

| Concern | Choice |
|---------|--------|
| Identity | `User` row keyed by email |
| Ownership field | `owner_user_id` on transcripts, cases, runs, reports, exports |
| Product UI auth | Session cookie (HttpOnly); no shared key in user-facing React |
| Break-glass | Keep API key for worker/admin/dev only |
| Audit | Login / logout / ownership denials |

Do **not** start with Cognito, Google, Okta, SAML, or OIDC for this phase.

## Longer-term access models (evaluate in order after 003)

1. **Authenticated individual** — email sessions (shipped in 003); later optional IdP link.
2. **Therapist / coach workspace** — workspace membership; cases belong to workspace; roles: owner, clinician, viewer.
3. **Organization / team** — org → workspaces; billing/admin separate from clinical roles.
4. **Case sharing** — explicit grants (viewer/reviewer) with audit; no public links by default.
5. **Reviewer / admin** — eval golden review, module lifecycle, delete/export without owning cases.
6. **Enterprise SSO** — Cognito / OIDC / SAML as an additional IdP on the same `User` model.

## Sensitive data rules

- Case/transcript/report rows are confidential by default.
- Exports inherit redaction defaults; delete is cascade for transcript-linked artifacts.
- Logs must remain redacted (see [log-redaction.md](../developer/log-redaction.md)).
- No AWS credentials or DB URLs in any frontend bundle.

## Implementation path

### Now (phase 003)

1. Add `User` / `LoginCode` / `UserSession` (or equivalent).
2. Introduce nullable `owner_user_id` on Case / Transcript / related resources; backfill or require on create.
3. Session-cookie auth for React product UI; keep API key for worker/admin.
4. Enforce ownership checks in FastAPI dependencies before case/transcript reads.
5. Audit events for login/logout (share/delete/export when those features land).

### Later (deferred)

1. Cognito / enterprise IdP as optional identity provider.
2. Collaborator invites and workspace RBAC.
3. Fine-grained share grants.

## Decision

Ship controlled pilots with **email OTP + ownership**. Block broad multi-user / enterprise use until IdP and workspace models land. Cognito is **not** the v2.1 MVP.
