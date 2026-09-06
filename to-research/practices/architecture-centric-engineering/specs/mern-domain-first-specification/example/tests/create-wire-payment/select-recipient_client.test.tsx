import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { SelectRecipientClientHelper } from './helpers/select-recipient.client';

// ============================================================================
// STORY: View Active Recipients for Wire Payment
// Sub-Epic: Select Recipient | Epic: Create Wire Payment
// Client emphasis: render list, search filter, selection state
// ============================================================================

describe('View Active Recipients for Wire Payment', () => {
  let helper: SelectRecipientClientHelper;

  beforeEach(() => {
    helper = new SelectRecipientClientHelper();
    vi.clearAllMocks();
  });

  it('user views list of active recipients when initiating wire payment', async () => {
    helper.givenActiveRecipients([
      { name: 'Acme Corporation', status: 'Active', bankName: 'Chase Bank', accountMasked: '****1234' },
      { name: 'Global Supplies LLC', status: 'Active', bankName: 'Bank of America', accountMasked: '****5678' },
    ]);
    helper.whenRecipientListViewRenders();
    await helper.thenRecipientNamesVisible(['Acme Corporation', 'Global Supplies LLC']);
  });

  it('system displays empty state when no active recipients exist', async () => {
    helper.givenActiveRecipients([]);
    helper.whenRecipientListViewRenders();
    await waitFor(() => {
      expect(screen.getByText('No active recipients available')).toBeInTheDocument();
    });
  });
});
