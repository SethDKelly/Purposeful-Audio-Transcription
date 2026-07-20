import { useEffect, useState } from 'react'
import type { EvidenceQuote } from '../api/client'

type Props = {
  quotes: EvidenceQuote[]
  activeQuoteId?: string | null
  onClose?: () => void
}

function conciseText(quote: EvidenceQuote): string {
  if (quote.span_text?.trim()) return quote.span_text.trim()
  const text = quote.text || ''
  if (text.length <= 360) return text
  const sentence = text.split(/(?<=[.!?])\s+/)[0]?.trim()
  if (sentence && sentence.length < text.length) return sentence
  return `${text.slice(0, 357)}...`
}

export function EvidencePanel({ quotes, activeQuoteId, onClose }: Props) {
  const [showContext, setShowContext] = useState(false)
  const active = quotes.find((q) => q.quote_id === activeQuoteId) || quotes[0]

  useEffect(() => {
    setShowContext(false)
  }, [activeQuoteId])
  const hasContext = Boolean(active?.context_before || active?.context_after)
  const fullLongerThanConcise =
    active && conciseText(active) !== (active.text || '').trim()

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
            {active.evidence_type ? ` · ${active.evidence_type.replace('_', ' ')}` : ''}
          </p>
          {showContext && active.context_before ? (
            <p className="muted" style={{ fontSize: '0.85rem', marginBottom: '0.35rem' }}>
              Previous: {active.context_before}
            </p>
          ) : null}
          <blockquote
            style={{ margin: '0.75rem 0', borderLeft: '3px solid var(--accent)', paddingLeft: '0.75rem' }}
          >
            {showContext ? active.text : conciseText(active)}
          </blockquote>
          {showContext && active.context_after ? (
            <p className="muted" style={{ fontSize: '0.85rem', marginTop: '0.35rem' }}>
              Next: {active.context_after}
            </p>
          ) : null}
          {(hasContext || fullLongerThanConcise) && (
            <button
              type="button"
              className="btn"
              style={{ marginTop: '0.35rem' }}
              onClick={() => setShowContext((v) => !v)}
            >
              {showContext ? 'Hide context' : 'Show context'}
            </button>
          )}
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
            <strong>{q.quote_id}</strong>
            {q.speaker_label ? ` · ${q.speaker_label}` : ''} {conciseText(q)}
          </p>
        ))}
      </div>
    </aside>
  )
}
