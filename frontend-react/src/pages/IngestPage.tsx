import { useMutation } from '@tanstack/react-query'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import { ingestSchema } from '../api/schemas'

export function IngestPage() {
  const [text, setText] = useState(
    'Person A: I felt unheard when plans changed without checking in.\nPerson B: I thought it was a small adjustment. I hear you now.',
  )
  const [title, setTitle] = useState('Session notes')
  const [formError, setFormError] = useState<string | null>(null)
  const navigate = useNavigate()
  const create = useMutation({
    mutationFn: (payload: { text: string; title: string }) =>
      api.createTranscript(payload.text, payload.title),
    onSuccess: (data) => navigate(`/transcripts/${data.transcript.id}`),
  })

  return (
    <section className="card">
      <h1 style={{ marginTop: 0 }}>Ingest transcript</h1>
      <p className="muted">Paste labeled turns, then prepare speakers/exclusions before analysis.</p>
      <div className="field">
        <label htmlFor="title">Title</label>
        <input id="title" value={title} onChange={(e) => setTitle(e.target.value)} />
      </div>
      <div className="field">
        <label htmlFor="body">Transcript</label>
        <textarea id="body" rows={12} value={text} onChange={(e) => setText(e.target.value)} />
      </div>
      {(formError || create.isError) && (
        <p style={{ color: 'var(--danger)' }}>
          {formError || (create.error as Error).message}
        </p>
      )}
      <button
        className="btn btn-primary"
        type="button"
        disabled={create.isPending}
        onClick={() => {
          const parsed = ingestSchema.safeParse({ title, text })
          if (!parsed.success) {
            setFormError(parsed.error.issues[0]?.message || 'Invalid input')
            return
          }
          setFormError(null)
          create.mutate(parsed.data)
        }}
      >
        {create.isPending ? 'Creating…' : 'Continue to prepare'}
      </button>
      <p className="muted" style={{ marginTop: '1rem' }}>
        Or open <Link to="/cases">Cases</Link> for multi-session work.
      </p>
    </section>
  )
}
