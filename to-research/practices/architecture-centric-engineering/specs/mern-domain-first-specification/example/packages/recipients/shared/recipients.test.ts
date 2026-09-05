import { describe, it, expect } from 'vitest';
import { Recipient } from './Recipient';
import { Recipients } from './Recipients';
import { RecipientStatus } from './RecipientStatus';

// ============================================================================
// Domain unit tests — shared domain classes, no HTTP, no React, no DB
// ============================================================================

function makeRecipient(overrides: Partial<{
  id: string;
  enterpriseId: string;
  name: string;
  status: 'Active' | 'Pending' | 'Inactive';
  bankName: string;
}>): Recipient {
  const { id = '1', enterpriseId = 'ent-1', name = 'Acme Corp', status = 'Active', bankName = 'Chase' } = overrides;
  return new Recipient(
    id, enterpriseId, name,
    '****1234', '00001234',
    new RecipientStatus(status, new Date()),
    { swiftBic: 'TESTUS33', name: bankName, addressLine1: '1 Main St', city: 'NY', country: 'US' },
    undefined,
    new Date(), undefined,
  );
}

describe('Recipient', () => {
  it('is eligible for payment when status is Active', () => {
    const recipient = makeRecipient({ status: 'Active' });
    expect(recipient.isEligibleForPayment()).toBe(true);
  });

  it('is not eligible for payment when status is Pending', () => {
    const recipient = makeRecipient({ status: 'Pending' });
    expect(recipient.isEligibleForPayment()).toBe(false);
  });

  it('is not eligible for payment when status is Inactive', () => {
    const recipient = makeRecipient({ status: 'Inactive' });
    expect(recipient.isEligibleForPayment()).toBe(false);
  });
});

describe('Recipients', () => {
  it('filterByStatus returns only recipients with matching status', () => {
    const collection = new Recipients([
      makeRecipient({ name: 'Active Vendor', status: 'Active' }),
      makeRecipient({ name: 'Pending Vendor', status: 'Pending' }),
      makeRecipient({ name: 'Inactive Vendor', status: 'Inactive' }),
    ]);
    const active = collection.filterByStatus('Active');
    expect(active.toArray().map(r => r.name)).toEqual(['Active Vendor']);
  });

  it('filterByEnterprise returns only recipients belonging to that enterprise', () => {
    const collection = new Recipients([
      makeRecipient({ name: 'Ours', enterpriseId: 'ent-1' }),
      makeRecipient({ name: 'Theirs', enterpriseId: 'ent-2' }),
    ]);
    expect(collection.filterByEnterprise('ent-1').toArray().map(r => r.name)).toEqual(['Ours']);
  });

  it('search matches on recipient name', () => {
    const collection = new Recipients([
      makeRecipient({ name: 'Acme Corporation' }),
      makeRecipient({ name: 'Global Supplies LLC' }),
    ]);
    expect(collection.search('acme').toArray().map(r => r.name)).toEqual(['Acme Corporation']);
  });

  it('search matches on bank name', () => {
    const collection = new Recipients([
      makeRecipient({ name: 'Vendor A', bankName: 'Chase Bank' }),
      makeRecipient({ name: 'Vendor B', bankName: 'Bank of America' }),
    ]);
    expect(collection.search('chase').toArray().map(r => r.name)).toEqual(['Vendor A']);
  });

  it('returns empty collection when no recipients match filter', () => {
    const collection = new Recipients([
      makeRecipient({ status: 'Pending' }),
    ]);
    expect(collection.filterByStatus('Active').length).toBe(0);
  });
});
