import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import { IngestPage } from '../pages/IngestPage'

vi.mock('../api/client', () => ({
  api: {
    createTranscript: vi.fn(),
  },
}))

describe('IngestPage', () => {
  it('renders paste form', () => {
    const client = new QueryClient()
    render(
      <QueryClientProvider client={client}>
        <MemoryRouter>
          <IngestPage />
        </MemoryRouter>
      </QueryClientProvider>,
    )
    expect(screen.getByText(/Ingest transcript/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Continue to prepare/i })).toBeInTheDocument()
  })
})
