# 002-B Concept-to-Domain Model Mapping

## Status

Accepted as the Phase 002-B concept-to-domain mapping inventory.

---

# Purpose

Map accepted concept-design terms to the current documented and implemented domain model before architecture planning begins.

This is not a schema migration and does not change application behavior.

---

# Inputs Reviewed

Primary concept authority:

- `docs/concepts/003_concept_catalog.md`
- `docs/planning/inventories/002a_terminology_inventory.md`

Current/reference domain material:

- `docs/design/03_domain_model.md`
- `docs/design/04_knowledge_ontology.md`
- `docs/design/05_data_model_and_schemas.md`
- `backend/domain/transcript.py`
- `backend/domain/finding.py`
- `backend/domain/workflow.py`
- `backend/domain/case.py`
- `backend/domain/enums.py`

---

# Mapping Rule

Accepted concepts control product semantics.

Existing domain entities are retained where they match the accepted concept model, renamed where they encode legacy terminology, promoted where they already partially implement an accepted concept, and marked as gaps where no first-class domain representation exists.

```text
Accepted Concept -> Domain Model -> Schema/API/Service -> UI/Report
```

002-B only defines the first two steps.

---

# Concept-to-Domain Mapping

| Accepted Concept | Current Domain / Implementation Mapping | Status | Notes |
|---|---|---|---|
| Secure Conversation Analysis and Reflection System | Product-level concept, not a single domain class | Accepted product frame | Should guide docs, UI, APIs, and reports |
| Relationship Reasoning Engine / RRE | Existing engine/product wording in older docs | Retain as internal engine identity | Do not use as sole user-facing product identity |
| Conversation Record | `Transcript` plus optional source artifact | Partial | Needs clearer aggregate boundary around source, transcript, versions, and retention |
| Recording | `SourceType.AUDIO`, upload/transcription flow | Gap / partial | Needs first-class lifecycle concept or explicit transient artifact boundary |
| Transcript | `Transcript` | Strong match | Existing class already includes source type, readiness, case linkage, session metadata, and current version fields |
| Transcript Version | `TranscriptVersion`, `current_version_id`, `transcript_version_id` references | Strong partial | Concept is present; architecture phase should harden version binding and staleness behavior |
| Speaker | `Speaker` | Supporting entity | Not a core concept in 001, but necessary domain support |
| Turn | `Turn` | Supporting entity | Required for evidence anchoring and transcript prep |
| Evidence Quote | `EvidenceQuote` | Strong partial | Includes quote id, span text, context, evidence type, and transcript version id; should become version-required for retained analysis |
| Reflection Run | `WorkflowRun` plus `ModuleRun` | Rename / partial | Current implementation calls this workflow/module execution; concept language should distinguish product Reflection Run from implementation workflow orchestration |
| Reflection Lens | `ModuleDefinition` / analysis module | Rename / partial | Modules are implementation; product concept is Reflection Lens |
| Therapeutic Reflection Lens | `ModuleDefinition.primary_lens` / module config | Partial | Needs explicit lens-family metadata and authority boundary in architecture |
| Diagnostic-framework-informed concept | No clear first-class domain object | Gap | Should inform lens metadata, hypothesis metadata, and validators, not user-facing authority |
| Psychological Hypothesis | `FindingType.HYPOTHESIS`, exploratory hypotheses in reports | Gap / partial | Needs first-class bounded hypothesis representation or schema convention |
| Finding | `Finding` | Strong match | Already includes confidence, evidence quote ids, alternatives, and limitations |
| Confidence | `Confidence` enum | Strong partial | Existing enum differs from accepted language; 002-E should decide whether to add `possible`, `contraindicated`, or mapping aliases |
| Reflection Point | `recommendations`, `intervention`, report guidance | Rename / gap | Current terms risk sounding prescriptive; should map to non-prescriptive Reflection Point |
| Reasoning Graph | `Construct`, `ConstructRelationship`, ontology graph | Strong partial | Needs graph-edge evidence and confidence rules to align with concept authority |
| Case | `Case`, `CaseDetail`, transcript case fields | Strong partial | Needs retention implications and source transcript/version identity hardened |
| Retention Rule | No clear first-class domain model in reviewed domain files | Gap | 002-C should define artifact retention states and policy model |
| Privacy Boundary | Auth/ownership/security docs, not domain model | Gap | 002-D should decide owner scope, access rules, redaction, and encryption fields |
| Cost State | AWS ops / deployment behavior, not domain model | Gap | 002-F should define conceptual state and deployment/control representation |
| Export | Report ZIP/export behavior | Gap / partial | Needs explicit export artifact semantics and retention/default deletion behavior |
| Personal Mode | Deployment/operating posture | Gap / policy concept | Should be represented as deployment policy, not core analysis entity |
| Future Enterprise Policy Layer | Deferred policy layer | Deferred | Do not introduce enterprise domain complexity now |

---

# Domain Entities to Retain

The following existing entities align well with the concept model and should be retained unless later architecture work finds implementation defects:

- `Transcript`
- `TranscriptVersion`
- `Speaker`
- `Turn`
- `EvidenceQuote`
- `Finding`
- `Construct`
- `ConstructRelationship`
- `WorkflowRun`
- `ModuleRun`
- `Case`

---

# Domain Entities to Rename Conceptually

These do not require immediate code renaming, but future product/docs/API language should prefer the accepted concept terms.

| Current Term | Concept Term | Rationale |
|---|---|---|
| Analysis Module | Reflection Lens | User-facing concept is a reasoning lens, not a software module |
| Module Run | Lens Run or Lens Execution | Implementation detail within a broader Reflection Run |
| Workflow Run | Reflection Run | Product concept is one analysis/reflection execution over a transcript version |
| Recommendation | Reflection Point | Avoid prescriptive or treatment-like framing |
| Intervention | Reflection Point / Possible Repair Move | Avoid clinical or directive implication unless strictly bounded |
| Safety Mode | Safety-Aware Framing / Safety Override | Safety is a conceptual output posture, not only a mode flag |
| Transcript source type audio | Recording | Audio is an ephemeral artifact, not just an enum value |

---

# Domain Concepts Requiring Architecture Decisions

The following concepts are accepted but not yet sufficiently represented in the current domain model:

1. Recording lifecycle artifact
2. Retention Rule
3. Privacy Boundary
4. Cost State
5. Psychological Hypothesis as bounded reasoning object
6. Reflection Point as non-prescriptive output object
7. Export artifact and retention behavior
8. Personal Mode policy representation
9. Diagnostic-framework-informed lens metadata
10. Safety-aware override representation beyond a boolean flag

These should be handled by subgroups 002-C through 002-F and 002-H.

---

# Accepted 002-B Decision

The current domain model is usable as a prototype foundation.

It should not be discarded.

However, it should be refactored concept-first:

```text
Transcript-centered evidence model stays.
Workflow/module implementation remains useful.
Concept language shifts toward Reflection Run and Reflection Lens.
Retention, privacy, cost state, hypothesis, reflection point, and export need stronger first-class modeling.
```

---

# Handoff to 002-C

Proceed next to:

```text
002-C — Data Lifecycle and Retention Architecture Plan
```

002-C should use this mapping to decide how Recording, Transcript Draft, Saved Transcript, Transcript Version, Evidence Quote, Report, Case, Export, and deletion cascades should be represented architecturally.
