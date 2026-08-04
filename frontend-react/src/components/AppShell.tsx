import { useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { NavLink, Navigate, Outlet, useNavigate } from 'react-router-dom'
import { ApiError, api } from '../api/client'

const requireSession =
  import.meta.env.VITE_SESSION_AUTH_REQUIRED === 'true' ||
  import.meta.env.PROD

function readHandoffToken(): string | null {
  try {
    return new URLSearchParams(window.location.search).get('handoff')
  } catch {
    return null
  }
}

export function AppShell() {
  const navigate = useNavigate()
  const [handoffPending, setHandoffPending] = useState(() => Boolean(readHandoffToken()))
  const [handoffError, setHandoffError] = useState<string | null>(null)
  const me = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: () => api.me(),
    retry: false,
  })

  useEffect(() => {
    const token = readHandoffToken()
    if (!token) return
    let cancelled = false
    ;(async () => {
      try {
        await api.powerHandoff(token)
        if (cancelled) return
        const url = new URL(window.location.href)
        url.searchParams.delete('handoff')
        window.history.replaceState({}, '', `${url.pathname}${url.search}${url.hash}`)
        setHandoffPending(false)
        await me.refetch()
      } catch (err) {
        if (cancelled) return
        setHandoffError(err instanceof Error ? err.message : 'Sign-in handoff failed')
        setHandoffPending(false)
      }
    })()
    return () => {
      cancelled = true
    }
    // Intentionally run once on mount for ?handoff= from wake redirect.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function onLogout() {
    try {
      await api.logout()
    } finally {
      me.refetch()
      navigate('/login')
    }
  }

  const signedIn = me.data && !(me.error instanceof ApiError && me.error.status === 401)
  const isAdmin = Boolean(signedIn && me.data?.is_admin)

  if (handoffPending) {
    return (
      <div className="app-shell">
        <p className="muted" style={{ padding: '2rem' }}>
          Completing sign-in…
        </p>
      </div>
    )
  }

  if (handoffError) {
    return <Navigate to="/login" replace />
  }

  if (requireSession && me.isFetched && !signedIn) {
    return <Navigate to="/login" replace />
  }

  return (
    <div className="app-shell">
      <header className="nav">
        <strong style={{ fontSize: '1.15rem', letterSpacing: '0.02em' }}>RRE</strong>
        <NavLink to="/" end>
          Dashboard
        </NavLink>
        <NavLink to="/ingest">Ingest</NavLink>
        <NavLink to="/cases">Cases</NavLink>
        <NavLink to="/modules">Modules</NavLink>
        {isAdmin && <NavLink to="/evaluations">Evals</NavLink>}
        <NavLink to="/settings">Settings</NavLink>
        <span className="muted" style={{ marginLeft: 'auto', fontSize: '0.85rem' }}>
          {signedIn
            ? `${me.data?.email}${isAdmin ? ' (admin)' : ''}`
            : 'Not signed in'}
        </span>
        {signedIn ? (
          <button type="button" onClick={onLogout} style={{ marginLeft: '0.75rem' }}>
            Log out
          </button>
        ) : (
          <NavLink to="/login" style={{ marginLeft: '0.75rem' }}>
            Sign in
          </NavLink>
        )}
      </header>
      <Outlet />
    </div>
  )
}
