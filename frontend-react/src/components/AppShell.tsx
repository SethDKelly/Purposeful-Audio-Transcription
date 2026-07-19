import { NavLink, Outlet } from 'react-router-dom'

export function AppShell() {
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
        <NavLink to="/settings">Settings</NavLink>
        <span className="muted" style={{ marginLeft: 'auto', fontSize: '0.85rem' }}>
          Primary UI · /api/v1
        </span>
      </header>
      <Outlet />
    </div>
  )
}
