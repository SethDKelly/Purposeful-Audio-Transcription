import { FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api/client'

export function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [step, setStep] = useState<'email' | 'code'>('email')
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function onRequestCode(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    setMessage(null)
    try {
      await api.requestLoginCode(email)
      setStep('code')
      setMessage('If the email is valid, a login code was sent (check server logs in local/dev).')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not request code')
    } finally {
      setBusy(false)
    }
  }

  async function onVerify(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await api.verifyLoginCode(email, code)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Invalid code')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="login-page">
      <section className="card" style={{ maxWidth: 420, margin: '4rem auto' }}>
        <h1 style={{ marginTop: 0 }}>Sign in</h1>
        <p className="muted">
          Passwordless email login. Enterprise SSO (Google/Okta/Cognito) is future work.
        </p>
        {step === 'email' ? (
          <form onSubmit={onRequestCode}>
            <label style={{ display: 'block', marginTop: '1rem' }}>
              Email
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={{ display: 'block', width: '100%', marginTop: 4 }}
              />
            </label>
            <button type="submit" disabled={busy} style={{ marginTop: '1rem' }}>
              Send code
            </button>
          </form>
        ) : (
          <form onSubmit={onVerify}>
            <p className="muted">Code sent to {email}</p>
            <label style={{ display: 'block', marginTop: '1rem' }}>
              One-time code
              <input
                type="text"
                inputMode="numeric"
                required
                value={code}
                onChange={(e) => setCode(e.target.value)}
                style={{ display: 'block', width: '100%', marginTop: 4 }}
              />
            </label>
            <button type="submit" disabled={busy} style={{ marginTop: '1rem' }}>
              Verify & continue
            </button>
            <button
              type="button"
              className="muted"
              style={{ marginLeft: '0.75rem' }}
              onClick={() => {
                setStep('email')
                setCode('')
              }}
            >
              Change email
            </button>
          </form>
        )}
        {message && <p style={{ color: 'var(--ok, #2a7)', marginTop: '1rem' }}>{message}</p>}
        {error && <p style={{ color: 'var(--warn)', marginTop: '1rem' }}>{error}</p>}
        <p className="muted" style={{ marginTop: '1.5rem', fontSize: '0.85rem' }}>
          Internal/admin tools may still use a shared API key. Product users should not.
        </p>
        <p>
          <Link to="/">Continue without signing in</Link> (dev only when session auth is off)
        </p>
      </section>
    </div>
  )
}
