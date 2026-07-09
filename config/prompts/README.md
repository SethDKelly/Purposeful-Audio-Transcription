# Prompt Storage

Analysis prompts live in this directory as Markdown files. Module definitions in `config/modules/*.yaml` reference prompt files by name.

## Naming convention

Prompt files use **numbered, descriptive names** with spaces:

```
01 Relationship Conversation Analysis.md
02 Exploratory Psychological Formulation.md
...
13 Meta-Synthesis.md
```

- Two-digit prefix controls display order
- Descriptive title matches the analysis module
- Quote filenames in module YAML when they contain spaces or `&`

## Adding a new module

1. Create a prompt file here, e.g. `14 Meeting Summary Analysis.md`
2. Add a module entry in `config/modules/meeting_summary.yaml`:

```yaml
id: meeting_summary
name: "Meeting Summary"
version: "1.0.0"
enabled: true
description: "Summarize key decisions and action items."
primary_lens: "Meeting facilitation"
analytical_level: observable
unit_of_analysis: interaction
primary_question: "What decisions and action items appear in this conversation?"
confidence_ceiling: moderate
inference_depth: low
dependencies:
  - transcript_preprocessing
output_schema: module_output_v1
prompt_file: "14 Meeting Summary Analysis.md"
ollama_model: null
input_type: transcript
```

3. Optionally add the module to a workflow in `config/workflows/`
4. Restart the API (or rely on reload in dev mode)

Set `ollama_model` per module when ready, or use `DEFAULT_OLLAMA_MODEL` in `.env`.

## Current prompts

| File | Module |
|------|--------|
| `01 Relationship Conversation Analysis.md` | `relationship_conversation_analysis` |
| `02 Exploratory Psychological Formulation.md` | _(not in MVP module set)_ |
| `03 Cognitive Analysis.md` | _(not in MVP module set)_ |
| `04 Systems Analysis.md` | `systems_analysis` |
| `05 Mediation Analysis.md` | _(not in MVP module set)_ |
| `06 Gottman Analysis.md` | _(not in MVP module set)_ |
| `07 NVC Analysis.md` | `nvc_analysis` |
| `08 Attachment Interaction Matrix.md` | _(not in MVP module set)_ |
| `09 Trauma-Informed Communication.md` | _(not in MVP module set)_ |
| `10 Emotional Needs & Values.md` | _(not in MVP module set)_ |
| `11 Narrative Identity Analysis.md` | _(not in MVP module set)_ |
| `12 Bias & Epistemic Quality.md` | `bias_epistemic_quality` |
| `13 Meta-Synthesis.md` | `meta_synthesis` |

Structured modules use the prompt compiler with shared framework instructions and evidence-indexed transcripts. Meta-synthesis receives prior module JSON outputs, not the raw transcript.
