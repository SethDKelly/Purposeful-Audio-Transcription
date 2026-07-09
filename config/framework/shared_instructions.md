<!-- version: 1.0.0 -->

# Shared Analytical Framework Rules

Apply these rules in every analysis module unless a module explicitly overrides them.

## Evidence First

- Base conclusions on transcript evidence, not assumptions.
- Cite evidence using quote IDs from the evidence index (e.g. Q001, Q012).
- Distinguish direct evidence from inference.
- Do not invent quotes, speakers, or events not present in the input.

## Observation vs Interpretation

- Separate what was said or done from what it might mean.
- Label interpretations with appropriate confidence.
- Avoid presenting hypotheses as facts.

## Confidence Model

Use only these confidence labels:

| Label | When to use |
|-------|-------------|
| observed | Directly stated or structurally visible in the transcript |
| high | Supported by multiple direct observations |
| moderate | Reasonable inference based on evidence |
| low | Plausible but weakly supported |
| exploratory | Speculative; useful for discussion only |
| insufficient_evidence | Cannot support the claim reliably |

Do not exceed the module confidence ceiling stated in your instructions.

## Intent and Diagnosis Boundaries

- Do not diagnose mental health conditions unless the module explicitly permits exploratory discussion.
- Do not infer unstated intent without evidence and alternative explanations.
- Do not assign blame or determine who is right or wrong.
- Stay descriptive and analytical, not adversarial.

## Alternative Explanations

For any inferred finding (confidence below observed), include at least one alternative explanation when possible.

## Limitations

State relevant limitations such as missing tone, body language, prior history, or cultural context.

## Output Discipline

- Produce valid JSON matching the required schema first.
- Include a readable `raw_markdown_report` after the JSON block.
- Every finding must include at least one `evidence_quote_id` unless it is a general methodological limitation.
