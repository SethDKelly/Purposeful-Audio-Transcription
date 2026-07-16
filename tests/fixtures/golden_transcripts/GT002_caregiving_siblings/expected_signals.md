# GT002 Expected Signals

## Purpose

Use this file as a human-readable expected-output guide for evaluator/golden tests. These are not rigid answers; they are target signals that good modules should identify.

## Primary Interaction Cycle

Expected high-confidence cycle:

```text
Nina names caregiving failure and role overload
↓
Owen explains assumptions and constraints
↓
Nina experiences explanation as defaulting responsibility back to her
↓
Owen experiences criticism as accusation that he does not care
↓
Both compare contributions: time vs money
↓
Repair begins when each validates the other's contribution
↓
They shift from blame to system design
```

## High-Confidence Findings

- The immediate issue is a missed cardiology appointment.
- There is ambiguity about calendar visibility versus task ownership.
- Nina experiences herself as default coordinator/caregiver.
- Owen experiences his financial contribution as underrecognized.
- Aunt Carla functions as a third-party pressure/triangulation element.
- The conflict shifts from the missed appointment to broader family roles.
- Both participants eventually validate part of the other's perspective.
- A procedural agreement emerges: assign owners, Owen creates spreadsheet, Owen takes some appointment/bill responsibilities.
- Emotional residue remains: Nina says she is still hurt and tired.

## Construct Targets

| Construct Type | Expected Examples |
|---|---|
| factual_issue | missed cardiology appointment; appointment on calendar |
| ambiguity | calendar visibility did not equal assigned ownership |
| role_pattern | Nina as default coordinator/default daughter |
| triangulation | Aunt Carla calling Nina and being used as evidence in conflict |
| value_collision | time burden vs financial burden; initiative vs direct assignment |
| unmet_need | fairness, recognition, shared responsibility, predictability |
| repair_attempt | Owen: "I hear that"; "You are carrying too much." |
| repair_attempt | Nina: "When you pay for things, I sometimes dismiss it..." |
| mediation_interest | shared goal of caring for mother and reducing conflict |
| systems_leverage_point | explicit ownership system instead of assumptions |
| power_dynamic | possible asymmetry around invisible labor and family expectations; evidence-limited |
| manipulation/abuse caution | guilt/pressure present, but intentional manipulation is insufficiently supported |

## Module-Specific Expectations

### Systems / Family Systems

Should identify:
- default-role homeostasis
- triangulation involving Aunt Carla
- implicit family rule: Nina handles coordination
- transition from person-blame to system design

### Mediation

Should separate:
- factual issue: missed appointment
- procedural issue: lack of assignment
- emotional issue: feeling blamed/unrecognized
- value issue: time vs money contributions
- relationship issue: fairness and respect

### Emotional Needs & Values

Should identify:
- Nina: fairness, recognition, shared responsibility, relief from default role
- Owen: recognition, direct communication, realistic expectations, respect for constraints

### Cognitive / Narrative

Should identify possible narratives:
- Nina: "If I don't handle it, things fall apart"; "I'm the default daughter"
- Owen: "My contributions disappear unless I defend them"; "I'm being accused of not caring"

### Trauma-Informed Communication

Should identify:
- shame/defensiveness risk around "Why do I have to assign you tasks like you're a teenager?"
- regulation improvement after validation
- no basis to infer trauma history

### Bias/Reliability

Should warn that:
- family-history claims cannot be verified from one transcript
- role patterns are plausible but need more longitudinal evidence
- intentional manipulation is not established
- power dynamics can be discussed only as possible/asymmetric role burden, not as conclusive coercion

## Suggested Automated Test Assertions

- At least one finding should cite the missed appointment.
- At least one finding should cite calendar ambiguity.
- At least one finding should cite Aunt Carla as third-party/family pressure.
- At least one finding should cite both financial contribution and time/coordination burden.
- At least two repair attempts should be detected.
- The practical agreement should include assigned ownership/spreadsheet or equivalent.
- Abuse/manipulation frameworks should remain low-confidence/exploratory.
