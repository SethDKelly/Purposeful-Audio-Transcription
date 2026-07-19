# Long-transcript chunking foundation (v1.3 Workstream G)

## Goal

Support transcripts that exceed practical single-pass evidence budgets without claiming full long-document analysis yet.

## Chunk model (v1)

```text
TranscriptChunk
  id
  transcript_id
  index
  strategy: turn_window | speaker_shift | time_window
  turn_id_start
  turn_id_end
  quote_id_prefix          # e.g. C03-
  char_count
  token_estimate
```

## Quote ID preservation

1. Global evidence index remains source of truth after prepare/rebuild.
2. Chunk-scoped runs cite **global** quote IDs (not chunk-local renumbers).
3. Optional `quote_id_prefix` is metadata for UX grouping only; IDs stay stable.
4. Excluded turns never receive quotes (existing rebuild rules).

## Length warning (product)

- Soft warn when quote count &gt; `evidence_prompt_max_quotes` (see settings).
- Hard warn / block auto-full-suite when estimated tokens exceed module budget (future).
- React prepare page already surfaces short/empty-exclusion warnings; extend with length API when exposed.

## Prototype path (not full support)

```text
long transcript
→ chunk by N turns (default 40) overlapping 5 turns
→ create chunk evidence views (filter quotes by turn range)
→ run selected modules per chunk (background jobs)
→ consolidate findings by type + quote overlap
→ synthesis over consolidated set
```

## v1.3 delivered

- This design doc
- React length/quality warnings on prepare
- Existing sampling/truncation in evidence index remains the production path

## Explicit non-claims

Do **not** claim full long-transcript support until consolidation + eval fixtures exist.
