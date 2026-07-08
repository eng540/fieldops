import { test, expect } from '@playwright/test'

test.describe('Sprint-0 Smoke Tests', () => {
  test('homepage loads', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveTitle(/FieldOps/)
    await expect(page.locator('h1')).toContainText('FieldOps')
  })

  test('health endpoint is accessible', async ({ page }) => {
    // This test will be enabled when API is running
    test.skip(true, 'Pending API startup')
  })
})
