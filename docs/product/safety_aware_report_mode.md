# Safety-Aware Report Mode (v1.0 Priority 5) — **Shipped in v1.0**

The app must not diagnose or adjudicate abuse, but it should respond carefully when transcripts contain high-risk content (threats, coercion, intimidation, self-harm, stalking, severe control, etc.). Roadmap: [../planning/roadmap_v0.7_to_v1.0.md](../planning/roadmap_v0.7_to_v1.0.md). Design: [../design/14_testing_evaluation_and_safety.md](../design/14_testing_evaluation_and_safety.md).

## Capabilities (shipped)

- High-risk scan via `SafetyRiskScanner` (`GET /api/transcripts/{id}/safety-assessment`)
- `safety_mode` on workflow runs (auto on high risk, or request flag)
- Safety-aware UI banner
- Synthesis framing shifts away from mutual coaching under safety mode
- Skips exploratory modules (`exploratory_psychological_formulation`, `narrative_identity_analysis`) when safety mode is active

## Acceptance

High-risk transcripts trigger stronger caution language; reports stay evidence-limited and non-adjudicative; safety mode alters recommendations appropriately.

## Non-goals

Legal determination, clinical diagnosis, or mandatory reporting automation beyond clear user-facing guidance.
