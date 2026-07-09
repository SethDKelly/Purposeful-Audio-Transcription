# User guide

How to use the Streamlit UI and interpret results.

## The four steps

```text
Ingest → Prepare → Analyze → Report
```

### 1. Ingest

**Audio tab** — upload `.mp3`, `.wav`, `.m4a`, etc. If you know how many people spoke, choose **Expected speakers** (2, 3, 4, or a custom count) before transcribing; otherwise leave **Auto-detect**. Click **Transcribe audio** to run Whisper. When diarization is enabled (see [model-setup.md](model-setup.md)), the app labels turns as **Person A**, **Person B**, etc. Otherwise you get a single-speaker transcript you can edit manually in Step 2.

**Paste / upload tab** — paste labeled dialogue or upload a `.txt` file. Preferred format:

```text
Person A: I felt left out when plans changed.
Person B: I hear that. I should have checked in first.
```

### 2. Prepare

- Edit **speaker display names** (stored with the transcript).
- Review the transcript text. If you edit after preparation, re-prepare or accept that quote IDs may not match edited text.

Each turn receives a stable **evidence quote ID** (`Q001`, `Q002`, …) used in all findings.

### 3. Analyze

Select a **workflow** and **Ollama model**, then **Run workflow**.

Workflows run modules sequentially. Long workflows can be queued in the background via the API (`"background": true`); the UI runs synchronously by default.

### 4. Report

Report tabs:

| Tab | Purpose |
|-----|---------|
| **Overview** | Executive summary and top interventions |
| **Module reports** | Per-module findings with evidence |
| **Evidence map** | Quote-centric view; which modules cited each quote |
| **Synthesis** | Cross-module convergence and divergence |
| **Explore** | Interactive drill-down and follow-up questions |

## Workflows (v0.3.0)

| ID | Modules | Synthesis |
|----|---------|-----------|
| `quick_review` | Relationship, NVC, Bias | No |
| `full_mvp` | Relationship, NVC, Systems, Bias | Yes (meta-synthesis) |
| `conflict_coaching` | Relationship, NVC, Needs & Values, Bias | No |
| `mediation_brief` | Relationship, Mediation, NVC, Bias | No |
| `clinical_exploration` | Formulation, Cognitive, Attachment, Narrative, Bias | Yes |

Pick **Quick Review** for iteration; **Full MVP** for an integrated report; role-specific workflows for coaching or mediation framing.

## Understanding findings

Each finding includes:

- **Title and summary** — what the module concluded
- **Confidence** — how strongly the transcript supports it (e.g. observed, moderate)
- **Evidence quote IDs** — click through in Evidence map or Explore
- **Alternative explanations** — other plausible readings
- **Limitations** — what the module cannot know from text alone

## Explore tab

Without re-running a workflow you can:

- **Why this finding?** — evidence chain and related findings in other modules
- **Cross-module** — agreement and tension between modules
- **Compare sessions** — compare multiple runs on the same transcript
- **Knowledge graph** — constructs and relationships (when modules return them)
- **Ask a question** — scoped follow-up to Ollama using stored findings

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

- Start with short transcripts until you trust your model choice.
- Set `DEFAULT_OLLAMA_MODEL` in `.env`; use a larger model for `meta_synthesis` if JSON quality is weak.
- Re-run the same transcript with different workflows to compare lenses.
- Back up `data/rre.db` before upgrades — see [deployment.md](deployment.md).

## Related

- [getting-started.md](getting-started.md)
- [model-setup.md](model-setup.md)
- [deployment.md](deployment.md)
