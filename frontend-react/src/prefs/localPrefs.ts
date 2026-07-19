const SAVED_KEY = 'rre.savedReports'
const REVIEW_KEY = 'rre.findingReview'
const PRIVACY_KEY = 'rre.privacy'

export type ReviewStatus = 'unreviewed' | 'accepted' | 'rejected' | 'needs_followup'

export function listSavedReports(): string[] {
  try {
    return JSON.parse(localStorage.getItem(SAVED_KEY) || '[]') as string[]
  } catch {
    return []
  }
}

export function toggleSavedReport(runId: string): string[] {
  const cur = new Set(listSavedReports())
  if (cur.has(runId)) cur.delete(runId)
  else cur.add(runId)
  const next = [...cur]
  localStorage.setItem(SAVED_KEY, JSON.stringify(next))
  return next
}

export function getReviewMap(runId: string): Record<string, ReviewStatus> {
  try {
    const all = JSON.parse(localStorage.getItem(REVIEW_KEY) || '{}') as Record<
      string,
      Record<string, ReviewStatus>
    >
    return all[runId] || {}
  } catch {
    return {}
  }
}

export function setReviewStatus(runId: string, findingKey: string, status: ReviewStatus) {
  const all = JSON.parse(localStorage.getItem(REVIEW_KEY) || '{}') as Record<
    string,
    Record<string, ReviewStatus>
  >
  all[runId] = { ...(all[runId] || {}), [findingKey]: status }
  localStorage.setItem(REVIEW_KEY, JSON.stringify(all))
}

export type PrivacyPrefs = {
  redactExports: boolean
  showPrivacyBanner: boolean
}

export function getPrivacyPrefs(): PrivacyPrefs {
  try {
    return {
      redactExports: true,
      showPrivacyBanner: true,
      ...(JSON.parse(localStorage.getItem(PRIVACY_KEY) || '{}') as Partial<PrivacyPrefs>),
    }
  } catch {
    return { redactExports: true, showPrivacyBanner: true }
  }
}

export function setPrivacyPrefs(prefs: PrivacyPrefs) {
  localStorage.setItem(PRIVACY_KEY, JSON.stringify(prefs))
}
