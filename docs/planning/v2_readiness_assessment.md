# v2 Readiness Assessment

## Question

After completing the next phase of work, does the application meet v2 criteria, or is it still in minor post-v1 phases?

## Short Answer

The current application is beyond ordinary post-v1 cleanup, but it is not yet full v2 GA.

After completing the numeric v2.1 phase sequence — core tenet hardening, simple email auth, evidence precision, evidence snapshots, safety policy hardening, graph relationship evidence, and case evidence correctness — the application can reasonably be considered:

```text
v2.0 beta
or
v2 release candidate
```

It should not be called full v2 GA until external-readiness criteria are satisfied.

---

# Why It Is More Than Minor Post-v1

The application already has many v2-like foundations:

- React frontend
- API/UI/worker architecture
- normalized findings and constructs
- ontology/graph reasoning
- durable workflow jobs
- cases
- evaluations
- safety fixtures
- report exports
- telemetry
- structured reasoning objects

The next phase is not just polish. It hardens the central product promises.

---

# Why It Is Not Yet Full v2 GA

The following areas still need completion or validation:

- real user authentication
- resource ownership checks
- transcript/evidence versioning
- concise evidence spans
- worker atomicity
- stricter safety policy behavior
- graph edge evidence
- case/longitudinal evidence identity
- OpenAPI-generated React client
- external UAT feedback
- security/privacy review
- backup/restore and deletion verification

---

# Recommended Version Labeling

## Current State

```text
pre-production post-v1
```

or:

```text
v2 foundation build
```

## After Numeric v2.1 Phase Sequence

```text
v2.0 beta
```

or:

```text
v2 release candidate
```

## After External-Readiness Criteria

```text
v2.0 GA
```
