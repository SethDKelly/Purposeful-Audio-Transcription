# ADR 001 — Simple Email Authentication Before Enterprise SSO

## Status

Accepted (v2.1 near-term)

## Context

The application is moving from internal/pre-production use toward controlled external usage.

The current React approach may rely on a shared API key for early access. This is acceptable only for local development or tightly controlled internal testing. It is not suitable for real external users because client-side API keys are visible in built assets.

The application will eventually benefit from Google, Okta, SAML, OIDC, or other enterprise authentication. However, implementing enterprise auth immediately may slow progress and over-specialize the product before market focus is clear.

## Decision

Implement simple passwordless email login first.

Use:

```text
email → one-time code or magic link → secure session cookie → authenticated user
```

Design the user model so enterprise identity providers can be added later.

## Consequences

### Positive

- Removes reliance on public shared API keys.
- Adds user identity and resource ownership.
- Supports controlled pilots.
- Avoids password storage.
- Keeps implementation simpler than enterprise SSO.
- Allows later Google/Okta/OIDC integration.

### Negative

- Not enterprise-grade by itself.
- Requires email delivery and rate limiting.
- Does not yet support organization-level RBAC.
- Needs migration path for future SSO.

## Future Direction

Add:

- Google login
- Okta/OIDC
- SAML
- organization memberships
- role-based access
- enterprise admin controls

## Non-Goals

This decision does not implement:

- full enterprise SSO
- SCIM provisioning
- billing identity
- complex RBAC
- organization admin console
