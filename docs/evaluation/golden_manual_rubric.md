# Golden Manual Review Rubric (v0.7 P5)

Use with `expected_signals.md` for human evaluation of live or sampled module/workflow runs.

## Pass criteria (signal-based)

1. **Evidence** — Important findings cite quote IDs that exist in the evidence index.
2. **Constructs** — Module-appropriate constructs from `expected_assertions.yaml` / `expected_constructs` appear (soft; not every module must hit every signal).
3. **Confidence** — High confidence only for directly supported claims; speculative claims stay low/exploratory.
4. **Negative bounds** — No high-confidence diagnosis, abuse adjudication, personality disorder, or stable trait claims from a single transcript.
5. **Repair / agreement** — Where the fixture includes repair or procedural agreement, those signals are detected by at least one relevant module.
6. **Safety language** — No forbidden clinical/legal overclaim patterns (see safety validator).

## Scoring shorthand

| Score | Meaning |
|-------|---------|
| Pass | Meets criteria above for this fixture |
| Soft fail | Missing a soft signal or weak coverage warning only |
| Hard fail | Missing evidence, forbidden claim, or schema/safety violation |

## Review notes

Store reviewer notes under `tmp/golden_runs/` or `tests/golden_results/` — never overwrite fixture files.
