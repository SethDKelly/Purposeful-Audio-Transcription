# Prompt Storage

Analysis prompts live in this directory as Markdown files. Purposes in `config/purposes.yaml` reference prompt files by name.

## Naming convention

Prompt files use **numbered, descriptive names** with spaces:

```
01 Relationship Conversation Analysis.md
02 Exploratory Psychological Formulation.md
...
13 Meta-Synthesis.md
```

- Two-digit prefix controls display order
- Descriptive title matches the analysis purpose
- Quote filenames in `purposes.yaml` when they contain spaces or `&`

## Adding a new purpose

1. Create a prompt file here, e.g. `14 Meeting Summary Analysis.md`
2. Add an entry to `config/purposes.yaml`:

```yaml
purposes:
  meeting_summary:
    name: "Meeting Summary"
    description: "Summarize key decisions and action items."
    enabled: true
    ollama_model: null
    system_prompt_file: "14 Meeting Summary Analysis.md"
    user_prompt_template: |
      Summarize the following transcript:

      ---
      {transcript}
      ---
```

3. Restart the API (or rely on reload in dev mode) and select the new purpose in the UI.

Set `ollama_model` per purpose when ready, or use `DEFAULT_OLLAMA_MODEL` in `.env`.

## Current prompts

| File | Purpose |
|------|---------|
| `01 Relationship Conversation Analysis.md` | Relationship conversation analysis |
| `02 Exploratory Psychological Formulation.md` | Exploratory psychological formulation |
| `03 Cognitive Analysis.md` | Cognitive distortions and core beliefs |
| `04 Systems Analysis.md` | Systems and family systems analysis |
| `05 Mediation Analysis.md` | Conflict resolution and mediation analysis |
| `06 Gottman Analysis.md` | Gottman Method relationship analysis |
| `07 NVC Analysis.md` | Nonviolent communication analysis |
| `08 Attachment Interaction Matrix.md` | Attachment interaction matrix analysis |
| `09 Trauma-Informed Communication.md` | Trauma-informed communication analysis |
| `10 Emotional Needs & Values.md` | Emotional needs and values analysis |
| `11 Narrative Identity Analysis.md` | Narrative identity and meaning-making analysis |
| `12 Bias & Epistemic Quality.md` | Bias, reliability, and epistemic quality analysis |
| `13 Meta-Synthesis.md` | Integrative meta-synthesis across prior analyses |

The `{transcript}` placeholder in `user_prompt_template` is replaced at analysis time. For **Meta-Synthesis**, provide prior analysis outputs as the input (not the raw transcript).
