# 10 — Synthesis Engine

## Purpose

The synthesis engine integrates structured findings across modules into a coherent, confidence-weighted report.

## Inputs

- Module outputs
- Structured findings
- Evidence links
- Construct graph
- Confidence labels
- Bias audit results

## Outputs

- Executive integration
- High-confidence findings
- Moderate-confidence findings
- Exploratory hypotheses
- Convergence table
- Divergence table
- Integrated interaction model
- Highest-leverage interventions
- Outstanding questions

## Synthesis Is Not Averaging

Different modules answer different questions. The synthesis engine should explain how findings relate rather than forcing them into one conclusion.

## Convergence Detection

A finding has stronger support when multiple modules identify compatible constructs.

Example:

```text
Communication Analysis: criticism-defensiveness pattern
Systems Analysis: reinforcing feedback loop
Gottman: criticism and defensiveness
NVC: evaluation instead of need expression
```

Synthesis conclusion:

```text
The transcript strongly supports a recurring escalation pattern involving critical/evaluative language followed by defensive responses.
```

## Divergence Detection

Modules may disagree or emphasize different explanations.

Example:

- Cognitive Analysis: negative attribution
- Attachment Matrix: reassurance/protection cycle
- Needs Analysis: autonomy vs closeness value conflict

These may be complementary, not contradictory.

## Confidence Weighting

Suggested factors:

- number of modules supporting finding
- quality of evidence
- directness of evidence
- module confidence ceiling
- presence of contradictory evidence
- bias audit warnings

## Synthesis Output Structure

```json
{
  "executive_summary": "...",
  "high_confidence_findings": [],
  "moderate_confidence_findings": [],
  "exploratory_hypotheses": [],
  "convergence": [],
  "divergence": [],
  "integrated_model": [],
  "interventions": [],
  "outstanding_questions": [],
  "limitations": []
}
```

## Integrated Model Pattern

```text
Event
  → Interpretation
  → Emotion
  → Need/Value
  → Behavior
  → Partner Response
  → System Reinforcement
  → Narrative Meaning
```

## Highest-Leverage Interventions

Rank interventions by:

- expected impact
- evidence support
- feasibility
- risk of misuse
- number of modules recommending it

Examples:

- Validate before explaining
- Convert criticism into specific request
- Pause during flooding
- Clarify assumptions before responding
- Recognize repair attempts
- Establish conflict ritual

## Synthesis Guardrails

Do not:

- introduce new unsupported claims
- reanalyze transcript unless required
- let one speculative module dominate
- hide uncertainty
- diagnose
- imply certainty from volume of analysis alone

## MVP Approach

For MVP, meta-synthesis can be LLM-generated using structured module outputs. Later, supplement with deterministic graph-based scoring.
