# User guide

How to use the Streamlit UI and interpret results.

## The four steps

```text
Ingest → Prepare → Analyze → Report
```

### 1. Ingest

**Audio tab** — upload `.mp3`, `.wav`, `.m4a`, etc. If you know how many people spoke, choose **Expected speakers** before uploading; Amazon Transcribe labels turns as **Person A**, **Person B**, etc. Otherwise paste text in the text tab.

**Paste / upload tab** — paste labeled dialogue or upload a `.txt` file. Preferred format:

```text
Person A: I felt left out when plans changed.
Person B: I hear that. I should have checked in first.
```

### 2. Prepare

- Edit **speaker display names** (stored with the transcript).
- Review turns: edit text, **exclude** turns that should not enter analysis.
- Optionally rebuild the **evidence index** so quote IDs (`Q001…`) match the approved turns.
- Click **Ready to Analyze** (or intentionally skip review). Analysis is gated until ready.

Each included turn receives a stable **evidence quote ID** used in all findings.

### 3. Analyze

Select a **workflow** and **LLM model** (Bedrock), then **Run workflow**.

Workflows run modules sequentially. Long workflows default to background in the UI when the workflow sets `default_background`, or when module count exceeds `WORKFLOW_SYNC_MODULE_LIMIT`. You can also pass `"background": true` on the API.

### 4. Report

Report tabs:

| Tab | Purpose |
|-----|---------|
| **Overview** | Executive summary and top interventions |
| **Module reports** | Per-module findings with evidence |
| **Evidence map** | Quote-centric view; which modules cited each quote |
| **Synthesis** | Cross-module convergence and divergence |
| **Explore** | Interactive drill-down and follow-up questions |

## Workflows

| ID | Modules | Synthesis | Notes |
|----|---------|-----------|-------|
| `quick_review` | Relationship, NVC, Bias | No | Fast iteration |
| `full_mvp` | Relationship, NVC, Systems, Bias | Yes | Integrated report |
| `conflict_coaching` | Relationship, NVC, Needs & Values, Bias | No | Coaching framing |
| `mediation_brief` | Relationship, Mediation, NVC, Bias | No | Mediation framing |
| `clinical_exploration` | Formulation, Cognitive, Attachment, Narrative, Bias | Yes | Exploratory (non-diagnostic) |
| `research_oriented` | Relationship, Cognitive, Narrative, Bias, Systems | Yes | Pattern study; default background |
| `full_multidisciplinary` | All 12 transcript modules | Yes | Long suite; default background |

Long suites default to background execution in the UI/API. Synchronous runs are capped by `WORKFLOW_SYNC_MODULE_LIMIT` (default 6).

Pick **Quick Review** for iteration; **Full MVP** for an integrated report; **Full Multidisciplinary** when you want every lens; role-specific workflows for coaching or mediation framing.

## Understanding findings

Each finding includes:

- **Title and summary** — what the module concluded
- **Confidence** — how strongly the transcript supports it (e.g. observed, moderate)
- **Evidence quote IDs** — click through in Evidence map or Explore
- **Alternative explanations** — other plausible readings
- **Limitations** — what the module cannot know from text alone

## Explore tab

Without re-running a workflow you can:

- **Structured inventory** — table-first view of constructs, relationships, and findings (filter by type, confidence, module); includes convergence scores when available
- **Why this finding?** — evidence chain and related findings in other modules
- **Cross-module** — agreement and tension between modules
- **Compare sessions** — compare multiple runs on the same transcript
- **Knowledge graph** — constructs and relationships from normalized storage when present
- **Ask a question** — scoped follow-up via Bedrock using stored findings

Scope a question to one finding or the entire run.

## Exports

From the report dashboard:

| Export | Format |
|--------|--------|
| Workflow report | `.md`, `.json`, `.pdf` |
| Coach summary | `.md` |
| Mediation brief | `.md` (mediation workflows) |

Enable **Redact speaker labels** before export when sharing outside your trusted environment.

## Safety and framing

The app is **exploratory and non-diagnostic**:

- Output is analytical support, not therapy, legal advice, or abuse determination.
- A safety disclaimer appears in the UI; a validator flags some high-risk phrasing.
- Transcript context may be incomplete; tone and intent are inferred from text only.

For serious safety concerns, consult qualified professionals.

## Tips

- Start with short transcripts until you trust your Bedrock model choice.
- Mark transcripts **Ready to Analyze** after review so quote IDs stay stable.
- Prefer background for long suites (`research_oriented`, `full_multidisciplinary`).
- Soft construct-coverage warnings on module runs mean the model under-populated expected constructs — not a hard failure.
- Pause AWS when idle; deploy only for minor-version releases.

## Related

- [getting-started.md](getting-started.md)
- [model-setup.md](model-setup.md)
- [deployment.md](deployment.md)
- [../product/transcript_preparation_workspace.md](../product/transcript_preparation_workspace.md)
