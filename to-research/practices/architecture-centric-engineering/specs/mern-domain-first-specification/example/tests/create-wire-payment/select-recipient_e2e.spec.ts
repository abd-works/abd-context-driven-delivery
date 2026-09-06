import { test, expect } from '@playwright/test';
import { SelectRecipientE2eHelper } from './helpers/select-recipient.e2e';

// ============================================================================
// STORY: View Active Recipients for Wire Payment
// Sub-Epic: Select Recipient | Epic: Create Wire Payment
// E2E emphasis: full browser workflow — wire payment page → recipient list
// ============================================================================

test.describe('View Active Recipients for Wire Payment', () => {
  let helper: SelectRecipientE2eHelper;

  test.beforeEach(async ({ page }) => {
    helper = new SelectRecipientE2eHelper(page);
  });

  test('user navigates to wire payment recipient selection', async ({ page }) => {
    await helper.givenActiveRecipientsSeeded();
    await helper.whenUserOpensWirePaymentPage();
    await helper.thenRecipientSelectionPageVisible();
    await expect(page.getByRole('heading', { name: 'Select Recipient for Wire Payment' })).toBeVisible();
  });
});
