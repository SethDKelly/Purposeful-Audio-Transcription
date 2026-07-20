import { useQuery } from '@tanstack/react-query'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { ApiError, api } from '../api/client'

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
        <NavLink to="/evaluations">Evals</NavLink>
        <NavLink to="/settings">Settings</NavLink>
        <span className="muted" style={{ marginLeft: 'auto', fontSize: '0.85rem' }}>
          {signedIn ? me.data?.email : 'Not signed in'}
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
