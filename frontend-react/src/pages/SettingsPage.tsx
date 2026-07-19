import { useState } from 'react'
import { getPrivacyPrefs, setPrivacyPrefs, type PrivacyPrefs } from '../prefs/localPrefs'

export function SettingsPage() {
  const [prefs, setPrefs] = useState<PrivacyPrefs>(getPrivacyPrefs())

  return (
    <section className="card">
      <h1 style={{ marginTop: 0 }}>Settings & privacy</h1>
      <p className="muted">
        Client-side preferences for this browser. Server retention and deletion follow API/
        ops policy (see docs/developer/data_governance.md).
      </p>
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
          Auth today is shared API key (dev/UAT); multi-user RBAC is planned.
        </p>
      )}
      <h2>API key</h2>
      <p className="muted">
        Set <code>VITE_API_KEY</code> in <code>.env</code> for local builds. Never commit keys.
      </p>
    </section>
  )
}
