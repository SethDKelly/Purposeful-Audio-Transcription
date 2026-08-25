# 006 — Cost and Availability Concepts

## Purpose

Define cost and uptime behavior as explicit product concepts.

In the personal-use phase, cost is a major design constraint. The system should wake when needed, run analysis, and shut down when idle.

This is not a temporary hack. It is a valid operating mode.

---

# Concept — Cost State

## Purpose

Represent the availability and cost posture of the deployed system.

## Operational Principle

When the owner logs in, the system wakes required infrastructure. When no authenticated activity or active jobs exist for a configured idle period, the system shuts down expensive resources.

## States

```text
Asleep
Waking
Active
IdlePending
ShuttingDown
FailedWake
Maintenance
```

## State Descriptions

### Asleep

The system is minimized for cost.

Possible retained resources:

- ALB or wake endpoint
- storage
- secrets
- minimal power-control state

Expensive resources are stopped or scaled down.

### Waking

The user has requested access. The system is starting required services.

### Active

The application is usable.

### IdlePending

No active jobs or authenticated activity has occurred for the idle threshold.

### ShuttingDown

The system is stopping services, scaling down, deleting endpoints, or stopping database resources according to policy.

---

# Cost State Invariants

- Shutdown must not corrupt active jobs.
- Wake must be visible to the user.
- Active analysis should block sleep unless timeout policy applies.
- Idle state should depend on both user activity and job activity.
- Cost policy should be configurable.
- Cost policy should not be mixed with analysis semantics.

---

# Personal Mode Availability Policy

Near-term personal mode:

```text
aggressive sleep
wake on login
shutdown after idle window
cancel or handle long-running jobs according to explicit timeout policy
```

## Goals

- minimize AWS costs
- retain sensitive data safely
- allow occasional personal use
- avoid always-on infrastructure
- preserve future enterprise path

---

# Enterprise Mode Availability Policy

Future enterprise mode may use:

```text
always-on services
scheduled uptime
autoscaling workers
multi-user sessions
high availability database
monitoring and alerting
```

The key design point:

> Availability policy should change without redefining the core analysis concepts.

---

# Open Questions

1. Should personal mode keep the ALB alive or use a cheaper wake mechanism later?
2. Should idle timeout be user-configurable?
3. Should long-running jobs prevent sleep indefinitely or be capped?
4. Should there be a “keep awake for X hours” control?
5. Should analysis jobs be resumable after shutdown?
