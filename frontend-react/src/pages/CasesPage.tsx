import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'

export function CasesPage() {
  const qc = useQueryClient()
  const casesQ = useQuery({ queryKey: ['cases'], queryFn: api.listCases })
  const [title, setTitle] = useState('')
  const [selected, setSelected] = useState<string | null>(null)
  const [notes, setNotes] = useState('')
  const [transcriptId, setTranscriptId] = useState('')
  const [sessionLabel, setSessionLabel] = useState('')

  const create = useMutation({
    mutationFn: () => api.createCase(title),
    onSuccess: async (c) => {
      setTitle('')
      setSelected(c.id)
      await qc.invalidateQueries({ queryKey: ['cases'] })
    },
  })

  const detailQ = useQuery({
    queryKey: ['case', selected],
    queryFn: () => api.getCase(selected!),
    enabled: Boolean(selected),
  })

  const timelineQ = useQuery({
    queryKey: ['case-timeline', selected],
    queryFn: () => api.getCaseTimeline(selected!),
    enabled: Boolean(selected),
  })

  const saveNotes = useMutation({
    mutationFn: () => api.updateCase(selected!, { notes }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['case', selected] }),
  })

  const assign = useMutation({
    mutationFn: () =>
      api.assignTranscriptCase(transcriptId.trim(), selected!, sessionLabel.trim() || undefined),
    onSuccess: async () => {
      setTranscriptId('')
      setSessionLabel('')
      await qc.invalidateQueries({ queryKey: ['case', selected] })
      await qc.invalidateQueries({ queryKey: ['case-timeline', selected] })
    },
  })

  const compare = useMutation({
    mutationFn: () => api.compareCaseTranscripts(selected!),
  })

  const longitudinal = useMutation({
    mutationFn: () => api.runLongitudinal(selected!),
  })

  const pinnedQ = useQuery({
    queryKey: ['case-pinned', selected],
    queryFn: () => api.listCasePinned(selected!),
    enabled: Boolean(selected),
  })

  return (
    <section className="layout-split">
      <div className="card">
        <h1 style={{ marginTop: 0 }}>Cases</h1>
        <div className="field">
          <label htmlFor="case-title">New case</label>
          <input id="case-title" value={title} onChange={(e) => setTitle(e.target.value)} />
        </div>
        <button
          className="btn btn-primary"
          type="button"
          disabled={!title.trim() || create.isPending}
          onClick={() => create.mutate()}
        >
          Create
        </button>
        <ul style={{ listStyle: 'none', padding: 0, marginTop: '1rem' }}>
          {(casesQ.data?.cases || []).map((c) => (
            <li key={c.id}>
              <button
                type="button"
                className="btn"
                style={{ width: '100%', textAlign: 'left', marginBottom: '0.35rem' }}
                onClick={() => {
                  setSelected(c.id)
                  setNotes(c.notes || '')
                }}
              >
                {c.title}
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div className="card">
        {!selected ? (
          <p className="muted">Select a case for timeline, longitudinal compare, and synthesis.</p>
        ) : (
          <>
            <h2 style={{ marginTop: 0 }}>{detailQ.data?.case.title || 'Case'}</h2>
            <div className="field">
              <label htmlFor="notes">Case notes</label>
              <textarea
                id="notes"
                rows={4}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
            </div>
            <button className="btn" type="button" onClick={() => saveNotes.mutate()}>
              Save notes
            </button>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.75rem' }}>
              <button
                className="btn"
                type="button"
                disabled={compare.isPending}
                onClick={() => compare.mutate()}
              >
                Compare transcripts
              </button>
              <button
                className="btn btn-primary"
                type="button"
                disabled={longitudinal.isPending}
                onClick={() => longitudinal.mutate()}
              >
                Run longitudinal synthesis
              </button>
            </div>
            {compare.isError && (
              <p style={{ color: 'var(--danger)' }}>{(compare.error as Error).message}</p>
            )}
            {longitudinal.isError && (
              <p style={{ color: 'var(--danger)' }}>{(longitudinal.error as Error).message}</p>
            )}
            {compare.data && (
              <div style={{ marginTop: '1rem' }}>
                <h3>Longitudinal compare</h3>
                <p className="muted">
                  Shared {compare.data.shared_themes?.length || 0} · New{' '}
                  {compare.data.new_themes?.length || 0} · Resolved{' '}
                  {compare.data.resolved_themes?.length || 0}
                </p>
                <ul>
                  {(compare.data.shared_themes || []).slice(0, 8).map((t, i) => {
                    const row = t as { label?: string; title?: string; transcript_ids?: string[] }
                    return (
                      <li key={i}>
                        {row.label || row.title || JSON.stringify(t).slice(0, 80)}
                        {row.transcript_ids?.length
                          ? ` · transcripts: ${row.transcript_ids.join(', ')}`
                          : ''}
                      </li>
                    )
                  })}
                </ul>
              </div>
            )}
            {longitudinal.data && (
              <div style={{ marginTop: '1rem' }}>
                <h3>Case synthesis</h3>
                <p className="muted">
                  {longitudinal.data.module_id} · {longitudinal.data.status} · id{' '}
                  {longitudinal.data.id}
                </p>
                <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.8rem' }}>
                  {JSON.stringify(longitudinal.data.parsed_output || {}, null, 2).slice(0, 4000)}
                </pre>
              </div>
            )}
            <h3>Transcripts</h3>
            <div className="field">
              <label htmlFor="assign-tid">Add transcript ID</label>
              <input
                id="assign-tid"
                value={transcriptId}
                onChange={(e) => setTranscriptId(e.target.value)}
                placeholder="transcript uuid"
              />
            </div>
            <div className="field">
              <label htmlFor="session-label">Session label</label>
              <input
                id="session-label"
                value={sessionLabel}
                onChange={(e) => setSessionLabel(e.target.value)}
                placeholder="Session 1"
              />
            </div>
            <button
              className="btn"
              type="button"
              disabled={!transcriptId.trim() || assign.isPending}
              onClick={() => assign.mutate()}
            >
              Assign to case
            </button>
            {assign.isError && (
              <p style={{ color: 'var(--danger)' }}>{(assign.error as Error).message}</p>
            )}
            <ul>
              {(detailQ.data?.transcripts || []).map((t) => (
                <li key={t.id}>
                  <Link to={`/transcripts/${t.id}`}>{t.title || t.id}</Link>
                  {t.session_label ? ` · ${t.session_label}` : ''} · runs {t.workflow_run_count}
                </li>
              ))}
            </ul>
            <h3>Timeline</h3>
            <ul>
              {(timelineQ.data?.events || []).map((e) => (
                <li key={e.transcript_id}>
                  {e.created_at}: {e.title || e.transcript_id} ({e.workflow_run_count} runs)
                </li>
              ))}
            </ul>
            <h3>Pinned findings</h3>
            <ul>
              {(pinnedQ.data?.pinned_findings || []).map((p, i) => (
                <li key={i}>
                  <code>{String(p.finding_key || p.id)}</code>
                  {p.workflow_run_id ? (
                    <>
                      {' '}
                      ·{' '}
                      <Link to={`/runs/${String(p.workflow_run_id)}/report`}>report</Link>
                    </>
                  ) : null}
                </li>
              ))}
              {!pinnedQ.data?.pinned_findings?.length && (
                <li className="muted">Pin findings from a report with feedback label pinned.</li>
              )}
            </ul>
          </>
        )}
      </div>
    </section>
  )
}
