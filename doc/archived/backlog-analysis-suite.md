# Backlog: Analysis Suite

Future capability to run multiple analyses against a single transcript as a coordinated **suite**, rather than one purpose at a time. Suites differ by depth, runtime, and audience.

**Status:** Backlog — not implemented.

---

## Concept

An **analysis suite** is a predefined bundle of purposes run in sequence (or selectively in parallel) against one transcript. Each suite targets a different use case and time budget.

```
Transcript
    │
    ├─► Purpose 1 ──► Output 1 ──┐
    ├─► Purpose 2 ──► Output 2 ──┼─► Meta-Synthesis (optional)
    ├─► Purpose N ──► Output N ──┘
    │
    └─► Suite report (combined export)
```

**Meta-Synthesis** is a separate final step: it receives only the analysis outputs from the suite, not the original transcript. It integrates findings, resolves tensions between lenses, and produces a unified summary.

---

## Proposed Suites

### Quick Suite

| Attribute | Target |
|-----------|--------|
| **Analyses** | 2–3 |
| **Runtime** | 30–60 seconds (local LLM, typical transcript) |
| **Audience** | Fast orientation, first pass, time-constrained review |

**Candidate analyses:**

| # | Analysis | Prompt (current / planned) |
|---|----------|----------------------------|
| 1 | Relationship Conversation Analysis | `relationship_conversation_analysis` ✓ |
| 2 | Cognitive Analysis | `cognitive_analysis` ✓ |
| 3 | *(optional)* Communication Strengths Summary | *new lightweight prompt* |

**Goal:** Surface the most actionable communication and thinking patterns quickly.

---

### Therapeutic Suite

| Attribute | Target |
|-----------|--------|
| **Analyses** | 5–6 |
| **Runtime** | ~2–5 minutes |
| **Audience** | Therapists, coaches, couples working through conflict |

**Candidate analyses:**

| # | Analysis | Prompt (current / planned) |
|---|----------|----------------------------|
| 1 | Relationship Conversation Analysis | `relationship_conversation_analysis` ✓ |
| 2 | Systems Analysis | `systems_analysis` ✓ |
| 3 | Cognitive Analysis | `cognitive_analysis` ✓ |
| 4 | Escalation & Repair Mapping | *new prompt* |
| 5 | Emotional Needs & Validation Gaps | *new prompt* |
| 6 | Repair & Communication Alternatives | *new prompt* |

**Goal:** Balanced clinical-communication view without full exploratory depth.

---

### Clinical Exploration Suite

| Attribute | Target |
|-----------|--------|
| **Analyses** | 7–8 |
| **Runtime** | ~5–10 minutes |
| **Audience** | Deeper formulation work, supervised exploration, case review |

**Candidate analyses:**

| # | Analysis | Prompt (current / planned) |
|---|----------|----------------------------|
| 1 | Relationship Conversation Analysis | `relationship_conversation_analysis` ✓ |
| 2 | Exploratory Psychological Formulation | `exploratory_psychological_formulation` ✓ |
| 3 | Cognitive Analysis | `cognitive_analysis` ✓ |
| 4 | Systems Analysis | `systems_analysis` ✓ |
| 5 | Attachment & Relational Patterns (exploratory) | *new prompt* |
| 6 | Trauma-Informed Interaction Patterns (exploratory) | *new prompt* |
| 7 | Power, Safety & Emotional Risk | *new prompt* |
| 8 | Formulation Integration Notes | *new prompt* |

**Goal:** Multi-lens exploratory formulation with explicit non-diagnostic framing throughout.

---

### Research Suite

| Attribute | Target |
|-----------|--------|
| **Analyses** | All available prompts |
| **Runtime** | ~10–20+ minutes (depends on prompt count) |
| **Audience** | Research, training, comprehensive case documentation |

**Candidate analyses:**

- Run **every enabled purpose** in `config/purposes.yaml`
- Include any future prompts added to the library
- Finish with **Meta-Synthesis** (required for this suite)

**Goal:** Maximum coverage plus a single integrative document across all lenses.

---

## Meta-Synthesis Prompt

A dedicated prompt that runs **after** suite analyses complete.

| Input | Output |
|-------|--------|
| Analysis outputs only (labeled by purpose) | Integrated synthesis document |

**Does not receive:**

- The original audio
- The raw transcript

**Should produce:**

- Cross-analysis themes and contradictions
- Confidence-weighted integrated summary
- Prioritized observations (observed vs inferred)
- Unified recommendations
- Explicit gaps and limitations across analyses

**Storage:** `config/prompts/13 Meta-Synthesis.md` (to be created)

**Config sketch:**

```yaml
# config/suites.yaml (proposed)
suites:
  quick:
    name: "Quick Suite"
    purposes:
      - relationship_conversation_analysis
      - cognitive_analysis
    meta_synthesis: false

  research:
    name: "Research Suite"
    purposes: all_enabled
    meta_synthesis: true
    meta_synthesis_prompt: "13 Meta-Synthesis.md"
```

---

## Technical Approach (proposed)

### Configuration

| File | Role |
|------|------|
| `config/suites.yaml` | Suite definitions: purpose lists, ordering, meta-synthesis flag |
| `config/prompts/13 Meta-Synthesis.md` | Meta-synthesis system prompt |
| `config/purposes.yaml` | Existing single-purpose definitions (unchanged) |

### Backend

| Component | Responsibility |
|-----------|----------------|
| `SuiteRegistry` | Load suites, resolve `all_enabled`, validate purpose IDs |
| `SuiteOrchestrator` | Run analyses in sequence; collect outputs; optional parallel runs |
| `POST /api/analyze/suite` | `{ transcript, suite_id, model }` → suite results |
| `POST /api/analyze/suite/stream` | Stream progress per analysis + final synthesis |
| Meta-synthesis step | Build user message from prior outputs only |

### UI

- Suite selector alongside single-purpose analysis
- Progress: `Analysis 2 of 6 — Cognitive Distortions & Core Beliefs`
- Collapsible sections per analysis output
- Meta-synthesis section at the end (when enabled)
- Export: single `.md` report with table of contents

### Runtime considerations

| Concern | Approach |
|---------|----------|
| Long runtimes | Progress streaming; optional async jobs (Phase 5) |
| Token limits | Truncate or summarize very long transcripts before suite |
| Cost / load | Quick Suite as default; warn before Research Suite |
| Failures mid-suite | Return partial results + error for failed step |

---

## Implementation Phases (suggested)

### Phase A — Suite foundation

- [ ] `config/suites.yaml` with Quick Suite (2 existing prompts)
- [ ] `SuiteRegistry` + `SuiteOrchestrator`
- [ ] `POST /api/analyze/suite`
- [ ] UI: suite selector + sequential progress

### Phase B — Meta-synthesis

- [ ] `config/prompts/13 Meta-Synthesis.md` (registered; suite wiring pending)
- [ ] Meta-synthesis step in orchestrator (outputs only)
- [ ] Research Suite definition

### Phase C — Full suite library

- [ ] Therapeutic Suite (+ new prompts)
- [ ] Clinical Exploration Suite (+ new prompts)
- [ ] Streaming suite progress
- [ ] Combined export format

### Phase D — Polish

- [ ] Suite runtime estimates in UI
- [ ] Partial-failure recovery
- [ ] Per-suite default models

---

## Open Questions

1. **Parallel vs sequential** — Run analyses in parallel for speed, or sequential to stay within local GPU/CPU limits?
2. **New prompts** — Which therapeutic/clinical prompts to author first?
3. **Meta-synthesis model** — Same Ollama model as analyses, or a larger model for synthesis only?
4. **Transcript editing** — Apply once before the suite, or allow per-analysis overrides?
5. **Privacy** — Meta-synthesis without transcript reduces re-exposure; document this as a feature for sensitive workflows.

---

## Related docs

- [implementation-plan.md](implementation-plan.md) — current phased delivery
- [../config/prompts/README.md](../config/prompts/README.md) — prompt storage conventions
