import type { EvidenceQuote } from '../api/client'

type Props = {
  quotes: EvidenceQuote[]
  activeQuoteId?: string | null
  onClose?: () => void
}

export function EvidencePanel({ quotes, activeQuoteId, onClose }: Props) {
  const active = quotes.find((q) => q.quote_id === activeQuoteId) || quotes[0]
  return (
    <aside className="card" style={{ position: 'sticky', top: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '0.5rem' }}>
        <h3 style={{ margin: 0 }}>Evidence</h3>
        {onClose && (
          <button type="button" className="btn" onClick={onClose}>
            Close
          </button>
        )}
      </div>
      {!active ? (
        <p className="muted">Select a quote ID on a finding.</p>
      ) : (
        <>
          <p className="badge" style={{ marginTop: '0.75rem' }}>
            {active.quote_id}
            {active.speaker_label ? ` · ${active.speaker_label}` : ''}
          </p>
          <blockquote style={{ margin: '0.75rem 0', borderLeft: '3px solid var(--accent)', paddingLeft: '0.75rem' }}>
            {active.text}
          </blockquote>
        </>
      )}
      <div style={{ maxHeight: '280px', overflow: 'auto', marginTop: '0.75rem' }}>
        {quotes.map((q) => (
          <p
            key={q.quote_id}
            id={`quote-${q.quote_id}`}
            style={{
              fontSize: '0.85rem',
              background: q.quote_id === activeQuoteId ? 'var(--surface-2)' : undefined,
              padding: '0.35rem',
              borderRadius: 6,
            }}
          >
            <strong>{q.quote_id}</strong> {q.text}
          </p>
        ))}
      </div>
    </aside>
  )
}
