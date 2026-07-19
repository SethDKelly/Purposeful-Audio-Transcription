import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api, type Turn } from '../api/client'

export function PreparePage() {
  const { transcriptId = '' } = useParams()
  const navigate = useNavigate()
  const qc = useQueryClient()
  const bundleQ = useQuery({
    queryKey: ['transcript', transcriptId],
    queryFn: () => api.getTranscript(transcriptId),
    enabled: Boolean(transcriptId),
  })
  const [dirty, setDirty] = useState(false)
  const [turns, setTurns] = useState<Turn[]>([])
  const [speakers, setSpeakers] = useState(bundleQ.data?.speakers || [])

  useEffect(() => {
    if (bundleQ.data) {
      setTurns(bundleQ.data.turns)
      setSpeakers(bundleQ.data.speakers)
      setDirty(false)
    }
  }, [bundleQ.data])

  useEffect(() => {
    const onBeforeUnload = (e: BeforeUnloadEvent) => {
      if (!dirty) return
      e.preventDefault()
      e.returnValue = ''
    }
    window.addEventListener('beforeunload', onBeforeUnload)
    return () => window.removeEventListener('beforeunload', onBeforeUnload)
  }, [dirty])

  const save = useMutation({
    mutationFn: async () => {
      await api.updateSpeakers(transcriptId, speakers)
      await api.updateTurns(
        transcriptId,
        turns.map((t) => ({
          id: t.id,
          text: t.text,
          excluded_from_analysis: t.excluded_from_analysis,
          speaker_id: t.speaker_id,
        })),
      )
      await api.rebuildEvidence(transcriptId)
    },
    onSuccess: async () => {
      setDirty(false)
      await qc.invalidateQueries({ queryKey: ['transcript', transcriptId] })
    },
  })

  const ready = useMutation({
    mutationFn: async () => {
      if (dirty) await save.mutateAsync()
      return api.markReady(transcriptId, false)
    },
    onSuccess: () => navigate(`/transcripts/${transcriptId}/analyze`),
  })

  const qualityWarnings = useMemo(() => {
    const warnings: string[] = []
    if (turns.length < 2) warnings.push('Very short transcript — analysis may be thin.')
    if (turns.every((t) => t.excluded_from_analysis)) warnings.push('All turns are excluded.')
    if (speakers.some((s) => !(s.display_name || s.label))) {
      warnings.push('Some speakers lack labels.')
    }
    const quoteCount = bundleQ.data?.evidence_quotes?.length || 0
    if (quoteCount > 80) {
      warnings.push(
        `Long transcript (${quoteCount} evidence quotes) — chunked analysis is not fully supported yet; see docs/architecture/long_transcript_chunking.md.`,
      )
    }
    return warnings
  }, [turns, speakers, bundleQ.data?.evidence_quotes?.length])

  if (bundleQ.isLoading) return <p className="muted">Loading transcript…</p>
  if (bundleQ.isError) return <p style={{ color: 'var(--danger)' }}>{(bundleQ.error as Error).message}</p>

  return (
    <section>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap' }}>
        <div>
          <h1 style={{ marginBottom: 0 }}>Prepare transcript</h1>
          <p className="muted">{bundleQ.data?.transcript.title || transcriptId}</p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button className="btn" type="button" disabled={!dirty || save.isPending} onClick={() => save.mutate()}>
            Save + rebuild evidence
          </button>
          <button className="btn btn-primary" type="button" disabled={ready.isPending} onClick={() => ready.mutate()}>
            Mark ready & analyze
          </button>
        </div>
      </div>

      {qualityWarnings.map((w) => (
        <p key={w} style={{ color: 'var(--warn)' }}>
          {w}
        </p>
      ))}
      {dirty && <p className="muted">Unsaved changes</p>}

      <div className="card" style={{ marginTop: '1rem' }}>
        <h3>Speakers</h3>
        {speakers.map((s, idx) => (
          <div key={s.id} className="field">
            <label htmlFor={`sp-${s.id}`}>{s.label || s.id}</label>
            <input
              id={`sp-${s.id}`}
              value={s.display_name || ''}
              onChange={(e) => {
                const next = [...speakers]
                next[idx] = { ...s, display_name: e.target.value }
                setSpeakers(next)
                setDirty(true)
              }}
            />
          </div>
        ))}
      </div>

      <div className="card" style={{ marginTop: '1rem' }}>
        <h3>Turns</h3>
        <p className="muted">Edit text, exclude from analysis, or remove (exclude).</p>
        {turns.map((turn, idx) => (
          <div
            key={turn.id}
            style={{
              borderTop: '1px solid var(--border)',
              padding: '0.75rem 0',
              opacity: turn.excluded_from_analysis ? 0.55 : 1,
            }}
          >
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.35rem', flexWrap: 'wrap' }}>
              <select
                value={turn.speaker_id || ''}
                onChange={(e) => {
                  const next = [...turns]
                  next[idx] = { ...turn, speaker_id: e.target.value }
                  setTurns(next)
                  setDirty(true)
                }}
              >
                {speakers.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.display_name || s.label || s.id}
                  </option>
                ))}
              </select>
              <label>
                <input
                  type="checkbox"
                  checked={Boolean(turn.excluded_from_analysis)}
                  onChange={(e) => {
                    const next = [...turns]
                    next[idx] = { ...turn, excluded_from_analysis: e.target.checked }
                    setTurns(next)
                    setDirty(true)
                  }}
                />{' '}
                Exclude
              </label>
              <button
                type="button"
                className="btn"
                onClick={() => {
                  if (idx === 0) return
                  const next = [...turns]
                  const merged = {
                    ...next[idx - 1],
                    text: `${next[idx - 1].text || ''} ${turn.text || ''}`.trim(),
                  }
                  next.splice(idx - 1, 2, merged)
                  // mark removed turn excluded if API cannot delete
                  setTurns(next)
                  setDirty(true)
                }}
              >
                Merge up
              </button>
            </div>
            <textarea
              rows={2}
              value={turn.text || ''}
              onChange={(e) => {
                const next = [...turns]
                next[idx] = { ...turn, text: e.target.value }
                setTurns(next)
                setDirty(true)
              }}
              style={{ width: '100%' }}
            />
          </div>
        ))}
      </div>

      <p style={{ marginTop: '1rem' }}>
        <Link to="/">Back to ingest</Link>
      </p>
    </section>
  )
}
