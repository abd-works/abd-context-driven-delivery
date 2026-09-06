import { Collection, Db } from 'mongodb';
import {
  Recipient,
  RecipientSchema,
  RecipientRepository,
} from '@channelone/recipients-shared';

/** MongoDB implementation of RecipientRepository. */
export class RecipientRepositoryServer implements RecipientRepository {
  private collection: Collection;

  constructor(db: Db) {
    this.collection = db.collection('recipients');
  }

  async findAll(): Promise<Recipient[]> {
    const docs = await this.collection.find().toArray();
    return docs.map(doc => Recipient.fromDto(RecipientSchema.parse(doc)));
  }

  async findByIds(ids: string[]): Promise<Recipient[]> {
    const docs = await this.collection.find({ id: { $in: ids } }).toArray();
    return docs.map(doc => Recipient.fromDto(RecipientSchema.parse(doc)));
  }

  async findByEnterprise(enterpriseId: string): Promise<Recipient[]> {
    const docs = await this.collection.find({ enterpriseId }).toArray();
    return docs.map(doc => Recipient.fromDto(RecipientSchema.parse(doc)));
  }
}
