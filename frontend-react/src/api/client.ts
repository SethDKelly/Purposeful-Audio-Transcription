export type ApiErrorBody = {
  detail?: string
  message?: string
  error_code?: string
  request_id?: string
  details?: unknown
}

export class ApiError extends Error {
  status: number
  body: ApiErrorBody

  constructor(status: number, body: ApiErrorBody) {
    super(body.message || body.detail || `API error ${status}`)
    this.status = status
    this.body = body
  }
}

const API_BASE = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, '') || ''

function headers(json = true): HeadersInit {
  const h: Record<string, string> = {}
  if (json) h['Content-Type'] = 'application/json'
  const key = import.meta.env.VITE_API_KEY as string | undefined
  if (key) h['X-API-Key'] = key
  return h
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { ...headers(!(init?.body instanceof FormData)), ...init?.headers },
  })
  if (!res.ok) {
    let body: ApiErrorBody = {}
    try {
      body = (await res.json()) as ApiErrorBody
    } catch {
      body = { message: res.statusText }
    }
    throw new ApiError(res.status, body)
  }
  if (res.status === 204) return undefined as T
  return (await res.json()) as T
}

export const api = {
  health: () => request<{ status: string }>('/api/live'),
  createTranscript: (raw_text: string, title?: string) =>
    request<{ transcript: { id: string; title?: string }; turns: Turn[]; speakers: Speaker[]; evidence_quotes: EvidenceQuote[] }>(
      '/api/v1/transcripts',
      { method: 'POST', body: JSON.stringify({ raw_text, source_type: 'paste', title }) },
    ),
  getTranscript: (id: string) =>
    request<TranscriptBundle>(`/api/v1/transcripts/${id}`),
  updateTurns: (id: string, turns: Partial<Turn>[]) =>
    request<TranscriptBundle>(`/api/v1/transcripts/${id}/turns`, {
      method: 'PATCH',
      body: JSON.stringify({ turns }),
    }),
  updateSpeakers: (id: string, speakers: Speaker[]) =>
    request<TranscriptBundle>(`/api/v1/transcripts/${id}/speakers`, {
      method: 'PATCH',
      body: JSON.stringify({ speakers }),
    }),
  markReady: (id: string, skip_review = false) =>
    request<TranscriptBundle>(`/api/v1/transcripts/${id}/ready`, {
      method: 'POST',
      body: JSON.stringify({ skip_review }),
    }),
  rebuildEvidence: (id: string) =>
    request<TranscriptBundle>(`/api/v1/transcripts/${id}/evidence/rebuild`, { method: 'POST' }),
  listWorkflows: () => request<{ workflows: WorkflowSummary[] }>('/api/v1/workflows'),
  startWorkflow: (workflow_id: string, transcript_id: string, background = true) =>
    request<WorkflowRun>('/api/v1/workflow-runs', {
      method: 'POST',
      body: JSON.stringify({ workflow_id, transcript_id, background }),
    }),
  getWorkflowStatus: (runId: string) =>
    request<WorkflowStatus>(`/api/v1/workflow-runs/${runId}/status`),
  getWorkflowRun: (runId: string) => request<WorkflowRun>(`/api/v1/workflow-runs/${runId}`),
  getReport: (runId: string) => request<SynthesisReport>(`/api/v1/reports/${runId}`),
  getReportFindings: (runId: string) =>
    request<{ findings: Finding[]; report_id: string; workflow_run_id: string }>(
      `/api/v1/reports/${runId}/findings`,
    ),
  exportReport: (workflow_run_id: string, format = 'json') =>
    request<{ download_hint: string; format: string }>('/api/v1/exports', {
      method: 'POST',
      body: JSON.stringify({ workflow_run_id, format }),
    }),
  submitFeedback: (workflow_run_id: string, finding_key: string, rating: string, note?: string) =>
    request(`/api/v1/findings/${encodeURIComponent(finding_key)}/feedback?workflow_run_id=${workflow_run_id}`, {
      method: 'POST',
      body: JSON.stringify({ rating, note }),
    }),
  listCases: () => request<{ cases: CaseSummary[] }>('/api/v1/cases'),
  createCase: (title: string, notes?: string) =>
    request<CaseSummary>('/api/v1/cases', {
      method: 'POST',
      body: JSON.stringify({ title, notes }),
    }),
  getCase: (id: string) => request<CaseDetail>(`/api/v1/cases/${id}`),
  updateCase: (id: string, patch: { title?: string; notes?: string }) =>
    request<CaseSummary>(`/api/v1/cases/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(patch),
    }),
  assignTranscriptCase: (transcript_id: string, case_id: string, session_label?: string) =>
    request(`/api/v1/transcripts/${transcript_id}/case`, {
      method: 'PATCH',
      body: JSON.stringify({ case_id, session_label }),
    }),
  getCaseTimeline: (id: string) =>
    request<{ events: CaseTimelineEvent[]; case_id: string }>(`/api/v1/cases/${id}/timeline`),
}

export type Speaker = {
  id: string
  label?: string
  display_name?: string | null
}

export type Turn = {
  id: string
  speaker_id?: string
  text?: string
  excluded_from_analysis?: boolean
  sequence?: number
}

export type EvidenceQuote = {
  quote_id: string
  text: string
  turn_id?: string
  speaker_label?: string
}

export type TranscriptBundle = {
  transcript: { id: string; title?: string | null; analysis_ready?: boolean }
  turns: Turn[]
  speakers: Speaker[]
  evidence_quotes: EvidenceQuote[]
}

export type WorkflowSummary = {
  id: string
  name: string
  description?: string
  module_sequence?: string[]
}

export type WorkflowRun = {
  id: string
  workflow_id: string
  transcript_id: string
  status: string
  error_log?: string | null
}

export type WorkflowStatus = {
  schema_version: string
  id: string
  status: string
  cancel_requested: boolean
  attempt_count: number
  error_log?: string | null
}

export type Finding = {
  id: string
  module_run_id?: string
  type?: string
  title: string
  summary: string
  confidence: string
  evidence_quote_ids?: string[]
  alternative_explanations?: string[]
  limitations?: string[]
}

export type SynthesisReport = {
  id: string
  workflow_run_id: string
  executive_summary: string
  high_confidence_findings: Finding[]
  moderate_confidence_findings: Finding[]
  exploratory_hypotheses: Finding[]
  findings?: Finding[]
  interventions?: string[]
  limitations?: string[]
  safety_flags?: string[]
}

export type CaseSummary = {
  id: string
  title: string
  notes?: string | null
  created_at: string
}

export type CaseDetail = {
  case: CaseSummary
  transcripts: Array<{
    id: string
    title?: string | null
    session_label?: string | null
    analysis_ready: boolean
    workflow_run_count: number
  }>
}

export type CaseTimelineEvent = {
  transcript_id: string
  title?: string | null
  session_label?: string | null
  created_at: string
  analysis_ready: boolean
  workflow_run_count: number
}
