import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from './components/AppShell'
import { AnalyzePage } from './pages/AnalyzePage'
import { CasesPage } from './pages/CasesPage'
import { IngestPage } from './pages/IngestPage'
import { PreparePage } from './pages/PreparePage'
import { ReportPage } from './pages/ReportPage'

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
            <Route index element={<IngestPage />} />
            <Route path="transcripts/:transcriptId" element={<PreparePage />} />
            <Route path="transcripts/:transcriptId/analyze" element={<AnalyzePage />} />
            <Route path="runs/:runId/report" element={<ReportPage />} />
            <Route path="cases" element={<CasesPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
