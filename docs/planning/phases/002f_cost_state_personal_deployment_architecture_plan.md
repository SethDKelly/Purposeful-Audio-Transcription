# 002-F — Cost State and Personal Deployment Architecture Plan

## Status

Complete.

This subgroup translates the accepted cost-state and personal operating model decisions into architecture planning requirements.

---

# Purpose

002-F defines how the personal-mode deployment should support low cost without corrupting work or confusing product semantics.

It answers:

- What does Cost State mean architecturally?
- Which states must be represented?
- What triggers wake?
- What allows sleep?
- How does idle shutdown work?
- Which jobs block sleep?
- What controls should the owner have?
- What must the UI eventually expose?
- How does future enterprise availability fit without redefining concepts?

---

# Outputs

| Output | Document |
|---|---|
| Cost state and personal deployment architecture plan | `../architecture/002f_cost_state_personal_deployment_architecture_plan.md` |
| Cost state transition matrix | `../inventories/002f_cost_state_transition_matrix.md` |
| Personal deployment control requirements | `../inventories/002f_personal_deployment_control_requirements.md` |

---

# Accepted Decisions

## 1. Cost State is control-plane architecture

Cost State should be represented by a control-plane layer that manages availability posture.

It must remain separate from transcript, analysis, evidence, hypothesis, report, and graph semantics.

## 2. Personal mode may sleep aggressively

Personal mode is allowed to be intentionally asleep to reduce cost.

Wake latency should be treated as intentional product behavior, not silent failure.

## 3. Wake is explicit

Accepted wake triggers:

```text
owner login
manual wake control
future scheduled wake, if explicitly added
```

## 4. Idle shutdown requires no user activity and no blocking jobs

The idle evaluator should consider both authenticated user activity and blocking job activity.

Recommended personal-mode idle window remains:

```text
2 hours
```

## 5. Active jobs block unsafe sleep

Shutdown must not corrupt active work.

Blocking jobs include transcription, reflection run, report/export generation, deletion cascades, purge work, encryption migration, and future corpus graph recomputation.

## 6. Manual controls are owner-only in personal mode

Personal mode should support owner-only wake, sleep, keep-awake, retry wake, cancel blocking job, and maintenance controls.

## 7. Enterprise availability is policy expansion

Future enterprise mode may change availability policy through scheduled uptime, always-on services, autoscaling, monitoring, and HA posture.

It should not redefine core product concepts.

---

# Resolved 002-F Architecture Questions

| Question | Resolution |
|---|---|
| Should Cost State be product or infrastructure? | Product-aware control-plane architecture concept |
| Should personal mode be always-on? | No; aggressive sleep/wake is accepted |
| Should idle shutdown depend only on user activity? | No; must also consider blocking jobs |
| Should long jobs block sleep indefinitely? | They block sleep unless timeout/cancel/resume policy applies |
| Should cost state affect analysis meaning? | No |
| Should enterprise drive near-term design? | No; enterprise is future policy expansion |

---

# Handoff to 002-G

002-G should define UI/UX concept alignment for:

- asleep state
- wake progress
- active state
- idle pending warning
- manual sleep/wake
- keep-awake
- active job keeps awake
- failed wake
- maintenance
- user-facing language that explains cost-saving behavior

---

# Handoff to 002-H

002-H should convert 002-F into refactor backlog items and acceptance gates, including:

- cost-state record or equivalent
- blocking job registry
- idle evaluator
- safe shutdown coordinator
- wake/sleep controls
- operational event redaction
- job-safe shutdown tests
- pipeline/workflow replacement plan

---

# Non-goals

002-F does not implement:

- cloud automation
- AWS scripts
- database migrations
- GitHub Actions
- scheduler changes
- queue changes
- UI changes
- monitoring stack
- autoscaling

Implementation remains blocked until Phase 002-I exit review authorizes the next phase.

---

# Exit Criteria

002-F is complete when:

- Cost State is mapped to architecture
- state model is documented
- transition matrix exists
- idle evaluation rule is documented
- blocking job behavior is documented
- owner controls are documented
- UI handoff is explicit
- implementation remains blocked until 002-I

All criteria are satisfied.

---

# Next Phase

Proceed to:

```text
002-G — UI/UX Concept Alignment Plan
```
