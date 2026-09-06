import {
  Recipients,
  Recipient,
  RecipientRepository,
  RecipientStatusType,
} from '@channelone/recipients-shared';

/** Server-tier Recipients — extends shared collection with persistence-backed loaders. */
export class RecipientsServer extends Recipients {
  static async loadByEnterprise(
    enterpriseId: string,
    repo: RecipientRepository,
    opts?: { activeOnly?: boolean },
  ): Promise<Recipient[]> {
    const all = await repo.findByEnterprise(enterpriseId);
    let collection: Recipients = new Recipients(all);
    if (opts?.activeOnly) {
      collection = collection.filterByStatus('Active' as RecipientStatusType);
    }
    return collection.toArray();
  }

  static async selectByIds(ids: string[], repo: RecipientRepository): Promise<Recipient[]> {
    return repo.findByIds(ids);
  }
}
