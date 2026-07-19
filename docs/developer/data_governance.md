# Data governance and recovery (v1.4)

## Retention (dev defaults)

| Asset | Retention | Notes |
|-------|-----------|-------|
| CloudWatch logs | `log_retention_days` (default 14) | Redacted; not a durable case archive |
| RDS (Postgres) | Manual snapshots + automated backups per RDS settings | Primary system of record |
| S3 uploads | Bucket lifecycle TBD; delete with transcript where applicable | Audio objects if present |
| Temp audio | Ephemeral `/tmp` on tasks | Not durable |

Product guidance: delete transcripts/cases when no longer needed. Long-term clinical archives are out of scope unless explicitly commissioned.

## Backup / restore drill

1. Confirm automated RDS backup window in AWS console (`infra/dev/rds.tf`).
2. Create a manual snapshot labeled `rre-dev-drill-YYYYMMDD`.
3. Restore to a **new** instance (never overwrite prod/dev blindly).
4. Point a throwaway task or local tunnel at the restored DB; verify `transcripts` / `cases` counts.
5. Document restore time and gaps; delete the drill instance and snapshot when finished.
6. Rotate any temporary credentials used for the drill.

## Delete / export verification

- API: transcript cascade delete (legacy `/api` + product flows); case `DELETE /api/v1/cases/{id}`.
- Export: report package JSON from React; prefer redaction defaults.
- After delete, confirm rows gone and S3 objects removed when upload keys existed.

## Secret rotation

| Secret | Location | Rotation |
|--------|----------|----------|
| `API_KEY` | Secrets Manager | Generate new value; update secret JSON; bounce API/UI/web tasks; update local `.env` |
| `DATABASE_URL` | Secrets Manager | Rotate RDS password → update secret → bounce API/worker |

Record rotation in ops notes; invalidate old API keys immediately.

## Audit / privacy

- Finding feedback and workflow runs provide operational audit trails.
- Privacy notice lifecycle: keep captions in UI Settings + user docs; revisit on multi-user auth.
- Review CloudWatch for accidental PII (should be redacted).

## Audio objects

If persistent audio exists in S3, apply the same retention as the parent transcript and delete on cascade. Prefer no long-lived raw audio in shared UAT.
