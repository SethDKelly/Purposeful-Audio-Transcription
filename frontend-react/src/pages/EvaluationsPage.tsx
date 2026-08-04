import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'

export function EvaluationsPage() {
  const evalsQ = useQuery({ queryKey: ['evaluations'], queryFn: api.listEvaluations })

  return (
    <section>
      <h1 style={{ marginBottom: '0.35rem' }}>Evaluation runs</h1>
      <p className="muted">
        Persisted offline golden / release-gate results. CI also runs safety + golden gates on
        release workflows.
      </p>
      {evalsQ.isLoading && <p className="muted">Loading…</p>}
      {evalsQ.isError && (
        <p style={{ color: 'var(--danger)' }}>{(evalsQ.error as Error).message}</p>
      )}
      <div style={{ display: 'grid', gap: '0.75rem', marginTop: '1rem' }}>
        {(evalsQ.data?.runs || []).map((r) => (
          <article key={r.id} className="card">
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <strong>{r.kind}</strong>
              <span className={`badge ${r.gate_passed ? 'badge-high' : 'badge-flag'}`}>
                {r.gate_passed ? 'gate passed' : 'gate failed'}
              </span>
            </div>
            <p className="muted" style={{ marginBottom: 0 }}>
              {r.fixture_id || '—'} · {r.module_id || '—'} · {r.created_at || ''}
            </p>
          </article>
        ))}
        {!evalsQ.data?.runs?.length && <p className="muted">No evaluation runs recorded yet.</p>}
      </div>
    </section>
  )
}
