## Summary

<!-- What changed and why -->

## Test plan

- [ ] `python -m pytest tests/ -q` passes (or targeted suite for this PR)
- [ ] No secrets in diff

## Tenet review

Does this change strengthen the Relationship Reasoning Engine as an evidence-linked, confidence-calibrated, non-diagnostic, multi-lens structured reasoning platform?

Full checklist: [docs/developer/pr_review_tenet_checklist.md](docs/developer/pr_review_tenet_checklist.md)

- [ ] **Evidence** — claims cite concise quote IDs; old reports stay valid after edits
- [ ] **Confidence** — no overstated inferences; alternatives/limitations where relevant
- [ ] **Multi-lens** — module provenance preserved; synthesis does not hide divergence
- [ ] **Non-diagnostic** — no clinical/abuse/personality determinations as fact
- [ ] **Longitudinal** — case evidence stays session/transcript-scoped
- [ ] **Professional fit** — outputs remain reviewable; version metadata preserved
- [ ] **Safety** — serious concerns not mutualized; cautious framing
- [ ] **Graph** — relationships keep type/confidence/rationale/evidence where possible
- [ ] **Auth/privacy** — ownership enforced when touching protected resources; no public API keys for real users

## Market-agnostic check

- [ ] Does **not** hard-code clinician / couples / enterprise / mediation specialization into the core engine
