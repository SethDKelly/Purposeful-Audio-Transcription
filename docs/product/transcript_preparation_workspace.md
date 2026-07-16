# Transcript Preparation Workspace (v0.7 Priority 2)

**Status:** Shipped in **v0.7.0** (edit + exclude + ready gate; split/merge deferred). Roadmap: [../planning/roadmap_v0.7_to_v1.0.md](../planning/roadmap_v0.7_to_v1.0.md). UI: Streamlit prepare/analyze steps in `ui/streamlit_app.py`.

## Problem

Generated transcripts (paste or Transcribe) often need speaker label fixes, turn cleanup, and exclusion of irrelevant sections. Running analysis on an unreviewed transcript wastes cost and reduces trust.

## Required capabilities

1. Review screen before workflow execution
2. Edit speaker labels and turn text
3. Split/merge turns when feasible; delete irrelevant turns
4. Mark sections **excluded from analysis**
5. Regenerate quote IDs / evidence index after edits
6. Quality warnings (empty speakers, very short turns, low diarization confidence if available)
7. Explicit **Ready to Analyze** confirmation (opt-in skip with clear warning)

## Acceptance

Edited approved transcript is the sole source for evidence index + workflow engine. Quote IDs stable within the approved version. Analysis cannot accidentally run against unapproved generated text unless the user skips intentionally.

## Out of scope here

- Split/merge turns — deferred (edit + exclude cover the primary review path for v0.7).
- Multi-file audio stitch → [../planning/future_considerations.md](../planning/future_considerations.md).
- Case attachment → v0.9.
