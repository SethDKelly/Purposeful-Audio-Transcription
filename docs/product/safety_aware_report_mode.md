# Safety-Aware Report Mode — **Shipped; phase 007 config-hardened**

The app must not diagnose or adjudicate abuse, but it should respond carefully when transcripts contain high-risk content (threats, coercion, intimidation, self-harm, stalking, severe control, etc.).

**Tenets:** Implements **safety-aware framing** and **non-diagnostic discipline** from [core_tenets.md](core_tenets.md). Policy config: [../planning/phases/007_v2_1_safety_policy_and_non_diagnostic_enforcement.md](../planning/phases/007_v2_1_safety_policy_and_non_diagnostic_enforcement.md). Evaluation: [../evaluation/tenet_compliance_evaluation_plan.md](../evaluation/tenet_compliance_evaluation_plan.md).

## Config-driven policy

`config/safety_policy.yaml` controls:

| Setting | Default behavior |
|---------|------------------|
| `elevated_risk_triggers_safety_mode` | true — coercion/stalking/control recommend safety mode |
| `high_risk_triggers_safety_mode` | true — threats/self-harm recommend safety mode |
| `suppress_modules` | exploratory formulation + narrative identity |
| `modify_modules` | trauma-informed + attachment matrix get safety overlays |
| `prohibit_mutualizing_serious_concerns` | true |

Loader: `backend/services/safety_policy.py`.

## Capabilities

- High-risk scan via `SafetyRiskScanner` (`GET /api/transcripts/{id}/safety-assessment`)
- `safety_mode` on workflow runs (auto on elevated/high per policy, or request flag)
- Safety-aware UI / report package banner (`safety_banner.md`)
- Synthesis + module framing under safety mode
- Skips suppress-list modules; overlays modify-list modules
- Harder runtime `SafetyValidator` blocks definitive diagnostic/adjudicative/mutualizing claims (quoted evidence spans ignored)

## Acceptance

Elevated and high-risk transcripts trigger safety-aware framing; reports stay evidence-limited and non-adjudicative; definitive diagnoses and mutualized serious concerns are blocked or repaired.

## Non-goals

Legal determination, clinical diagnosis, or mandatory reporting automation beyond clear user-facing guidance.
