# 019 — Cost State Decision

## Status

Accepted as the current cost-state decision for concept design and refactor planning.

This document defines cost state as a first-class personal-mode operating concept.

---

# Decision Summary

Cost State is a product concept for the personal operating mode.

The system should be able to sleep aggressively when unused, wake when the owner logs in, run active work safely, and shut down after the idle window.

This is not merely infrastructure detail. It affects how the user experiences the product.

## Core Rule

```text
Personal mode optimizes for low cost through explicit sleep/wake behavior.
Enterprise mode may later change availability policy without redefining the core product concepts.
```

---

# Cost State Model

Use these conceptual states:

```text
Asleep
Waking
Active
IdlePending
ShuttingDown
FailedWake
Maintenance
```

## Asleep

The system is minimized for cost.

Allowed retained resources may include:

- storage
- secrets
- minimal wake/auth path
- power-state record
- low-cost routing component if currently required

Expensive compute and runtime resources should be stopped, scaled to zero, or removed according to deployment policy.

## Waking

The owner has requested access and the system is starting required resources.

The user should know that wake latency is intentional cost control.

## Active

The application is usable.

Authenticated user activity or active background work keeps the system awake.

## IdlePending

The system has no authenticated activity and no active jobs for the configured idle window.

IdlePending should be visible or inferable to the user when relevant.

## ShuttingDown

The system is stopping services, deleting temporary endpoints, stopping databases, scaling workers down, or otherwise reducing cost according to policy.

## FailedWake

The system attempted to wake but did not reach a usable state.

The user should receive actionable feedback.

## Maintenance

The system is intentionally unavailable for maintenance or redesign work.

---

# Personal Mode Defaults

Recommended current defaults:

| Setting | Default |
|---|---|
| Wake trigger | Owner login |
| Idle window | 2 hours unless changed later |
| Active job behavior | Blocks sleep unless timeout/cancel policy applies |
| Long job cap | Explicit timeout policy required |
| Manual sleep | Allowed |
| Manual wake | Allowed |
| Always-on runtime | Not personal-mode default |

---

# Job Safety Rules

Sleep/wake behavior must not corrupt active work.

The system should not shut down while:

- transcription is active
- reflection run is active
- report generation is active
- export generation is active
- deletion/purge is active
- encryption/decryption migration is active

Long-running jobs require explicit timeout or cancellation policy.

---

# User Experience Rules

The user should understand:

- the app may be asleep to save cost
- login may trigger wake
- wake may take time
- active jobs keep the app awake
- idle shutdown is intentional
- failed wake is an operational state, not silent failure

---

# What Cost State Must Not Change

Cost State must not change the meaning of:

- transcript
- evidence quote
- finding
- hypothesis
- confidence
- reflection point
- case
- report
- reasoning graph

Availability policy may change when the app is available, but not what analysis objects mean.

---

# Enterprise Transition

Future enterprise mode may use:

```text
scheduled uptime
always-on services
autoscaling workers
high-availability database
multi-user sessions
monitoring and alerting
```

That should be a deployment policy change, not a conceptual rewrite.

---

# Decision

Keep Cost State as a first-class concept for personal mode.

Design later enterprise availability as a configurable policy layer over the same core product concepts.
