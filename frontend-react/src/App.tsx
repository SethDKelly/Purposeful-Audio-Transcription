import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from './components/AppShell'
import { AnalyzePage } from './pages/AnalyzePage'
import { CasesPage } from './pages/CasesPage'
import { DashboardPage } from './pages/DashboardPage'
import { GraphPage } from './pages/GraphPage'
import { IngestPage } from './pages/IngestPage'
import { ModulesPage } from './pages/ModulesPage'
import { PreparePage } from './pages/PreparePage'
import { ReportPage } from './pages/ReportPage'
import { SettingsPage } from './pages/SettingsPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, refetchOnWindowFocus: false },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<AppShell />}>
            <Route index element={<DashboardPage />} />
            <Route path="ingest" element={<IngestPage />} />
            <Route path="transcripts/:transcriptId" element={<PreparePage />} />
            <Route path="transcripts/:transcriptId/analyze" element={<AnalyzePage />} />
            <Route path="runs/:runId/report" element={<ReportPage />} />
            <Route path="runs/:runId/graph" element={<GraphPage />} />
            <Route path="graph" element={<GraphPage />} />
            <Route path="cases" element={<CasesPage />} />
            <Route path="modules" element={<ModulesPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
