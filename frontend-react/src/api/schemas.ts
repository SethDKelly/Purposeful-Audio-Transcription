import { z } from 'zod'

export const ingestSchema = z.object({
  title: z.string().trim().min(1, 'Title is required').max(200),
  text: z.string().trim().min(8, 'Transcript is too short'),
})

export type IngestInput = z.infer<typeof ingestSchema>
