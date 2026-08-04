import { FormEvent, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api/client'

type PowerStatus = {
  state?: string
  should_sleep?: boolean
  message?: string
}

export function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [step, setStep] = useState<'email' | 'code' | 'waking'>('email')
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [handoffToken, setHandoffToken] = useState<string | null>(null)
  const [power, setPower] = useState<PowerStatus | null>(null)

  useEffect(() => {
    let cancelled = false
    async function poll() {
      try {
        const status = (await api.powerStatus()) as PowerStatus
        if (!cancelled) setPower(status)
      } catch {
        /* asleep: Lambda may still answer; ignore transient errors */
      }
    }
    poll()
    const id = window.setInterval(poll, 5000)
    return () => {
      cancelled = true
      window.clearInterval(id)
    }
  }, [])

  useEffect(() => {
    if (step !== 'waking' || !handoffToken) return
    let cancelled = false
    async function tryEnter() {
      try {
        const status = (await api.powerStatus()) as PowerStatus
        if (cancelled) return
        setPower(status)
        // Only exchange once Dynamo power state is awake. Do not treat
        // should_sleep===false as ready — API returns that for waking/sleeping too.
        if (status.state === 'awake') {
          await api.powerHandoff(handoffToken!)
          navigate('/', { replace: true })
        }
      } catch {
        /* keep polling while stack wakes */
      }
    }
    tryEnter()
    const id = window.setInterval(tryEnter, 8000)
    return () => {
      cancelled = true
      window.clearInterval(id)
    }
  }, [step, handoffToken, navigate])

  async function onRequestCode(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    setMessage(null)
    try {
      await api.requestLoginCode(email)
      setStep('code')
      setMessage('If your email is registered, a one-time code was sent.')
    } catch (err) {
      // Fall back to Lambda power-auth path when API is asleep (503).
      try {
        await api.powerRequestCode(email)
        setStep('code')
        setMessage('If your email is registered, a one-time code was sent.')
      } catch {
        setError(err instanceof Error ? err.message : 'Could not request code')
      }
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
      return
    } catch {
      /* try power path */
    }
    try {
      const result = await api.powerVerifyCode(email, code)
      if (result.handoff_token) {
        setHandoffToken(result.handoff_token)
        if (result.status === 'awake') {
          await api.powerHandoff(result.handoff_token)
          navigate('/', { replace: true })
        } else {
          setStep('waking')
          setMessage('Signing you in and waking the environment. This can take several minutes.')
        }
      } else {
        navigate('/', { replace: true })
      }
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
          Passwordless email login with a one-time code. Your mailbox is the second factor.
        </p>
        {power?.state && (
          <p className="muted" style={{ fontSize: '0.85rem' }}>
            Environment: <strong>{power.state}</strong>
          </p>
        )}
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
        ) : step === 'code' ? (
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
        ) : (
          <div>
            <p>Waking the application…</p>
            <p className="muted">
              Cold start recreates VPC endpoints and starts the database. Typical wait: 5–15
              minutes.
            </p>
          </div>
        )}
        {message && <p style={{ color: 'var(--ok, #2a7)', marginTop: '1rem' }}>{message}</p>}
        {error && <p style={{ color: 'var(--warn)', marginTop: '1rem' }}>{error}</p>}
        <p className="muted" style={{ marginTop: '1.5rem', fontSize: '0.85rem' }}>
          Invite-only. Contact an admin if you need access.
        </p>
        {import.meta.env.DEV && (
          <p>
            <Link to="/">Continue without signing in</Link> (local dev only)
          </p>
        )}
      </section>
    </div>
  )
}
