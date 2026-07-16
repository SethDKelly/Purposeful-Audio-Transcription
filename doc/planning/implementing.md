# Implementing — Active Priorities

Material work in flight or next to ship for the **Relationship Reasoning Engine (RRE)**. Completed: [completed.md](completed.md). Optional future work: [backlog.md](backlog.md).

| | |
|---|---|
| **Status** | **Tier 2 closeout** — P1-3/P1-4a–e/P1-7 done; P1-4f burn-in in progress on AWS; then merge path + P1-5 |
| **Branch** | `tier-2-p1-trust-workflows` (from `main` @ v0.5.1) |
| **Strategy** | **AWS only** — Bedrock + Transcribe + ECS + RDS (account `521018312783`, `us-east-2`) via [aws-backbone](https://github.com/SethDKelly/aws-backbone). No local Whisper/Ollama product runtime. |
| **Cost control** | **Pause AWS when idle** (standing). Deploy wakes only on runtime/infra path pushes to `main`. See [aws-operations.md](../developer/aws-operations.md) |
| **Architecture** | [aws-deployment.md](aws-deployment.md) |
| **Design anchors** | [../design/01_product_vision_and_scope.md](../design/01_product_vision_and_scope.md) |

**Scope rule:** Items here **need to ship** or **materially improve** reliability, deployability, or core product value. Work top to bottom within each tier.

**Platform constraint:** During transcript analysis, transcription, and synthesis in AWS, the application must **not** call external APIs (off-host Ollama, Hugging Face, public model registries). Model operations use AWS services or in-VPC endpoints.

**Strategic architecture (unchanged):**

```text
Domain Model → Ontology → Module Definitions → Workflow Engine → Prompt Compiler
  → Structured Findings → Synthesis Engine → Interactive UI
```

Prompts are replaceable; enduring assets are the domain model, evidence/confidence model, workflow design, and structured data.

---

## Priority framework

| Tier | Meaning | When |
|------|---------|------|
| **1 — Critical** | Blocks cloud validation, Bedrock proof, or secure AWS operation | Done (gate held) |
| **2 — Significant** | Core product on AWS — trust, workflows, prune, burn-in, CI | **Now** |
| **3 — Materially important** | Application depth — ontology, cases, customization | After v0.6.0 Tier 2 closeout |

---

## Product vision gaps (remaining)

| Vision item | Gap | Tier |
|-------------|-----|------|
| Full Multidisciplinary Suite | Workflow + mocked tests ✓; **live Bedrock burn-in** (P1-4f) | 2 |
| Research-oriented analysis | Workflow + mocked tests ✓; **live Bedrock burn-in** (P1-4f) | 2 |
| Interactive exploration | No counterfactual presets | 3 (P2-O) / backlog |
| Knowledge graph | APIs exist; constructs/relationships rarely populated | 3 (P2-O) |
| Longitudinal / progress tracking | Same-transcript compare only; no case view | 3 (P2-P) |
| Multi-part recordings | One audio file per transcript; no ordered stitch across successive clips | 3 (P2-A) |
| Module customization | Fixed YAML workflows only | 3 (P2-Q) |
| Professional mode | No case files, session series, finding feedback | 3 (P2-P, P2-R) |
| Data residency | VPC Stage B + in-account Bedrock/Transcribe | ✓ |
| Secure client connection | Public ALB is **HTTP only**; optional `API_KEY` unused in UI (P2-R2). HTTPS/TLS → [backlog](backlog.md) — promote before external UAT of sensitive audio | Backlog → promote |

---

## Immediate next steps (post this branch)

```text
[x] v0.5.1 on `main` · Tier 2 branch · P1-3 trust · P1-4a–e workflows · P1-7 AWS-only prune
[ ] P1-4f — finish live burn-in (`research_oriented` + `full_multidisciplinary`); record run IDs
[ ] Push remaining branch commits if any · Deploy once · confirm synthesis findings in UI
[ ] Merge `tier-2-p1-trust-workflows` → `main` (toward v0.6.0) · Pause AWS when idle
[ ] P1-5 remaining — lockfile + golden fixtures (pre-commit / health hardening already on branch)
[ ] P1-6 — broader workflow burn-in on anonymized fixtures (no Ollama)
[ ] Then Tier 3 (P2-O ontology population first)
```

**Standing ops rule:** When AWS is idle, run **Pause AWS_dev**. Resume with **Deploy to AWS_dev**. Docs-only pushes do **not** deploy. [aws-operations.md](../developer/aws-operations.md) · [infra/dev/README.md](../../infra/dev/README.md).

**Burn-in helper:** `python scripts/p1_4f_burnin.py <alb-url>` — requires `background=true` long suites; fails if synthesis returns zero findings.

**Burn-in (2026-07-14+ on branch):** Quick Review / Transcribe previously green. Research-oriented completed live with meta-synthesis findings on Bedrock (buckets populated; API `findings` rollup added for clients). Full multidisciplinary burn-in in progress / affirm before checkmark.

---

## Quality review — gaps to track (Jul 2026)

Findings from AWS-only prune + long-suite burn-in. Items **not** previously first-class in the plan are called out.

| Gap | Severity | Disposition |
|-----|----------|-------------|
| Bedrock prose / markdown-outside-JSON failing modules | High | ✓ Mitigated — JSON-only prompts, structured `outputConfig`, alternative_explanations fill |
| `/api/live` failing under Converse load → ELB drain / deploy thrash | High | ✓ Mitigated — 2 uvicorn workers, ALB `unhealthy_threshold=10`, `min_healthy%=0` |
| Burn-in counted `findings=0` while buckets had data | High (false negative) | ✓ API `findings` rollup + burn-in asserts non-empty |
| Meta parse preferred empty confidence buckets over `findings[]` | High (latent) | ✓ Safer `_is_synthesis_output_shape` |
| No pre-commit / config cross-check | Medium | ✓ Tier 1–2 hooks + CI `validate_*` |
| Compact meta handoff (drop `raw_markdown_report`) | Medium | ✓ Done — Bedrock token efficiency |
| Separate compute worker vs API servers | Medium | **Backlog** — promote if single-task still flaps under load |
| Workflow cancel mid-run | Medium | P2-R6 (promote earlier if burn-in UX needs it) |
| Streamlit non-ASCII / encoding footguns | Low | Contributing: prefer ASCII UI separators |
| Pin deps / golden LLM fixtures | Medium | **P1-5** remaining |
| Construct / relationship population | Product depth | **P2-O** |
| Multi-worker: only leader resumes incomplete jobs | Acceptable | Documented via PG advisory lock at startup |

---

## Tier 1 — Critical

**Complete** for the AWS pivot gate (Quick Review on Bedrock, Stage B, Transcribe, smoke).

### Finish P0-AWS — Bedrock proof & secure AWS_dev

| # | Task | Notes |
|---|------|-------|
| **AWS-5h** | VPC endpoints Stage B | ✓ |
| **AWS-5g** | Secrets Manager: `HF_TOKEN` | **Skipped** — Transcribe replaces pyannote |
| **AWS-3f** | Deploy smoke beyond `/api/health` | ✓ |
| **AWS-6f** | Deploy trigger → `main` | ✓ |
| **AWS-6g** | Pause AWS when idle | ✓ Standing practice |
| **AWS-1b** | Formal LLM evaluation note | ✓ [llm-evaluation-bedrock.md](llm-evaluation-bedrock.md) |
| **AWS-1c** | Formal ASR evaluation note | ✓ [asr-evaluation-transcribe.md](asr-evaluation-transcribe.md) |
| **AWS-1d** | Document no-egress network model | ✓ [aws-deployment.md](aws-deployment.md) |

### Runtime profile (AWS only)

| Profile | API image | LLM | Audio ingest |
|---------|-----------|-----|--------------|
| **AWS** | `Dockerfile.cloud` (2 uvicorn workers) | Bedrock | Amazon Transcribe |
| **UI** | `Dockerfile.ui` | — | — |

Local dual-path removed in **P1-7**.

---

## Tier 2 — Significant

### P1-1 — ASR migration (Amazon Transcribe) ✓

| # | Task | Status |
|---|------|--------|
| P1-1a–c | Provider + Transcribe adapter + S3 JSON path | ✓ |
| P1-1d | Whisper local path | ✓ then **removed** in P1-7 (superseded) |
| — | Live AWS Transcribe + Quick Review burn-in | ✓ 2026-07-14 |

### P1-2 — Slim cloud API image ✓

| # | Task | Status |
|---|------|--------|
| P1-2a–e | Cloud Dockerfile, CI, ECS env, sizing, docs | ✓ |
| — | Follow-on: 2 uvicorn workers + softer ALB thresholds | ✓ on branch (health under Bedrock load) |

### P1-3 — Data handling & trust ✓

| # | Task | Status |
|---|------|--------|
| P1-3a–f | Temp cleanup, cascade DELETE, redaction, privacy, retention, audit | ✓ |

### P1-4 — Workflow completeness (Phase N)

| # | Task | Status |
|---|------|--------|
| P1-4a | `full_multidisciplinary.yaml` | ✓ |
| P1-4b | `research_oriented.yaml` | ✓ |
| P1-4c | Default background for long workflows | ✓ |
| P1-4d | `WORKFLOW_SYNC_MODULE_LIMIT` + UI warning | ✓ |
| P1-4e | Mocked integration tests | ✓ |
| P1-4f | Live AWS burn-in (research + full multidisciplinary) | **In progress** — research green on Bedrock; finish full suite + record IDs |

### P1-7 — Prune local dual-path ✓

| # | Task | Status |
|---|------|--------|
| P1-7a–g | AWS-only defaults, remove Ollama/Whisper/fat image, docs | ✓ |

### P1-5 — CI & deploy reliability

**Goal:** Reproducible builds; local/CI gates that catch config and health regressions before AWS cost.

| # | Task | Status |
|---|------|--------|
| P1-5a | Pinned lockfile (`uv.lock` or equivalent) in CI and Docker | **Pending** |
| P1-5b | Golden LLM output fixtures — record/replay for integration tests | **Pending** |
| P1-5c | Container smoke in CI — health + one mocked module run (beyond AWS-3f) | **Pending** (AWS-3f already post-deploy) |
| P1-5d | Pre-commit Tier 1–2 + `validate_yaml` / `validate_config` in Deploy CI | ✓ on branch |
| P1-5e | Multi-worker uvicorn + ALB unhealthy_threshold + min_healthy 0 | ✓ on branch |
| P1-5f | Synthesis API `findings` rollup + burn-in fails on empty synthesis | ✓ on branch |

### P1-6 — Evaluation & real-world hardening

| # | Task | Status |
|---|------|--------|
| P1-6a | Burn-in: `quick_review`, `conflict_coaching`, `full_mvp` on real/anonymized transcripts (**Bedrock only**) | Pending after P1-4f |
| P1-6b | Add 3–5 anonymized scenarios to `tests/fixtures/transcripts/` | Pending |
| P1-6c | Track safety validator false positives; adjust patterns | Pending |

---

## Tier 3 — Materially important

Start after **v0.6.0** Tier 2 closeout (P1-4f done, branch merged, Pause practiced).

### P2-A — Multi-file audio upload & transcript stitching

**Goal:** When a conversation is recorded as successive clips (phone stops mid-session, multi-segment capture), users can upload multiple audio files, transcribe each individually, then stitch the transcripts in order into one evidence-ready transcript for workflows.

| # | Task | Notes |
|---|------|-------|
| P2-A1 | UI multi-file audio upload with explicit clip order | Drag-reorder or numbered list; reject empty set |
| P2-A2 | Transcribe each clip as its own ingest job | Reuse Amazon Transcribe path; surface per-clip status/errors |
| P2-A3 | Stitch API: ordered merge into one transcript | Concatenate turns/segments; adjust timestamps with cumulative offset; preserve speaker labels where Transcribe provides them |
| P2-A4 | Persist stitch provenance | Store source clip transcript IDs + order so audits and re-stitch are possible |
| P2-A5 | Run workflows on the stitched transcript | Same Analyze path as a single-file transcript; no double-charge for stitch-only |

**Acceptance:** Two+ ordered recordings → per-clip transcripts succeed → one stitched transcript → Quick Review (or longer suite) runs with continuous evidence. Partial clip failure does not silently drop order (fail visible or allow stitch of completed subset with warning).

**Non-goals (this slice):** Cross-conversation case files (P2-P); merging unrelated sessions; audio-level concat before ASR (prefer transcript stitch so failed clips stay isolatable).

### P2-O — Ontology & construct population

| # | Task |
|---|------|
| P2-O1 | Extend `output_schema_instructions.md` with construct minimums |
| P2-O2 | `PromptCompiler` optional ontology cheat-sheet |
| P2-O3 | Soft warnings + retry when `constructs` empty (`expects_constructs: true`) |
| P2-O4 | Post-parse `construct_ids` suggestions via ontology YAML |
| P2-O5 | Exploration presets: `why`, `evidence`, `counterfactual`, `agreement` |

### P2-P — Cases & longitudinal analysis

| # | Task |
|---|------|
| P2-P1–4 | Case entity, APIs, compare-across-transcripts, Streamlit case dashboard |

Related backlog (not on this slice): **Multi-conversation report pack** — export → upload several workflow reports for richer cross-session guidance without requiring every transcript to live in one case yet ([backlog.md](backlog.md#analysis--ontology-speculative--incremental)).

### P2-Q — Custom workflows

| # | Task |
|---|------|
| P2-Q1–4 | Custom run API, validation (also covered partly by `validate_config`), UI picker, tone/depth |

### P2-R — Streamlit professional polish

| # | Task | Notes |
|---|------|-------|
| P2-R1 | Human-readable confidence labels | Pending |
| P2-R2 | UI sends `X-API-Key` when set | Pending |
| P2-R3 | Background workflow toggle | ✓ (Analyze step) |
| P2-R4 | Finding feedback API + UI | Pending |
| P2-R5 | Supervision export template | Pending |
| P2-R6 | Basic workflow cancellation | **Consider promoting** after burn-in UX pain |
| P2-R7 | Coaching action plan export | Pending |

---

## Release milestones (target)

| Release | Theme | Status |
|---------|--------|--------|
| **v0.5.1** | Transcribe + slim cloud + main deploy/pause | **Released** |
| **v0.6.0** | Trust + full/research workflows + AWS-only prune + burn-in | **In progress** on `tier-2-p1-trust-workflows` |
| **v0.7.0** | Ontology + cases + multi-file audio / transcript stitch (P2-A) | Pending |
| **v1.0.0** | Stable `main` deploy + API contract | Pending |

---

## Explicitly out of scope

- Modifying **MinneAnalytics** IAM/state in aws-backbone
- Multi-user SaaS, billing, RBAC beyond API key
- Production AWS account / `prod-github-deploy`
- Runtime Hugging Face or public model downloads in AWS
- Hardcoded per-model branches
- Graph database backend
- Tone/emotion inference from audio timing
- torchcodec migration ([aws-deployment.md §5](aws-deployment.md))

**Deferred (backlog, not forbidden):** dedicated ECS worker fleet / queue for Bedrock jobs if API serving still fights long Converse under load.

---

## Decision log (active)

| Decision | Rationale |
|----------|-----------|
| **Pause AWS when idle** | Stop Fargate + RDS compute between sessions |
| **Skip AWS-5g HF_TOKEN** | Transcribe replaces pyannote on AWS |
| **S3 output for Transcribe JSON** | Stage B has no public egress |
| **`/api/live` for ALB** | Full `/api/health` can hang on Bedrock/deps |
| **2 uvicorn workers** | Keep liveness responsive during Converse |
| **Structured Bedrock JSON** | Reduce prose-only parse failures on Sonnet 4.5 |
| **Compact meta handoff** | Drop `raw_markdown_report` from prior outputs for token cost |
| **Bounded parallel transcript modules** | `WORKFLOW_MODULE_CONCURRENCY` (default 3 on Postgres); barrier before meta; SQLite serial |
| **Lean Bedrock outputs + fewer retries** | `bedrock_max_tokens=8192`, `module_run_max_retries=1`, short/empty markdown guidance |
| **Bedrock prompt caching** | Cache framework + evidence prefix across modules (`BEDROCK_PROMPT_CACHE`, TTL 1h) |
| **Constructs before React** | Graph UI useless without populated data |
| **Cases before custom workflows** | Longitudinal value for coach/therapist personas |
| **Transcript stitch over audio concat** | Process successive clips via Transcribe individually, then merge ordered transcripts (isolates clip failures; keeps speaker/timing provenance) |
| **SQLite for pytest only** | Product DB is RDS Postgres on AWS |

---

## Supporting documents

| Document | Purpose |
|----------|---------|
| [aws-deployment.md](aws-deployment.md) | AWS architecture, backbone integration, model strategy |
| [../developer/aws-operations.md](../developer/aws-operations.md) | CloudWatch, smoke, pause/resume, burn-in notes |
| [../developer/contributing.md](../developer/contributing.md) | Pre-commit + module/workflow contribution |
| **aws-backbone** (separate repo) | IAM, OIDC, `dev-github-deploy` |
