import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useParams, useSearchParams } from 'react-router-dom'
import { api, type KnowledgeGraphNode } from '../api/client'

function confidenceColor(c?: string | null) {
  const v = (c || '').toLowerCase()
  if (v.includes('high') || v === 'observed') return 'var(--ok)'
  if (v.includes('low') || v.includes('explor')) return 'var(--warn)'
  return 'var(--accent)'
}

export function GraphPage() {
  const { runId: routeRunId = '' } = useParams()
  const [params] = useSearchParams()
  const runId = routeRunId || params.get('runId') || ''
  const [moduleFilter, setModuleFilter] = useState('')
  const [confidenceFilter, setConfidenceFilter] = useState('all')
  const [selected, setSelected] = useState<KnowledgeGraphNode | null>(null)

  const graphQ = useQuery({
    queryKey: ['kg', runId],
    queryFn: () => api.getKnowledgeGraph(runId),
    enabled: Boolean(runId),
  })

  const filtered = useMemo(() => {
    const nodes = graphQ.data?.nodes || []
    const edges = graphQ.data?.edges || []
    const mod = moduleFilter.trim().toLowerCase()
    const nodesF = nodes.filter((n) => {
      if (mod && !(n.module_id || '').toLowerCase().includes(mod)) return false
      if (confidenceFilter !== 'all') {
        const c = (n.confidence || '').toLowerCase()
        if (!c.includes(confidenceFilter)) return false
      }
      return true
    })
    const ids = new Set(nodesF.map((n) => n.id))
    const edgesF = edges.filter((e) => ids.has(e.source) && ids.has(e.target))
    return { nodes: nodesF, edges: edgesF }
  }, [graphQ.data, moduleFilter, confidenceFilter])

  const layout = useMemo(() => {
    const n = filtered.nodes.length || 1
    const cx = 320
    const cy = 220
    const r = Math.min(180, 40 + n * 8)
    return filtered.nodes.map((node, i) => {
      const angle = (i / n) * Math.PI * 2
      return { ...node, x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) }
    })
  }, [filtered.nodes])

  if (!runId) {
    return (
      <section className="card">
        <h1 style={{ marginTop: 0 }}>Graph explorer</h1>
        <p className="muted">Open a report and use “Graph”, or pass ?runId=…</p>
        <Link to="/">Back to dashboard</Link>
      </section>
    )
  }

  return (
    <section>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap' }}>
        <div>
          <h1 style={{ marginBottom: 0 }}>Graph explorer</h1>
          <p className="muted">
            Run {runId} · <Link to={`/runs/${runId}/report`}>Report</Link>
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <input
            placeholder="Module filter…"
            value={moduleFilter}
            onChange={(e) => setModuleFilter(e.target.value)}
          />
          <select
            value={confidenceFilter}
            onChange={(e) => setConfidenceFilter(e.target.value)}
          >
            <option value="all">All confidence</option>
            <option value="high">High</option>
            <option value="moderate">Moderate</option>
            <option value="low">Low / exploratory</option>
          </select>
        </div>
      </div>

      {graphQ.isLoading && <p className="muted">Loading graph…</p>}
      {graphQ.isError && (
        <p style={{ color: 'var(--danger)' }}>{(graphQ.error as Error).message}</p>
      )}

      <div className="layout-split" style={{ marginTop: '1rem' }}>
        <div className="card" style={{ overflow: 'auto' }}>
          <svg width="640" height="440" role="img" aria-label="Knowledge graph">
            {filtered.edges.map((e, i) => {
              const s = layout.find((n) => n.id === e.source)
              const t = layout.find((n) => n.id === e.target)
              if (!s || !t) return null
              return (
                <line
                  key={`${e.source}-${e.target}-${i}`}
                  x1={s.x}
                  y1={s.y}
                  x2={t.x}
                  y2={t.y}
                  stroke="var(--border)"
                  strokeWidth={1.5}
                />
              )
            })}
            {layout.map((n) => (
              <g key={n.id} onClick={() => setSelected(n)} style={{ cursor: 'pointer' }}>
                <circle cx={n.x} cy={n.y} r={14} fill={confidenceColor(n.confidence)} opacity={0.9} />
                <text x={n.x} y={n.y + 28} textAnchor="middle" fill="var(--muted)" fontSize={10}>
                  {(n.label || n.id).slice(0, 18)}
                </text>
              </g>
            ))}
          </svg>
          <p className="muted" style={{ fontSize: '0.85rem' }}>
            {filtered.nodes.length} nodes · {filtered.edges.length} edges
            {selected?.convergence_score ? ` · convergence ${selected.convergence_score}` : ''}
          </p>
        </div>

        <div className="card">
          <h2 style={{ marginTop: 0 }}>Evidence</h2>
          {!selected ? (
            <p className="muted">Select a construct/node.</p>
          ) : (
            <>
              <p>
                <strong>{selected.label}</strong>
              </p>
              <p className="muted">
                {selected.type} · {selected.module_id} · {selected.confidence || 'n/a'}
              </p>
              {(selected.evidence_quote_ids || []).length === 0 ? (
                <p className="muted">No cited quotes on this node.</p>
              ) : (
                <ul>
                  {(selected.evidence_quote_ids || []).map((qid) => (
                    <li key={qid}>
                      <code>{qid}</code>
                    </li>
                  ))}
                </ul>
              )}
            </>
          )}
        </div>
      </div>
    </section>
  )
}
