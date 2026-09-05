import { render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import { vi } from 'vitest';
import { RecipientListView } from '../../../packages/recipients/client/RecipientListView';
import { RecipientData, SelectRecipientBaseHelper } from './select-recipient.base';

vi.mock('../../../../packages/recipients/client/Recipient.api', () => ({
  RecipientApi: {
    loadByEnterprise: vi.fn(),
    selectByIds: vi.fn(),
  },
}));

import { RecipientApi } from '../../../../packages/recipients/client/Recipient.api';

export class SelectRecipientClientHelper extends SelectRecipientBaseHelper {
  givenActiveRecipients(data: RecipientData[]): void {
    const recipients = data.map(r => ({
      id: crypto.randomUUID(),
      enterpriseId: this.enterprise.id,
      name: r.name,
      accountNumber: r.accountMasked,
      accountNumberFull: r.accountMasked.replace('*', '0'),
      status: r.status,
      beneficiaryBank: {
        swiftBic: 'TESTUS33',
        name: r.bankName,
        addressLine1: '1 Test St',
        city: 'NY',
        country: 'US',
      },
      createdAt: new Date().toISOString(),
    }));
    vi.mocked(RecipientApi.loadByEnterprise).mockResolvedValue(recipients as never);
  }

  whenRecipientListViewRenders(): void {
    render(<RecipientListView />);
  }

  async thenRecipientNamesVisible(names: string[]): Promise<void> {
    await waitFor(() => {
      for (const name of names) {
        expect(screen.getByText(name)).toBeInTheDocument();
      }
    });
  }
}
