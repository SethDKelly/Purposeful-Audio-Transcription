# 002-B — Concept-to-Domain Model Mapping

## Status

Complete for Phase 002 planning.

This subgroup maps accepted concepts to the current documented and implemented domain model.

---

# Purpose

002-B determines how the concept foundation relates to existing domain entities before architecture planning proceeds.

It answers:

- Which accepted concepts already have usable domain representation?
- Which existing entities should be retained?
- Which current names are implementation terms rather than product concepts?
- Which accepted concepts require new architecture decisions?
- What should 002-C use as its lifecycle/retention starting point?

---

# Inputs

| Input | Role |
|---|---|
| `docs/concepts/003_concept_catalog.md` | Accepted concept catalog |
| `docs/planning/inventories/002a_terminology_inventory.md` | Accepted terminology |
| `docs/design/03_domain_model.md` | Older/reference domain model |
| `docs/design/04_knowledge_ontology.md` | Existing graph/ontology model |
| `docs/design/05_data_model_and_schemas.md` | Older/reference schema model |
| `backend/domain/*.py` | Current implemented Pydantic domain models |

---

# Outputs

| Output | Document |
|---|---|
| Concept-to-domain mapping | `../inventories/002b_concept_domain_model_mapping.md` |
| Domain gap register | `../inventories/002b_domain_gap_register.md` |

---

# Accepted Findings

## 1. Existing Domain Model Is Useful

The existing model should be preserved as a prototype foundation.

Strong or partial matches already exist for:

- Transcript
- Transcript Version
- Speaker
- Turn
- Evidence Quote
- Finding
- Confidence
- Construct
- Construct Relationship
- Workflow Run
- Module Run
- Case

## 2. Concept Names Must Now Govern Product Semantics

The following mappings are accepted:

| Current / implementation term | Concept term |
|---|---|
| Analysis Module | Reflection Lens |
| Module Run | Lens Execution / part of Reflection Run |
| Workflow Run | Reflection Run |
| Recommendation / Intervention | Reflection Point |
| Safety Mode | Safety-Aware Framing / Safety Override |
| Audio source type | Recording input artifact |

Code names do not need to be changed immediately, but future user-facing docs, APIs, and UI should move toward accepted concept language.

## 3. Several Accepted Concepts Need Stronger Domain Representation

The main domain gaps are:

- Recording lifecycle
- Retention Rule
- Privacy Boundary
- Psychological Hypothesis
- Reflection Point
- Export
- Cost State
- Safety-aware override representation
- diagnostic-framework-informed lens metadata

## 4. Transcript Remains the Near-Term Aggregate Root

For now, `Transcript` remains the practical aggregate root for analysis.

A broader `ConversationRecord` concept may remain conceptual unless 002-C determines that retention and recording lifecycle require a new domain aggregate.

## 5. Do Not Introduce Enterprise Domain Complexity Yet

Enterprise remains a future policy layer.

Do not add organizations, workspaces, SSO roles, or multi-tenant domain objects during this refactor planning unless a later phase explicitly authorizes them.

---

# Non-Goals

002-B does not:

- modify code
- rename classes
- change database tables
- change schemas
- add migrations
- change API contracts
- update prompts
- modify UI copy

---

# Handoff to 002-C

002-C should focus on lifecycle and retention architecture for:

```text
Recording
Transcript Draft
Saved Transcript
Transcript Version
Evidence Quote
Reflection Run
Finding
Hypothesis
Reflection Point
Report
Case
Export
Deletion Cascade
```

Proceed next to:

```text
002-C — Data Lifecycle and Retention Architecture Plan
```

---

# Exit Criteria

002-B is complete when:

- accepted concepts are mapped to existing domain entities
- strong matches are identified
- naming shifts are documented
- domain gaps are registered
- the next architecture subgroup is named

All criteria are satisfied.
