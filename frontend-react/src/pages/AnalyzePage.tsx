import { useMutation, useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../api/client'

const TERMINAL = new Set(['completed', 'failed', 'cancelled'])

export function AnalyzePage() {
  const { transcriptId = '' } = useParams()
  const navigate = useNavigate()
  const [runId, setRunId] = useState<string | null>(null)
  const workflowsQ = useQuery({ queryKey: ['workflows'], queryFn: api.listWorkflows })
  const [workflowId, setWorkflowId] = useState('quick_review')

  const start = useMutation({
    mutationFn: () => api.startWorkflow(workflowId, transcriptId, true),
    onSuccess: (run) => setRunId(run.id),
  })

  const statusQ = useQuery({
    queryKey: ['run-status', runId],
    queryFn: () => api.getWorkflowStatus(runId!),
    enabled: Boolean(runId),
    refetchInterval: (q) => {
      const status = q.state.data?.status
      if (status && TERMINAL.has(status)) return false
      return 2000
    },
  })

  useEffect(() => {
    if (statusQ.data?.status === 'completed' && runId) {
      navigate(`/runs/${runId}/report`)
    }
  }, [statusQ.data?.status, runId, navigate])

  return (
    <section className="card">
      <h1 style={{ marginTop: 0 }}>Run analysis</h1>
      <p className="muted">
        Transcript <code>{transcriptId}</code>
      </p>
      <div className="field">
        <label htmlFor="wf">Workflow</label>
        <select
          id="wf"
          value={workflowId}
          onChange={(e) => setWorkflowId(e.target.value)}
          disabled={Boolean(runId)}
        >
          {(workflowsQ.data?.workflows || [{ id: 'quick_review', name: 'Quick Review' }]).map((w) => (
            <option key={w.id} value={w.id}>
              {w.name}
            </option>
          ))}
        </select>
      </div>
      {!runId ? (
        <button className="btn btn-primary" type="button" disabled={start.isPending} onClick={() => start.mutate()}>
          {start.isPending ? 'Starting…' : 'Start workflow'}
        </button>
      ) : (
        <div>
          <p>
            Run <code>{runId}</code>
          </p>
          <p>
            Status: <strong>{statusQ.data?.status || 'queued'}</strong>
          </p>
          {statusQ.data?.error_log && (
            <p style={{ color: 'var(--danger)' }}>{statusQ.data.error_log}</p>
          )}
          {statusQ.data?.status === 'completed' && (
            <Link className="btn btn-primary" to={`/runs/${runId}/report`}>
              Open report
            </Link>
          )}
        </div>
      )}
      {start.isError && <p style={{ color: 'var(--danger)' }}>{(start.error as Error).message}</p>}
      <p style={{ marginTop: '1rem' }}>
        <Link to={`/transcripts/${transcriptId}`}>Back to prepare</Link>
      </p>
    </section>
  )
}
