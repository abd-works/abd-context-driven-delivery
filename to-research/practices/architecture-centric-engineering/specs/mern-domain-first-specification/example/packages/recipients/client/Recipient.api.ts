import {
  Recipient,
  RecipientSchema,
  SelectRecipientsInput,
} from '@channelone/recipients-shared';
import { RecipientClient } from './RecipientClient';

const API_BASE = '/api/recipients';

function hydrateRecipients(raw: unknown[]): RecipientClient[] {
  return raw.map(item => {
    const dto = RecipientSchema.parse(item);
    return RecipientClient.fromRecipient(Recipient.fromDto(dto));
  });
}

/** Type-safe HTTP client for Recipient operations. */
export class RecipientApi {
  static async loadByEnterprise(opts?: { activeOnly?: boolean }): Promise<RecipientClient[]> {
    const params = new URLSearchParams();
    if (opts?.activeOnly) params.set('activeOnly', 'true');
    const response = await fetch(`${API_BASE}?${params}`);
    const data = await response.json();
    return hydrateRecipients(data.recipients);
  }

  static async selectByIds(input: SelectRecipientsInput): Promise<RecipientClient[]> {
    const response = await fetch(`${API_BASE}/select`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    });
    const data = await response.json();
    return hydrateRecipients(data.selected);
  }
}
