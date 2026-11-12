import { expect, test } from './story-ui'

test.describe('Place Order', () => {
  test('Place an order on the page', async ({ page }) => {
    await page.getByRole('button', { name: 'Place order' }).click()
    await expect(page.getByText('Confirmed')).toBeVisible()
  })
})
