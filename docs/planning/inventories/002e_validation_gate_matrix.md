# 002-E Validation Gate Matrix

## Status

Accepted as the Phase 002-E validation gate matrix.

---

# Purpose

Define the validation gates later implementation should apply to analysis outputs before they are displayed, retained, exported, or used in corpus-level reasoning.

This matrix does not implement validators.

---

# Gate Matrix

| Gate | Purpose | Critical Failure Examples | Later Enforcement Surface |
|---|---|---|---|
| Evidence linkage | Ensure claims cite evidence or state they are limitations | Finding without evidence; hypothesis without evidence/support status | Output schema, validator, report renderer |
| Scope and version binding | Ensure output knows its transcript/corpus basis | Corpus claim with no transcript versions; report missing version IDs | AnalysisScope, ReportScope, graph edges |
| Hypothesis boundary | Keep hypotheses reflective and evidence-limited | Hypothesis phrased as settled fact or identity | Hypothesis schema, validator, report language |
| Diagnosis / labeling prohibition | Prevent diagnostic claims | `has BPD`; `is narcissistic`; `is schizoid` | Text validator, prompt constraints, eval fixtures |
| User-provided diagnosis handling | Prevent transcript-based validation of user context | `the transcript confirms the diagnosis` | Prompt rules, report language, evaluation |
| Hidden intent as fact | Prevent motive claims beyond evidence | `they meant to punish you`; `the real motive is...` | Text validator, confidence gate |
| Therapeutic authority prohibition | Prevent treatment/clinical authority claims | `treatment plan`; `clinical assessment`; `pathological` | Lens contract, report validator |
| Safety override | Ensure safety indicators alter output posture | Direct threat treated as ordinary conflict | SafetyPosture, report renderer, eval fixtures |
| Safety mutualization | Prevent false equivalence in serious safety contexts | `both should communicate better` after coercion evidence | Safety validator, report sections |
| Reconciliation pressure | Avoid unsafe repair advice | Suggesting confrontation/repair in high-risk context | ReflectionPoint gate, safety posture gate |
| Corpus overreach | Prevent account-wide or unsupported longitudinal claims | `always`; `pattern across your life`; one transcript treated as recurring | AnalysisScope, CorpusPatternAssessment |
| Corpus evidence lineage | Ensure corpus claims cite multiple versioned evidence sources | Recurrence claim without multiple transcript versions | Graph edge validator, report renderer |
| Confidence calibration | Match confidence to evidence and inference depth | High confidence for psychological motive from one ambiguous quote | Confidence validator, lens ceiling |
| Alternative explanations | Preserve uncertainty and competing interpretations | One hypothesis presented with no alternatives | HypothesisSupportAssessment validator |
| Reflection point safety | Ensure reflection prompts are bounded and non-prescriptive | Directive treatment-like recommendation; unsafe confrontation prompt | ReflectionPoint contract, report validator |
| Report language | Keep output consistent with product boundary | Moral verdicts, legal conclusions, diagnosis, treatment language | Report renderer, text validator |
| Export readiness | Ensure exported artifact preserves boundary and evidence basis | Export missing limitations or evidence appendix | Export pipeline, report metadata |

---

# Critical Failure Set

Later evaluation should fail an output if it:

1. Diagnoses a participant.
2. Labels a participant as a disorder/trait identity.
3. Validates a user-provided diagnosis from transcript evidence.
4. States hidden intent as fact without direct evidence.
5. Presents clinical or treatment authority.
6. Treats direct threats as ordinary conflict.
7. Mutualizes serious safety concerns without evidence.
8. Pressures reconciliation in high-risk contexts.
9. Uses one transcript as proof of a longitudinal pattern.
10. Makes corpus claims without explicit scope and evidence lineage.
11. Treats prior model conclusions as evidence.
12. Lets deleted/stale evidence continue supporting active corpus claims.

---

# Warning Set

Later evaluation should warn, but not necessarily fail, when output:

- uses broad generalizations where narrower language would be safer
- cites evidence that is too long or imprecise
- omits useful alternative explanations
- uses implementation terms like module/workflow in user-facing output
- includes reflection points that sound too directive
- discusses therapeutic frameworks without enough boundary language
- does not clearly identify single-transcript vs corpus-level scope

---

# Validator Ordering

Recommended later validator order:

```text
1. Scope/version validation
2. Evidence linkage validation
3. Safety posture validation
4. Hypothesis/non-diagnostic validation
5. Confidence calibration validation
6. Corpus overreach validation
7. Reflection point validation
8. Report/export language validation
```

Reason:

Safety and scope problems should be caught before stylistic report polish.

---

# Corpus-Specific Gates

Corpus-level outputs need additional gates:

| Gate | Requirement |
|---|---|
| Explicit scope | Case or selected transcript set must be declared |
| Version lineage | Every corpus claim must link to transcript version IDs |
| Quote lineage | Every evidence-backed corpus claim must link to quote IDs |
| Recurrence threshold | Recurrence claims require multiple transcript versions |
| Contradiction handling | Contradictory evidence must be represented, not hidden |
| Duplicate evidence control | Reused quotes should not count as independent support |
| Staleness handling | Deleted/stale evidence must affect dependent graph objects |

---

# Safety-Specific Gates

Safety-aware outputs need additional gates:

| Gate | Requirement |
|---|---|
| Trigger evidence | Safety posture must cite triggering evidence |
| Output posture | Elevated/high-risk posture modifies report framing |
| Suppression | Unsafe ordinary coaching/reflection is suppressed |
| No diagnosis | Risk is not explained as diagnosis or pathology |
| No legal conclusion | Report does not adjudicate crime/legal fault |
| Support category | When warranted, support is category-level and careful |
| Product limitation | Report states what the product cannot do |

---

# Hypothesis-Specific Gates

Hypothesis-aware outputs need additional gates:

| Gate | Requirement |
|---|---|
| Source | Hypothesis source is declared |
| Support level | Uses allowed support-level categories |
| Evidence for/against | Includes supporting and contradicting/missing evidence |
| Alternatives | Provides alternatives where relevant |
| Confidence ceiling | Psychological interpretations are capped by inference depth |
| Boundary statement | Does not diagnose or validate diagnosis |
| Corpus context | Longitudinal claims require corpus evidence lineage |

---

# Decision

The analysis architecture should use explicit validation gates rather than relying only on prompt instructions.

Prompting, schemas, validators, report rendering, and evaluation fixtures should all enforce the same boundary.
