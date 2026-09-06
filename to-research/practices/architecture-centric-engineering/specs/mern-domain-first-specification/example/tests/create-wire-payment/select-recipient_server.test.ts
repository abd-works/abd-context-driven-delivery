import { describe, it, beforeEach, afterEach } from 'vitest';
import { SelectRecipientServerHelper } from './helpers/select-recipient.server';

// ============================================================================
// STORY: View Active Recipients for Wire Payment
// Sub-Epic: Select Recipient | Epic: Create Wire Payment
// Server emphasis: Receive, filter by status, return active recipients only
// ============================================================================

describe('View Active Recipients for Wire Payment', () => {
  const suite = new (class {
    helper = new SelectRecipientServerHelper();

    async cleanup() {
      await this.helper.cleanup();
    }
  })();

  beforeEach(async () => {
    await suite.cleanup();
  });

  afterEach(async () => {
    await suite.cleanup();
  });

  it('user views list of active recipients when initiating wire payment', async () => {
    await suite.helper.givenUserLoggedIntoChannelOne();
    await suite.helper.givenEnterpriseHasRecipientsWithActiveStatus([
      { name: 'Acme Corporation', status: 'Active', bankName: 'Chase Bank', accountMasked: '****1234' },
      { name: 'Global Supplies LLC', status: 'Active', bankName: 'Bank of America', accountMasked: '****5678' },
    ]);
    await suite.helper.whenUserInitiatesCreateWirePayment();
    suite.helper.thenRecipientSelectionIncludesActiveRecipientsOnly(['Acme Corporation', 'Global Supplies LLC']);
  });

  it('system excludes pending and inactive recipients from selection', async () => {
    await suite.helper.givenUserLoggedIntoChannelOne();
    await suite.helper.givenEnterpriseHasRecipientsWithMixedStatuses();
    await suite.helper.whenUserInitiatesCreateWirePayment();
    suite.helper.thenRecipientSelectionIncludesActiveRecipientsOnly(['Active Vendor Inc']);
    suite.helper.thenPendingAndInactiveExcluded(['Pending Vendor LLC', 'Inactive Supplier']);
  });

  it('system returns empty list when no active recipients exist', async () => {
    await suite.helper.givenUserLoggedIntoChannelOne();
    await suite.helper.givenEnterpriseHasNoActiveRecipients();
    await suite.helper.whenUserInitiatesCreateWirePayment();
    suite.helper.thenEmptyStateReturned();
  });

  it('user without wire entitlement receives access denied', async () => {
    await suite.helper.givenUserLoggedIntoChannelOne({ hasWireEntitlement: false });
    await suite.helper.whenUserAttemptsToAccessWirePayment();
    suite.helper.thenAccessDeniedWithMessage('You do not have permission to create wire payments');
  });
});
