# 006 — Worker Atomicity and Operational Safety

## Phase Goal

Close the remaining **atomic claim** gap and verify worker queue safety before broader usage.

Much of queue observability already shipped in v1.1 (Phase **50**): max in-flight, queue metrics, stale recovery patterns, health checks, and alarms. This phase focuses on **true concurrent claim** (no fetch-then-update race) and tests that prove it.

**Status:** Complete · Tests: `tests/test_phase_006_worker_atomicity.py`

---

# Problem

If multiple workers poll for queued jobs, the same workflow run may be claimed twice unless claiming is atomic.

This can cause:

- duplicate reports
- inconsistent module runs
- higher model costs
- confusing user experience
- trust loss

---

# Recommended Claim Pattern

Use atomic SQL update:

```sql
UPDATE workflow_runs
SET status = 'running_modules',
    attempt_count = attempt_count + 1,
    started_at = now()
WHERE id = :id
  AND status = 'created'
  AND cancel_requested = false
```

Or use:

```sql
SELECT ...
FOR UPDATE SKIP LOCKED
```

for Postgres-backed queue claiming.

Implemented as a conditional SQLAlchemy `UPDATE … WHERE status='created' AND cancel_requested=false` in `WorkflowRunRepository.claim_queued` (portable across SQLite and Postgres).

---

# Implementation Tasks

## Worker Claiming (primary gap)

- [x] Replace fetch-then-update claim logic with atomic claim (`UPDATE … WHERE status=created RETURNING` or `FOR UPDATE SKIP LOCKED`).
- [x] Ensure cancellation is respected during claim.
- [x] Confirm max jobs claimed per poll / max in-flight still enforced (likely already present from v1.1 — verify, do not rebuild).
- [x] Confirm retry exhaustion + stale job recovery still correct after atomic claim change.

## Operational Metrics (verify / fill gaps)

- [x] Queue depth / oldest age / running / failed metrics exist from v1.1 — re-verify after claim change.
- [x] Add any missing metric only if atomic-claim work regresses observability.
- [x] Confirm CloudWatch alarms and worker health checks still fire.

## Tests

- [x] Simulate two workers claiming the same job.
- [x] Verify only one worker succeeds.
- [x] Verify canceled jobs are not claimed.
- [x] Verify stale jobs can be recovered.
- [x] Verify retry exhaustion.
- [x] Verify queue metrics remain emitted or callable.

---

# Acceptance Criteria

- Concurrent workers cannot claim the same job.
- Duplicate workflow execution is prevented.
- Worker queue behavior is observable.
- Failed/stale jobs are recoverable or visible.
- Metrics are not emitted too frequently.
- Worker safety is sufficient for controlled UAT.
