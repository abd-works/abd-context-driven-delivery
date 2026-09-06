import type { Page } from '@playwright/test';
import { SelectRecipientBaseHelper } from './select-recipient.base';

export class SelectRecipientE2eHelper extends SelectRecipientBaseHelper {
  constructor(private readonly page: Page) {
    super();
  }

  async givenActiveRecipientsSeeded(): Promise<void> {
    // E2E seed hook — wire to test API or fixture loader in a full app.
  }

  async whenUserOpensWirePaymentPage(): Promise<void> {
    await this.page.goto('/wire-payment/create');
  }

  async thenRecipientSelectionPageVisible(): Promise<void> {
    await this.page.waitForSelector('.recipient-list-view');
  }

  protected async seedRecipients(): Promise<void> {
    // Not used in E2E tier — seed via API in givenActiveRecipientsSeeded.
  }

  protected async seedUser(): Promise<void> {
    // Auth handled by E2E fixture in a full app.
  }

  async cleanup(): Promise<void> {
    // Teardown test data when wired to a live server.
  }
}
