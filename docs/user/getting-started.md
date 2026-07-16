# Getting started

Operator path from a paused stack to your first workflow report on **AWS**.

## What you need

| Requirement | Notes |
|-------------|-------|
| Access to this GitHub repo | Deploy / Pause workflows via OIDC |
| AWS account `521018312783` | Region `us-east-2` |
| Bedrock model access | Claude (see [model-setup.md](model-setup.md)) |

No local Whisper, Ollama, ffmpeg, or Hugging Face token is required for product use.

## Deploy

1. In GitHub Actions, run **Deploy to AWS dev** (`workflow_dispatch`), or push a version tag such as `v0.8.0`.
2. Wait for ECS services healthy (workflow summary includes ALB URL tips).
3. Open the Streamlit UI via the ALB (see [aws-operations.md](../developer/aws-operations.md)).

Ordinary commits to `main` do **not** auto-deploy. When finished, run **Pause AWS dev**.

## First workflow (5 minutes)

1. Open the UI; sidebar should show API healthy with Bedrock / Transcribe / database available.
2. **Ingest** — paste a short two-speaker transcript or upload audio (Transcribe) / text.
3. **Prepare** — rename speakers if needed; edit or exclude turns; click **Ready to Analyze** (or skip review intentionally).
4. **Analyze** — choose **Quick Review** and the Bedrock model; prefer background for long suites.
5. **Report** — review findings, open **Explore**, export `.md` or `.pdf`.

Workflows require a transcript marked ready for analysis.

## Choose a workflow

| Workflow | Best for | Runtime |
|----------|----------|---------|
| `quick_review` | Fast practical insight | ~1–3 min |
| `full_mvp` | Full analysis + synthesis | ~3–8 min |
| `conflict_coaching` | Needs, coaching tone | ~2–4 min |
| `mediation_brief` | Positions, interests, agreements | ~3–6 min |
| `clinical_exploration` | Deeper exploratory lenses | ~8–15 min |
| `research_oriented` | Pattern study | ~6–15 min |
| `full_multidisciplinary` | All transcript modules | ~15–45 min (background) |

See [user-guide.md](user-guide.md) for details.

## Next steps

- [User guide](user-guide.md) — preparation, exploration, exports, safety notes
- [Model setup](model-setup.md) — Bedrock + Transcribe
- [Deployment](deployment.md) — AWS ops pointers
- [AWS architecture](../planning/aws-deployment.md)
