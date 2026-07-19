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
          <p className="muted">Select a case to view timeline, notes, and transcripts.</p>
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
                  {t.workflow_run_count > 0 && (
                    <>
                      {' '}
                      · <span className="muted">prior reports via Analyze/Report on transcript</span>
                    </>
                  )}
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
            <p className="muted">
              Pin findings from a report using feedback label <code>pinned</code>. Case export
              placeholder: use report Export JSON per run.
            </p>
          </>
        )}
      </div>
    </section>
  )
}
