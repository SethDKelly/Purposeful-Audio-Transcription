# Auth and RBAC plan (v1.4)

Planning document only — no multi-user auth implementation in v1.4.

## Current model (dev / UAT)

| Layer | Mechanism |
|-------|-----------|
| Edge | Optional ACM HTTPS on ALB |
| API | Shared `X-API-Key` from Secrets Manager |
| React | `VITE_API_KEY` at build/runtime (same key) |
| Streamlit admin | Same API key via env / Secrets |

This is a **single shared secret**, not per-user identity. Adequate for private UAT; **not** for external multi-user or shared practice workspaces.

## Target access models (evaluate in order)

1. **Authenticated individual** — Cognito (or equivalent) user pool; JWT → API; cases owned by `user_id`.
2. **Therapist / coach workspace** — workspace membership; cases belong to workspace; roles: owner, clinician, viewer.
3. **Organization / team** — org → workspaces; billing/admin separate from clinical roles.
4. **Case sharing** — explicit grants (viewer/reviewer) with audit; no public links by default.
5. **Reviewer / admin** — eval golden review, module lifecycle, delete/export without owning cases.

## Sensitive data rules

- Case/transcript/report rows are confidential by default.
- Exports inherit redaction defaults; delete is cascade for transcript-linked artifacts.
- Logs must remain redacted (see [log-redaction.md](../developer/log-redaction.md)).
- No AWS credentials or DB URLs in any frontend bundle.

## Implementation path (post–v1.4)

1. Introduce `subject_id` on Case / Transcript (nullable during migration).
2. Replace shared API key for product UI with Cognito JWT; keep API key for worker-to-API or break-glass admin if needed.
3. Enforce ownership checks in FastAPI dependencies before case/transcript reads.
4. Add audit events for share/delete/export.
5. Only then enable collaborator invites.

## Decision for v1.4 exit

Ship with documented single-key UAT model + this roadmap. Block broad external multi-user use until Cognito (or equivalent) lands.
