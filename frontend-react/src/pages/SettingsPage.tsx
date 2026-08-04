import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ApiError, api } from '../api/client'
import { getPrivacyPrefs, setPrivacyPrefs, type PrivacyPrefs } from '../prefs/localPrefs'

export function SettingsPage() {
  const [prefs, setPrefs] = useState<PrivacyPrefs>(getPrivacyPrefs())
  const me = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: () => api.me(),
    retry: false,
  })
  const signedIn = me.data && !(me.error instanceof ApiError && me.error.status === 401)

  return (
    <section className="card">
      <h1 style={{ marginTop: 0 }}>Settings & privacy</h1>
      <p className="muted">
        Client-side preferences for this browser. Server retention and deletion follow API/
        ops policy (see docs/developer/data_governance.md).
      </p>

      <h2>Account</h2>
      {signedIn ? (
        <p>
          Signed in as <strong>{me.data?.email}</strong>
          {me.data?.display_name ? ` (${me.data.display_name})` : ''}
          {me.data?.is_admin ? ' — role: admin (also standard user)' : ' — role: user'}
        </p>
      ) : (
        <p className="muted">
          Not signed in. <Link to="/login">Sign in with email</Link> for ownership-scoped
          resources. Product auth uses session cookies — not a shared browser API key.
        </p>
      )}

      <label style={{ display: 'block', marginTop: '1rem' }}>
        <input
          type="checkbox"
          checked={prefs.redactExports}
          onChange={(e) => {
            const next = { ...prefs, redactExports: e.target.checked }
            setPrefs(next)
            setPrivacyPrefs(next)
          }}
        />{' '}
        Prefer redacted exports (client reminder — server export may still apply redaction)
      </label>
      <label style={{ display: 'block', marginTop: '0.75rem' }}>
        <input
          type="checkbox"
          checked={prefs.showPrivacyBanner}
          onChange={(e) => {
            const next = { ...prefs, showPrivacyBanner: e.target.checked }
            setPrefs(next)
            setPrivacyPrefs(next)
          }}
        />{' '}
        Show privacy reminder on dashboard
      </label>
      {prefs.showPrivacyBanner && (
        <p style={{ color: 'var(--warn)', marginTop: '1rem' }}>
          Sensitive dialogue: treat cases as confidential. Delete transcripts you no longer need.
        </p>
      )}
      <h2>Developer / admin API key</h2>
      <p className="muted">
        Optional <code>VITE_API_KEY</code> is for internal/dev break-glass only. Real users
        authenticate with email OTP. Cognito / enterprise SSO is deferred.
      </p>
    </section>
  )
}
