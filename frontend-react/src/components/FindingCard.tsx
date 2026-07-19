import type { Finding } from '../api/client'
import type { ReviewStatus } from '../lib/localPrefs'

const FEEDBACK_LABELS = [
  'helpful',
  'not_helpful',
  'unsupported',
  'wrong_speaker',
  'wrong_evidence',
  'too_speculative',
  'too_clinical',
  'too_vague',
  'actionably_useful',
  'unsafe_framing',
  'pinned',
] as const

type Props = {
  finding: Finding
  selected?: boolean
  onSelectEvidence?: (quoteId: string) => void
  onFeedback?: (findingKey: string, rating: string) => void
  onReview?: (findingKey: string, status: ReviewStatus) => void
  findingKey?: string
  reviewStatus?: ReviewStatus
}

export function FindingCard({
  finding,
  selected,
  onSelectEvidence,
  onFeedback,
  onReview,
  findingKey,
  reviewStatus = 'unreviewed',
}: Props) {
  const conf = (finding.confidence || 'moderate').toLowerCase()
  const hasEvidence = (finding.evidence_quote_ids || []).length > 0
  return (
    <article
      className="card"
      style={{
        borderColor: selected ? 'var(--accent)' : undefined,
        opacity: hasEvidence ? 1 : 0.85,
      }}
    >
      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '0.4rem' }}>
        <span
          className={`badge badge-${conf === 'high' || conf === 'observed' ? 'high' : conf === 'low' ? 'low' : 'moderate'}`}
        >
          {finding.confidence}
        </span>
        {!hasEvidence && <span className="badge badge-flag">no evidence</span>}
        {finding.type && <span className="badge">{finding.type}</span>}
        {finding.module_run_id && (
          <span className="badge" title="module / source run">
            {finding.module_run_id}
          </span>
        )}
        <span className="badge">{reviewStatus}</span>
      </div>
      <h3 style={{ margin: '0 0 0.35rem', fontSize: '1rem' }}>{finding.title}</h3>
      <p className="muted" style={{ marginTop: 0 }}>
        {finding.summary}
      </p>
      {(finding.alternative_explanations || []).length > 0 && (
        <p style={{ fontSize: '0.9rem' }}>
          <strong>Alternatives:</strong> {finding.alternative_explanations?.join('; ')}
        </p>
      )}
      {(finding.limitations || []).length > 0 && (
        <p className="muted" style={{ fontSize: '0.85rem' }}>
          Limitations: {finding.limitations?.join('; ')}
        </p>
      )}
      <button
        type="button"
        className="btn"
        style={{ marginTop: '0.35rem' }}
        onClick={() => navigator.clipboard.writeText(JSON.stringify(finding, null, 2))}
      >
        Copy finding JSON
      </button>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem', marginTop: '0.5rem' }}>
        {(finding.evidence_quote_ids || []).map((qid) => (
          <button key={qid} className="btn" type="button" onClick={() => onSelectEvidence?.(qid)}>
            {qid}
          </button>
        ))}
      </div>
      {onReview && findingKey && (
        <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.35rem', flexWrap: 'wrap' }}>
          {(['accepted', 'rejected', 'needs_followup', 'unreviewed'] as ReviewStatus[]).map((s) => (
            <button
              key={s}
              type="button"
              className={`btn ${reviewStatus === s ? 'btn-primary' : ''}`}
              onClick={() => onReview(findingKey, s)}
            >
              {s}
            </button>
          ))}
        </div>
      )}
      {onFeedback && findingKey && (
        <div style={{ marginTop: '0.75rem' }}>
          <label className="muted" style={{ fontSize: '0.8rem' }}>
            Feedback
          </label>
          <select
            defaultValue=""
            onChange={(e) => {
              if (e.target.value) onFeedback(findingKey, e.target.value)
              e.target.value = ''
            }}
          >
            <option value="" disabled>
              Choose label…
            </option>
            {FEEDBACK_LABELS.map((label) => (
              <option key={label} value={label}>
                {label}
              </option>
            ))}
          </select>
        </div>
      )}
    </article>
  )
}
