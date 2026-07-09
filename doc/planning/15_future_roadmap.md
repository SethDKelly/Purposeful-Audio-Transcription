# 15 — Future Roadmap

> **Completed items:** Many near-term items below shipped in **v0.3.0** (phases H–L). See [../releases/v0.3.0.md](../releases/v0.3.0.md) and the active forward plan [18_post_v0.3_plan.md](18_post_v0.3_plan.md).

## Completed in v0.3.0

- Remaining modules (13 total) and workflows (5): Quick Review, Conflict Coaching, Mediation Brief, Clinical Exploration, Full MVP
- Export options: Markdown, PDF, JSON, coach summary, mediation brief
- Knowledge graph + interactive exploration APIs and Streamlit Explore tab
- PostgreSQL, migrations, background jobs, API key auth
- Comparative analysis (workflow runs on same transcript)

## Near-Term Enhancements (remaining)

### Speaker diarization (next — Phase M)

**Status:** Not implemented. Audio upload produces a single **Speaker 1** block; Whisper does not identify who spoke when.

Planned:

- [pyannote.audio](https://github.com/pyannote/pyannote-audio) diarization (local, `HF_TOKEN` for model access)
- Align diarization timeline with Whisper segments → `Person A` / `Person B` labeled turns
- Integrate with existing transcript parser and evidence index

See [18_post_v0.3_plan.md](18_post_v0.3_plan.md) §4.

### Workflow library (gaps)

- **Full Multidisciplinary Suite** — all transcript modules + meta-synthesis
- **Research-Oriented Analysis** — pattern-focused module chain

### Knowledge Graph UI

Show relationships between needs, behaviors, emotions, cycles, narratives, interventions.

**Status:** API + basic Streamlit Mermaid in v0.3.0; needs richer construct population (see Phase O in [18_post_v0.3_plan.md](18_post_v0.3_plan.md)).

### Interactive Exploration

**Status:** Drill-down, cross-module, follow-up Q&A in v0.3.0. Remaining:

- What would change this conclusion? (preset counterfactuals)
- React frontend

### Comparative Analysis

**Status:** Compare workflow runs on one transcript in v0.3.0. Remaining:

- Cross-transcript / case-level progress tracking
- Pattern change and theme evolution over time

### Module Customization

Allow advanced users to:

- include/exclude modules
- adjust depth
- choose coaching vs clinical tone
- choose output format

## Long-Term Enhancements

### Audio/Video Inputs

**Status:** Whisper transcription + streaming progress shipped; **speaker diarization planned (Phase M)**.

Potential future features beyond diarization:
- timing analysis
- interruption detection
- pause detection

Be cautious with tone/emotion inference.

### Collaborative Review

Allow multiple participants to:

- add context
- respond to findings
- mark findings as helpful/unhelpful
- create shared agreements

### Professional Mode

For therapists/coaches/mediators:

- case notes
- session comparison
- exportable reports
- supervision notes
- treatment planning support

### Ontology-Driven Prompt Generation

Move from static templates to generated prompts based on:

- selected constructs
- module metadata
- workflow goals
- desired output schema
- user context

## Strategic Direction

The strongest long-term architecture treats the application as a reasoning platform:

```text
Domain Model
  → Ontology
  → Module Definitions
  → Workflow Engine
  → Prompt Compiler
  → Structured Findings
  → Synthesis Engine
  → Interactive UI
```

The prompts are important, but they should remain replaceable.

The enduring assets are:

- domain model
- ontology
- evidence model
- confidence model
- workflow design
- structured data
- synthesis logic
