import { NavLink, Outlet } from 'react-router-dom'

export function AppShell() {
  return (
    <div className="app-shell">
      <header className="nav">
        <strong style={{ fontSize: '1.15rem', letterSpacing: '0.02em' }}>RRE</strong>
        <NavLink to="/" end>
          Ingest
        </NavLink>
        <NavLink to="/cases">Cases</NavLink>
        <span className="muted" style={{ marginLeft: 'auto', fontSize: '0.85rem' }}>
          React MVP · API client only
        </span>
      </header>
      <Outlet />
    </div>
  )
}
