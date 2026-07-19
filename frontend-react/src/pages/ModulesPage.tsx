import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'

export function ModulesPage() {
  const lifeQ = useQuery({ queryKey: ['module-lifecycle'], queryFn: api.moduleLifecycle })

  return (
    <section>
      <h1 style={{ marginBottom: '0.35rem' }}>Module lifecycle</h1>
      <p className="muted">{lifeQ.data?.compatibility_note}</p>
      {lifeQ.isLoading && <p className="muted">Loading…</p>}
      {lifeQ.isError && (
        <p style={{ color: 'var(--danger)' }}>{(lifeQ.error as Error).message}</p>
      )}
      <div style={{ display: 'grid', gap: '0.75rem', marginTop: '1rem' }}>
        {(lifeQ.data?.modules || []).map((m) => (
          <article key={m.id} className="card">
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
              <h2 style={{ margin: 0, fontSize: '1.05rem' }}>{m.name}</h2>
              <span className="badge">{m.version}</span>
              {m.deprecated ? (
                <span className="badge badge-flag">deprecated / disabled</span>
              ) : (
                <span className="badge badge-high">enabled</span>
              )}
            </div>
            <p className="muted" style={{ marginBottom: '0.35rem' }}>
              <code>{m.id}</code> · schema {m.output_schema}
            </p>
            <p style={{ marginTop: 0 }}>{m.description || 'No description.'}</p>
            <p className="muted" style={{ fontSize: '0.8rem', wordBreak: 'break-all' }}>
              Prompt {m.prompt_file} · sha256 {m.prompt_sha256.slice(0, 16)}…
            </p>
          </article>
        ))}
      </div>
    </section>
  )
}
