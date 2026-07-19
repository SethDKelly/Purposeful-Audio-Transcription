import { expect, test } from '@playwright/test'

test('home ingest smoke', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: /Ingest transcript/i })).toBeVisible()
  await expect(page.getByRole('button', { name: /Continue to prepare/i })).toBeVisible()
})
