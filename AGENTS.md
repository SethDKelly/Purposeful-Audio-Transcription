# Repository Agent Rules

## Purpose

These rules apply to Codex, Cursor, AI assistants, and human contributors performing implementation work in this repository.

The repository contains a prototype/reference implementation for the accepted product concept:

```text
Secure Conversation Analysis and Reflection System
```

The repository name, `Purposeful Audio Transcription`, is historical. Audio transcription is an input capability, not the product identity.

---

# Required Read Order for Agents

Before changing code, schemas, prompts, UI, reports, deployment, or tests, read:

```text
docs/planning/implementation_guardrails.md
docs/planning/phases/README.md
docs/planning/phases/004_controlled_foundation_refactor_implementation.md
```

Then read the accepted Phase 004 subgroup summary and the directly relevant Phase 003 plan/checklist for the work.

For current 004-B work, read:

```text
docs/planning/architecture/003b_domain_terminology_concept_mapping_implementation_plan.md
docs/planning/inventories/003b_domain_concept_mapping_inventory.md
docs/planning/inventories/003b_domain_terminology_migration_work_packages.md
```

---

# Authority Order

When sources conflict, follow:

```text
docs/concepts/
→ Phase 003 exit review and Phase 004 authorized scope
→ Phase 004 overview and current subgroup summary
→ directly relevant Phase 003 gates and work packages
→ reconciled implementation docs
→ code
→ legacy/reference/historical docs
```

Code is implementation evidence. It is not product authority when it conflicts with accepted concepts.

---

# Mandatory Implementation Header

Every non-trivial change should record:

```text
Phase 004 subgroup:
Phase 003 work packages executed:
Applicable gates:
Compatibility posture:
Migration posture:
Tests / verification:
Deferred or explicitly not touched:
```

Use a pull request body, implementation note, subgroup phase summary, or commit documentation.

---

# Current Phase Boundary

Current phase:

```text
Phase 004 — Controlled Foundation Refactor Implementation
```

Completed:

```text
004-A — Implementation Authority Lock, Agent Rules, and Documentation Guardrails
```

Next:

```text
004-B — Domain Terminology Compatibility and Concept Contract Implementation
```

Mandatory exit:

```text
004-I — Phase 004 Exit Review and Consolidation
```

Do not start broad rewrite work.

---

# Non-Negotiable Product Boundaries

The application may use therapeutic, psychological, behavioral, cognitive, relational, and diagnostic-framework-informed concepts as evidence-limited reasoning references.

It must not present itself as:

- a clinician
- a therapist
- a diagnostic tool
- a treatment system
- a legal adjudicator
- an HR/workplace surveillance system
- a hidden-intent detector

Do not implement output, UI, prompts, reports, or exports that imply those roles.

---

# Sensitive Data Boundaries

Never add logs, telemetry, errors, audit extras, lifecycle events, debug output, or UI status messages that expose:

- audio content
- transcript bodies
- long evidence passages
- prompt payloads
- raw model completions
- report bodies in operational logs
- export contents in operational logs
- secrets
- tokens
- login codes

---

# Compatibility First

Prefer additive contracts, aliases, adapters, DTO fields, and compatibility layers.

Do not perform destructive class, table, route, or API field renames without explicit compatibility, migration, regression, and release-readiness gates.

---

# GitHub Actions

GitHub Actions workflows were intentionally cleared.

Do not restore or add workflows until the applicable cost-state, privacy, job-safe shutdown, deployment documentation, regression, and release-readiness gates are satisfied.

---

# Enterprise Deferral

Do not introduce enterprise org/workspace/RBAC/SSO/compliance/billing or always-on availability as Phase 004 baseline scope.

Enterprise remains a future policy/deployment layer.

---

# Completion Standard

A subgroup is not complete just because files compile or docs exist.

It is complete only when:

- the subgroup scope is respected
- applicable gates are addressed
- compatibility/migration posture is explicit
- tests or verification are recorded
- docs/indexes are updated when relevant
- deferred work is explicit
- the next subgroup is named
