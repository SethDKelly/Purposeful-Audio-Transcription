# Streamlit role decision (v1.4)

## Decision

**Keep Streamlit as an internal admin / eval / golden-review console.**  
**React (`frontend-react/`) is the primary product UI.**

This is option **2 + 3** from the v1.4 plan (admin console + eval console), not full retirement yet.

## Implications

| Surface | Owner |
|---------|--------|
| Ingest → prepare → analyze → report → graph → cases | React |
| Golden eval review, ad-hoc ops debugging, legacy explorers | Streamlit |
| New product features | React only (`/api/v1`) |

Do not add new end-user product workflows only in Streamlit.

## Deployment

- Current ALB default target remains Streamlit (`rre-dev-ui`) until React web service is cut over.
- React image: `frontend-react/Dockerfile` → ECR `rre-dev-web` (Terraform repo + ECS at `web_desired_count` default 0).
- Cutover checklist:
  1. Build/push web image tagged with git SHA.
  2. Set `web_desired_count = 1` and apply Terraform.
  3. Point ALB default action at web `:80`; route `/admin*` to Streamlit.
  4. Smoke React ingest→report and Streamlit eval reachability.

## Exit criteria met

Streamlit role is explicit; duplicate product UX is discouraged; React owns the primary journey locally and in planning docs.
