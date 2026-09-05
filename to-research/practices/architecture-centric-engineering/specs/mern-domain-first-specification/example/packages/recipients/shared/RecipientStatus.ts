export type RecipientStatusType = 'Active' | 'Pending' | 'Inactive';

export class RecipientStatus {
  constructor(
    public readonly status: RecipientStatusType,
    public readonly createdAt: Date,
    private readonly countryCode: 'US' | 'MX' | 'CA' = 'US'
  ) {}

  private static readonly MX_PENDING_PERIOD_MS = 30 * 60 * 1000;

  isEligibleForPayment(): boolean {
    return this.status === 'Active';
  }

  isPending(): boolean {
    return this.status === 'Pending';
  }

  get remainingPendingMinutes(): number | null {
    if (this.countryCode !== 'MX' || this.status !== 'Pending') return null;
    const elapsed = Date.now() - this.createdAt.getTime();
    const remaining = Math.max(0, RecipientStatus.MX_PENDING_PERIOD_MS - elapsed);
    return Math.ceil(remaining / 60000);
  }
}
