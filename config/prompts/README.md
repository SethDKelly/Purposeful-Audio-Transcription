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
2. Add a module entry in `config/modules/meeting_summary.yaml` (see existing modules for fields)
3. Optionally add the module to a workflow in `config/workflows/`
4. Restart the API (or rely on reload in dev mode)

Set `ollama_model` per module when ready, or use `DEFAULT_OLLAMA_MODEL` in `.env`.

## Current prompts

| File | Module ID |
|------|-----------|
| `01 Relationship Conversation Analysis.md` | `relationship_conversation_analysis` |
| `02 Exploratory Psychological Formulation.md` | `exploratory_psychological_formulation` |
| `03 Cognitive Analysis.md` | `cognitive_analysis` |
| `04 Systems Analysis.md` | `systems_analysis` |
| `05 Mediation Analysis.md` | `mediation_analysis` |
| `06 Gottman Analysis.md` | `gottman_analysis` |
| `07 NVC Analysis.md` | `nvc_analysis` |
| `08 Attachment Interaction Matrix.md` | `attachment_interaction_matrix` |
| `09 Trauma-Informed Communication.md` | `trauma_informed_communication` |
| `10 Emotional Needs & Values.md` | `emotional_needs_values` |
| `11 Narrative Identity Analysis.md` | `narrative_identity_analysis` |
| `12 Bias & Epistemic Quality.md` | `bias_epistemic_quality` |
| `13 Meta-Synthesis.md` | `meta_synthesis` |

Structured modules use the prompt compiler with shared framework instructions and evidence-indexed transcripts. Meta-synthesis receives prior module JSON outputs, not the raw transcript.

## Workflows

| Workflow | Modules |
|----------|---------|
| `quick_review` | relationship, NVC, bias |
| `full_mvp` | relationship, NVC, systems, bias, meta-synthesis |
| `conflict_coaching` | relationship, NVC, needs/values, bias |
| `mediation_brief` | mediation, systems, bias |
| `clinical_exploration` | formulation, cognitive, attachment, narrative, bias, meta-synthesis |
