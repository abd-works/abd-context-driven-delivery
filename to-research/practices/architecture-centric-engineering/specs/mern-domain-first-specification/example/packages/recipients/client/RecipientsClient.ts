import {
  Recipients,
  Recipient,
  SelectRecipientsInput,
  SelectRecipientsSchema,
} from '@channelone/recipients-shared';
import { RecipientApi } from './Recipient.api';
import { RecipientClient } from './RecipientClient';

/** Client-tier Recipients — extends shared collection with selection and API orchestration. */
export class RecipientsClient extends Recipients {
  constructor(
    items: Recipient[],
    private readonly selectedIds: Set<string> = new Set(),
  ) {
    super(items);
  }

  static async load(opts?: { activeOnly?: boolean }): Promise<RecipientsClient> {
    const items = await RecipientApi.loadByEnterprise(opts);
    return new RecipientsClient(items);
  }

  withItems(items: Recipient[]): RecipientsClient {
    return new RecipientsClient(items, this.selectedIds);
  }

  search(query: string): RecipientsClient {
    return this.withItems(super.search(query).toArray());
  }

  displayed(query: string): RecipientClient[] {
    const collection = query ? this.search(query) : this;
    return collection.toPresentation();
  }

  toPresentation(): RecipientClient[] {
    return this.toArray().map(r => RecipientClient.fromRecipient(r));
  }

  toggleSelection(id: string): RecipientsClient {
    const next = new Set(this.selectedIds);
    if (next.has(id)) {
      next.delete(id);
    } else {
      next.add(id);
    }
    return new RecipientsClient(this.toArray(), next);
  }

  isSelected(id: string): boolean {
    return this.selectedIds.has(id);
  }

  selectedCount(): number {
    return this.selectedIds.size;
  }

  getSelectedIds(): string[] {
    return Array.from(this.selectedIds);
  }

  getSelected(): Recipient[] {
    return this.toArray().filter(r => this.selectedIds.has(r.id));
  }

  async confirmSelection(): Promise<Recipient[]> {
    const input: SelectRecipientsInput = { recipientIds: this.getSelectedIds() };
    const validation = SelectRecipientsSchema.safeParse(input);
    if (!validation.success) {
      throw new Error(validation.error.issues[0].message);
    }
    return RecipientApi.selectByIds(input);
  }
}
