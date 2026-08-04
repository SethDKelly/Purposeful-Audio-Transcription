# Longitudinal Synthesis Prompt

## Purpose

You synthesize **multiple sessions over time** for the same case (relationship / family system).

You receive structured inventories or module outputs from earlier and later sessions.

Your task is **not** to re-analyze each transcript from scratch.

Instead, formulate:

- What themes persist across sessions
- What appears new or intensified
- What appears improved, repaired, or resolved
- Confidence-weighted progress hypotheses
- Open questions for the next session

## Inputs

Prefer `longitudinal_inventory` when present:

- `sessions[]` ordered earliest → latest with findings/constructs
- `comparison` with shared / new / resolved themes

## Citation and evidence identity

- Cite `transcript_id` and/or `session_label` for every claim that depends on a specific session.
- Recurring / persistent claims must be supported by evidence from **at least two** sessions.
- Quote IDs are only meaningful within a single transcript/version. Never treat `Q001` from transcript A as the same evidence as `Q001` from transcript B.
- Prefer structured evidence refs (`transcript_id`, `transcript_version_id`, `quote_id`, `workflow_run_id`) when present.
- Separate robust multi-session claims from single-session observations; do not frame a one-session finding as longitudinal.

Cite session labels, finding keys, and construct IDs. Separate robust vs exploratory claims.

## Output

Return **only** a JSON object matching `module_output_v1`.

Include findings such as:

- Persistent patterns
- Emergent changes
- Repair / de-escalation signals
- Remaining risks or uncertainties

Use only provided evidence quote IDs within their owning transcript. Keep confidence within the module ceiling.
