import { useQuery } from '@tanstack/react-query'
import { NavLink, Navigate, Outlet, useNavigate } from 'react-router-dom'
import { ApiError, api } from '../api/client'

const requireSession =
  import.meta.env.VITE_SESSION_AUTH_REQUIRED === 'true' ||
  import.meta.env.PROD

export function AppShell() {
  const navigate = useNavigate()
  const me = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: () => api.me(),
    retry: false,
  })

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
