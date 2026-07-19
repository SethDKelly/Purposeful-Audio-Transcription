# 007 — Safety Policy and Non-Diagnostic Enforcement

## Phase Goal

Make safety-aware framing configurable and enforce stricter non-diagnostic discipline.

---

# Target Safety Policy

Create a configurable policy:

```yaml
safety_policy:
  elevated_risk_triggers_safety_mode: true
  high_risk_triggers_safety_mode: true
  require_safety_framing: true
  prohibit_mutualizing_serious_concerns: true
  suppress_modules:
    - exploratory_psychological_formulation
  modify_modules:
    - trauma_informed_communication
    - attachment_interaction_matrix
```

---

# Required Behavior

The app should avoid:

- definitive diagnosis
- personality disorder determinations
- narcissism labels
- abuse determinations as settled fact
- intentional manipulation determinations
- trauma history claims
- fixed attachment style claims
- mutualizing serious safety concerns
- reconciliation pressure in high-risk contexts

The app may say:

- the transcript contains safety-relevant indicators
- this may warrant careful review
- more context is needed
- consider appropriate professional or emergency support when relevant

---

# Implementation Tasks

## Policy Config

- [ ] Add safety policy YAML/config.
- [ ] Move module suppression/modification rules into config.
- [ ] Define elevated-risk and high-risk behavior.
- [ ] Add policy docs.

## Validator

- [ ] Tighten forbidden-claim detection.
- [ ] Distinguish quoted text from model claim.
- [ ] Force lower confidence or repair for risky claims.
- [ ] Block definitive diagnostic/adjudicative outputs.

## Prompting

- [ ] Add safety-aware framing instructions.
- [ ] Add non-diagnostic language instructions.
- [ ] Add “do not mutualize serious concerns” instruction.

## Reports

- [ ] Add safety-aware report banner.
- [ ] Add limitations where needed.
- [ ] Avoid ordinary conflict-coaching framing for high-risk cases.

## Evaluation

- [ ] Add tests for elevated-risk safety mode.
- [ ] Add tests for high-risk safety mode.
- [ ] Add tests for false positives.
- [ ] Add tests for forbidden diagnostic/manipulation/abuse claims.
- [ ] Add tests for mutualizing serious concerns.

---

# Acceptance Criteria

- Safety mode is config-driven.
- Elevated risk can trigger safety-aware framing.
- High risk always triggers safety-aware framing.
- Definitive diagnostic/adjudicative claims are blocked or downgraded.
- Safety red-team fixtures pass.
- Reports avoid mutualizing serious concerns.
