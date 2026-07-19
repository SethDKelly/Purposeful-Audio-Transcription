import { expect, test } from '@playwright/test'

test('dashboard smoke', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: /Dashboard/i })).toBeVisible()
  await expect(page.getByRole('link', { name: /Ingest transcript/i })).toBeVisible()
})

test('ingest smoke', async ({ page }) => {
  await page.goto('/ingest')
  await expect(page.getByRole('heading', { name: /Ingest transcript/i })).toBeVisible()
  await expect(page.getByRole('button', { name: /Continue to prepare/i })).toBeVisible()
})
