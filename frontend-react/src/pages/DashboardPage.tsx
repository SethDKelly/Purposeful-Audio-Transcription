import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { listSavedReports } from '../lib/localPrefs'

export function DashboardPage() {
  const casesQ = useQuery({ queryKey: ['cases'], queryFn: api.listCases })
  const modulesQ = useQuery({ queryKey: ['modules'], queryFn: api.listModules })
  const healthQ = useQuery({ queryKey: ['health'], queryFn: api.health })
  const saved = listSavedReports()

  return (
    <section>
      <h1 style={{ marginBottom: '0.35rem' }}>Dashboard</h1>
      <p className="muted">Primary product shell — ingest, cases, reports, and module lifecycle.</p>

      <div className="layout-split" style={{ marginTop: '1rem' }}>
        <div className="card">
          <h2 style={{ marginTop: 0 }}>Start</h2>
          <p className="muted">Paste a transcript or open an existing case.</p>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <Link className="btn btn-primary" to="/ingest">
              Ingest transcript
            </Link>
            <Link className="btn" to="/cases">
              Cases
            </Link>
            <Link className="btn" to="/modules">
              Modules
            </Link>
          </div>
          <p className="muted" style={{ marginTop: '1rem', fontSize: '0.85rem' }}>
            API health: {healthQ.isLoading ? '…' : healthQ.data?.status || 'unavailable'}
          </p>
        </div>

        <div className="card">
          <h2 style={{ marginTop: 0 }}>Cases</h2>
          {(casesQ.data?.cases || []).slice(0, 6).map((c) => (
            <div key={c.id} style={{ marginBottom: '0.4rem' }}>
              <Link to="/cases">{c.title}</Link>
              <span className="muted"> · {c.created_at.slice(0, 10)}</span>
            </div>
          ))}
          {!casesQ.data?.cases?.length && <p className="muted">No cases yet.</p>}
        </div>
      </div>

      <div className="layout-split" style={{ marginTop: '1rem' }}>
        <div className="card">
          <h2 style={{ marginTop: 0 }}>Saved reports</h2>
          {saved.length === 0 ? (
            <p className="muted">Pin reports from the report viewer.</p>
          ) : (
            <ul>
              {saved.map((id) => (
                <li key={id}>
                  <Link to={`/runs/${id}/report`}>{id}</Link>
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className="card">
          <h2 style={{ marginTop: 0 }}>Modules</h2>
          <p className="muted">
            {(modulesQ.data?.modules || []).filter((m) => m.enabled).length} enabled ·{' '}
            {(modulesQ.data?.modules || []).length} total
          </p>
          <Link className="btn" to="/modules">
            Open lifecycle
          </Link>
        </div>
      </div>
    </section>
  )
}
