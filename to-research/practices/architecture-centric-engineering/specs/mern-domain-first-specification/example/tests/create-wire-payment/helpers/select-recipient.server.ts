import request from 'supertest';
import assert from 'node:assert';
import { SelectRecipientBaseHelper, RecipientData } from './select-recipient.base';

// Replace these imports with your actual app and db instances
// import { app } from '@channelone/app-server';
// import { db } from '@channelone/app-server-db';
declare const app: any;
declare const db: any;

export class SelectRecipientServerHelper extends SelectRecipientBaseHelper {
  private response!: request.Response;

  protected async seedRecipients(data: RecipientData[]): Promise<void> {
    await db.collection('recipients').insertMany(
      data.map(r => ({
        id: crypto.randomUUID(),
        enterpriseId: this.enterprise.id,
        name: r.name,
        status: r.status,
        beneficiaryBank: { name: r.bankName, swiftBic: 'TESTUS33', addressLine1: '1 Test St', city: 'NY', country: 'US' },
        accountNumber: r.accountMasked,
        accountNumberFull: r.accountMasked.replace('*', '0'),
        createdAt: new Date(),
      }))
    );
  }

  protected async seedUser(options: { hasWireEntitlement: boolean }): Promise<void> {
    this.user = { token: options.hasWireEntitlement ? 'valid-token' : 'no-entitlement-token' };
  }

  async cleanup(): Promise<void> {
    await db.collection('recipients').deleteMany({ enterpriseId: this.enterprise.id });
  }

  async whenUserInitiatesCreateWirePayment(): Promise<void> {
    // Route handler delegates to recipients-server domain class
    this.response = await request(app)
      .get('/api/recipients')
      .query({ activeOnly: 'true' })
      .set('Authorization', `Bearer ${this.user.token}`);
  }

  async whenUserAttemptsToAccessWirePayment(): Promise<void> {
    this.response = await request(app)
      .get('/api/recipients')
      .set('Authorization', `Bearer ${this.user.token}`);
  }

  thenRecipientSelectionIncludesActiveRecipientsOnly(expectedNames: string[]): void {
    assert.strictEqual(this.response.status, 200);
    const actualNames = (this.response.body.recipients as any[]).map(r => r.name);
    assert.deepStrictEqual(actualNames.sort(), expectedNames.sort());
    for (const r of this.response.body.recipients) {
      assert.strictEqual(r.status, 'Active');
    }
  }

  thenPendingAndInactiveExcluded(excludedNames: string[]): void {
    const actualNames = (this.response.body.recipients as any[]).map(r => r.name);
    for (const name of excludedNames) {
      assert.ok(!actualNames.includes(name), `${name} should be excluded`);
    }
  }

  thenEmptyStateReturned(): void {
    assert.strictEqual(this.response.status, 200);
    assert.strictEqual(this.response.body.recipients.length, 0);
  }

  thenAccessDeniedWithMessage(expectedMessage: string): void {
    assert.strictEqual(this.response.status, 403);
    assert.strictEqual(this.response.body.message, expectedMessage);
  }
}
