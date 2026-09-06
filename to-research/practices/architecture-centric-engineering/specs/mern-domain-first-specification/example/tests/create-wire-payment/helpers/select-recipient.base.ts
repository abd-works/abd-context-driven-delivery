export interface RecipientData {
  name: string;
  status: 'Active' | 'Pending' | 'Inactive';
  bankName: string;
  accountMasked: string;
}

export abstract class SelectRecipientBaseHelper {
  protected enterprise: { id: string } = { id: 'test-enterprise-id' };
  protected user: { token: string } = { token: '' };

  static readonly ACTIVE_RECIPIENTS: RecipientData[] = [
    { name: 'Acme Corporation', status: 'Active', bankName: 'Chase Bank', accountMasked: '****1234' },
    { name: 'Global Supplies LLC', status: 'Active', bankName: 'Bank of America', accountMasked: '****5678' },
  ];

  static readonly MIXED_STATUS_RECIPIENTS: RecipientData[] = [
    { name: 'Active Vendor Inc', status: 'Active', bankName: 'Chase Bank', accountMasked: '****1111' },
    { name: 'Pending Vendor LLC', status: 'Pending', bankName: 'Wells Fargo', accountMasked: '****2222' },
    { name: 'Inactive Supplier', status: 'Inactive', bankName: 'Citi', accountMasked: '****3333' },
  ];

  protected abstract seedRecipients(data: RecipientData[]): Promise<void>;
  protected abstract seedUser(options: { hasWireEntitlement: boolean }): Promise<void>;
  abstract cleanup(): Promise<void>;

  async givenUserLoggedIntoChannelOne(options = { hasWireEntitlement: true }): Promise<void> {
    await this.seedUser(options);
  }

  async givenEnterpriseHasRecipientsWithActiveStatus(
    data: RecipientData[] = SelectRecipientBaseHelper.ACTIVE_RECIPIENTS
  ): Promise<void> {
    await this.seedRecipients(data);
  }

  async givenEnterpriseHasRecipientsWithMixedStatuses(
    data: RecipientData[] = SelectRecipientBaseHelper.MIXED_STATUS_RECIPIENTS
  ): Promise<void> {
    await this.seedRecipients(data);
  }

  async givenEnterpriseHasNoActiveRecipients(): Promise<void> {
    await this.cleanup();
  }
}
