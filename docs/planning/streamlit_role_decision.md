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
- React image: `frontend-react/Dockerfile` → planned ECR `rre-dev-web`.
- Cutover runbook: deploy web → ALB default → React; route `/admin*` (or keep separate URL) to Streamlit; document DNS.
- Terraform may provision web at `desired_count = 0` until the first cutover.

## Exit criteria met

Streamlit role is explicit; duplicate product UX is discouraged; React owns the primary journey locally and in planning docs.
