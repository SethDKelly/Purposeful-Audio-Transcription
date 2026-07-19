import { useMutation, useQuery } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client'
import { EvidencePanel } from '../components/EvidencePanel'
import { FindingCard } from '../components/FindingCard'
import {
  getReviewMap,
  listSavedReports,
  setReviewStatus,
  toggleSavedReport,
} from '../lib/localPrefs'

export function ReportPage() {
  const { runId = '' } = useParams()
  const [tab, setTab] = useState<'findings' | 'package'>('findings')
  const [confidence, setConfidence] = useState<'all' | 'high' | 'moderate' | 'exploratory'>('all')
  const [typeFilter, setTypeFilter] = useState('')
  const [moduleFilter, setModuleFilter] = useState('')
  const [activeQuote, setActiveQuote] = useState<string | null>(null)
  const [hideUnevidenced, setHideUnevidenced] = useState(false)
  const [reviewOnly, setReviewOnly] = useState(false)
  const [reviews, setReviews] = useState(() => getReviewMap(runId))
  const [saved, setSaved] = useState(() => listSavedReports().includes(runId))

  const runQ = useQuery({ queryKey: ['run', runId], queryFn: () => api.getWorkflowRun(runId) })
  const reportQ = useQuery({ queryKey: ['report', runId], queryFn: () => api.getReport(runId) })
  const structuredQ = useQuery({
    queryKey: ['structured', runId],
    queryFn: () => api.getStructuredGraph(runId),
    enabled: tab === 'package',
  })
  const transcriptQ = useQuery({
    queryKey: ['transcript', runQ.data?.transcript_id],
    queryFn: () => api.getTranscript(runQ.data!.transcript_id),
    enabled: Boolean(runQ.data?.transcript_id),
  })

  const feedback = useMutation({
    mutationFn: ({ key, rating }: { key: string; rating: string }) =>
      api.submitFeedback(runId, key, rating),
  })

  const exportMut = useMutation({
    mutationFn: async () => {
      await api.exportReport(runId, 'json')
      const packagePayload = {
        schema_version: '1',
        report: reportQ.data,
        structured: structuredQ.data || null,
        evidence_quotes: transcriptQ.data?.evidence_quotes || [],
      }
      const blob = new Blob([JSON.stringify(packagePayload, null, 2)], {
        type: 'application/json',
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `rre-report-package-${runId}.json`
      a.click()
      URL.revokeObjectURL(url)
    },
  })

  const findings = useMemo(() => {
    const report = reportQ.data
    if (!report) return []
    let list =
      confidence === 'high'
        ? report.high_confidence_findings
        : confidence === 'moderate'
          ? report.moderate_confidence_findings
          : confidence === 'exploratory'
            ? report.exploratory_hypotheses
            : [
                ...report.high_confidence_findings,
                ...report.moderate_confidence_findings,
                ...report.exploratory_hypotheses,
              ]
    if (typeFilter.trim()) {
      const needle = typeFilter.trim().toLowerCase()
      list = list.filter((f) => (f.type || '').toLowerCase().includes(needle))
    }
    if (moduleFilter.trim()) {
      const needle = moduleFilter.trim().toLowerCase()
      list = list.filter((f) => (f.module_run_id || '').toLowerCase().includes(needle))
    }
    return list
  }, [reportQ.data, confidence, typeFilter, moduleFilter])

  const visible = findings.filter((f) => {
    if (hideUnevidenced && !(f.evidence_quote_ids || []).length) return false
    const key = `${f.module_run_id || 'synth'}:${f.id}`
    if (reviewOnly && reviews[key] && reviews[key] !== 'unreviewed') return false
    return true
  })

  if (reportQ.isLoading || runQ.isLoading) return <p className="muted">Loading report…</p>
  if (reportQ.isError) return <p style={{ color: 'var(--danger)' }}>{(reportQ.error as Error).message}</p>

  return (
    <section>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap' }}>
        <div>
          <h1 style={{ marginBottom: 0 }}>Report</h1>
          <p className="muted">Run {runId}</p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <button
            className="btn"
            type="button"
            onClick={() => {
              toggleSavedReport(runId)
              setSaved(listSavedReports().includes(runId))
            }}
          >
            {saved ? 'Unsave report' : 'Save report'}
          </button>
          <Link className="btn" to={`/runs/${runId}/graph`}>
            Graph
          </Link>
          <button className="btn btn-primary" type="button" onClick={() => exportMut.mutate()}>
            Export package
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '0.5rem', margin: '1rem 0' }}>
        <button
          className={`btn ${tab === 'findings' ? 'btn-primary' : ''}`}
          type="button"
          onClick={() => setTab('findings')}
        >
          Findings review
        </button>
        <button
          className={`btn ${tab === 'package' ? 'btn-primary' : ''}`}
          type="button"
          onClick={() => setTab('package')}
        >
          Report package
        </button>
      </div>

      {tab === 'package' ? (
        <div className="card">
          <h2 style={{ marginTop: 0 }}>Package viewer</h2>
          <p>{reportQ.data?.executive_summary}</p>
          <p className="muted">
            Structured inventory: findings {structuredQ.data?.counts.findings ?? '…'} · constructs{' '}
            {structuredQ.data?.counts.constructs ?? '…'} · relationships{' '}
            {structuredQ.data?.counts.relationships ?? '…'}
          </p>
          {(reportQ.data?.interventions || []).length > 0 && (
            <>
              <h3>Interventions</h3>
              <ul>
                {reportQ.data?.interventions?.map((x) => (
                  <li key={x}>{x}</li>
                ))}
              </ul>
            </>
          )}
          {(reportQ.data?.limitations || []).length > 0 && (
            <>
              <h3>Limitations</h3>
              <ul>
                {reportQ.data?.limitations?.map((x) => (
                  <li key={x}>{x}</li>
                ))}
              </ul>
            </>
          )}
          {(reportQ.data?.safety_flags || []).length > 0 && (
            <p style={{ color: 'var(--warn)' }}>
              Safety flags: {reportQ.data?.safety_flags?.join(', ')}
            </p>
          )}
        </div>
      ) : (
        <>
          <div className="card" style={{ marginTop: 0 }}>
            <h2 style={{ marginTop: 0 }}>Summary</h2>
            <p>{reportQ.data?.executive_summary}</p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', margin: '1rem 0', flexWrap: 'wrap' }}>
            <select
              value={confidence}
              onChange={(e) => setConfidence(e.target.value as typeof confidence)}
            >
              <option value="all">All findings</option>
              <option value="high">High</option>
              <option value="moderate">Moderate</option>
              <option value="exploratory">Exploratory</option>
            </select>
            <input
              placeholder="Filter by type…"
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
            />
            <input
              placeholder="Filter by module/source…"
              value={moduleFilter}
              onChange={(e) => setModuleFilter(e.target.value)}
            />
            <label>
              <input
                type="checkbox"
                checked={hideUnevidenced}
                onChange={(e) => setHideUnevidenced(e.target.checked)}
              />{' '}
              Hide without evidence
            </label>
            <label>
              <input
                type="checkbox"
                checked={reviewOnly}
                onChange={(e) => setReviewOnly(e.target.checked)}
              />{' '}
              Unreviewed only
            </label>
          </div>

          <div className="layout-split">
            <div style={{ display: 'grid', gap: '0.75rem' }}>
              {visible.map((finding) => {
                const findingKey = `${finding.module_run_id || 'synth'}:${finding.id}`
                return (
                  <FindingCard
                    key={finding.id}
                    finding={finding}
                    findingKey={findingKey}
                    reviewStatus={reviews[findingKey] || 'unreviewed'}
                    onSelectEvidence={setActiveQuote}
                    onFeedback={(key, rating) => feedback.mutate({ key, rating })}
                    onReview={(key, status) => {
                      setReviewStatus(runId, key, status)
                      setReviews(getReviewMap(runId))
                    }}
                  />
                )
              })}
              {visible.length === 0 && <p className="muted">No findings for this filter.</p>}
            </div>
            <EvidencePanel
              quotes={transcriptQ.data?.evidence_quotes || []}
              activeQuoteId={activeQuote}
            />
          </div>
        </>
      )}

      <p style={{ marginTop: '1rem' }}>
        <Link to="/ingest">New transcript</Link>
      </p>
    </section>
  )
}
