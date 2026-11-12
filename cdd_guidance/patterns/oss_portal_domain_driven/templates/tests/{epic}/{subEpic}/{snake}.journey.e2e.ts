// The representative citizen journey the pack verifies after every release (OP-05 step 6): portal, BFF, Apigee,
// service, and database, with nothing stubbed or intercepted.
import { test, expect } from '@playwright/test';

test('{{Screen}}: a citizen applies and is told it is received', async ({ page }) => {
  await page.goto('/{{serviceBasePath}}/{screen}');
  await page.getByRole('button', { name: 'Submit' }).click();
  await expect(page).toHaveURL(/submitted/);
});
