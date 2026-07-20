# 007 — Safety Policy and Non-Diagnostic Enforcement

## Phase Goal

Make safety-aware framing configurable and enforce stricter non-diagnostic discipline.

**Status:** Complete · Tests: `tests/test_phase_007_safety_policy.py` · Policy: `config/safety_policy.yaml`

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

Shipped config also suppresses `narrative_identity_analysis` (existing safety-mode behavior).

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

- [x] Add safety policy YAML/config.
- [x] Move module suppression/modification rules into config.
- [x] Define elevated-risk and high-risk behavior.
- [x] Add policy docs.

## Validator

- [x] Tighten forbidden-claim detection.
- [x] Distinguish quoted text from model claim.
- [x] Force lower confidence or repair for risky claims.
- [x] Block definitive diagnostic/adjudicative outputs.

## Prompting

- [x] Add safety-aware framing instructions.
- [x] Add non-diagnostic language instructions.
- [x] Add “do not mutualize serious concerns” instruction.

## Reports

- [x] Add safety-aware report banner.
- [x] Add limitations where needed.
- [x] Avoid ordinary conflict-coaching framing for high-risk cases.

## Evaluation

- [x] Add tests for elevated-risk safety mode.
- [x] Add tests for high-risk safety mode.
- [x] Add tests for false positives.
- [x] Add tests for forbidden diagnostic/manipulation/abuse claims.
- [x] Add tests for mutualizing serious concerns.

---

# Acceptance Criteria

- Safety mode is config-driven.
- Elevated risk can trigger safety-aware framing.
- High risk always triggers safety-aware framing.
- Definitive diagnostic/adjudicative claims are blocked or downgraded.
- Safety red-team fixtures pass.
- Reports avoid mutualizing serious concerns.
