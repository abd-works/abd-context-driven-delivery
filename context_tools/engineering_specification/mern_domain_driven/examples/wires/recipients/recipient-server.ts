import { Router } from 'express';
import type { Collection, Db } from 'mongodb';
import {
  Recipient,
  Recipients,
  RecipientSchema,
  type RecipientRepository,
} from './recipients';

/**
 * recipient-server.ts — server tier for the recipients domain.
 *
 * Repository (Mongo I/O), RecipientsServer (domain ops that call the repo),
 * and the Express router. Routes only parse the request and delegate
 * (delegate-routes-to-domain-server).
 */

export class RecipientRepositoryServer implements RecipientRepository {
  constructor(private readonly db: Db) {}

  private get collection(): Collection {
    return this.db.collection('recipients');
  }

  async findByEnterprise(enterpriseId: string): Promise<Recipient[]> {
    const docs = await this.collection.find({ enterpriseId }).toArray();
    return docs.map((doc) => Recipient.fromDto(RecipientSchema.parse(doc)));
  }
}

export class RecipientsServer extends Recipients {
  static async loadByEnterprise(
    enterpriseId: string,
    repo: RecipientRepository,
    opts?: { activeOnly?: boolean },
  ): Promise<Recipient[]> {
    const all = await repo.findByEnterprise(enterpriseId);
    let collection: Recipients = new Recipients(all);
    if (opts?.activeOnly) {
      collection = collection.filterByStatus('Active');
    }
    return collection.toArray();
  }
}

export function createRecipientsRouter(repo: RecipientRepositoryServer): Router {
  const router = Router();

  router.get('/', async (req, res) => {
    const enterpriseId = (req as any).user.enterpriseId;
    const activeOnly = req.query.activeOnly === 'true';
    const recipients = await RecipientsServer.loadByEnterprise(enterpriseId, repo, {
      activeOnly,
    });
    res.json({ recipients, total: recipients.length });
  });

  return router;
}
