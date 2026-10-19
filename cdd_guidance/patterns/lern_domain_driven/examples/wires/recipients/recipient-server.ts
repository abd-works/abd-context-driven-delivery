import { Router } from 'express';
import { Low } from 'lowdb';
import { JSONFilePreset } from 'lowdb/node';
import {
  Recipient,
  Recipients,
  RecipientSchema,
  type CreateRecipientInput,
  type RecipientRepository,
  type RecipientSearch,
} from './recipients';

/**
 * recipient-server.ts — server tier for the recipients aggregate.
 */

type RecipientStore = {
  recipients: unknown[];
};

const defaultData: RecipientStore = { recipients: [] };
const STORE_PATH = 'data/recipients.json';

export class RecipientRepositoryServer implements RecipientRepository {
  constructor(private readonly db: Low<RecipientStore>) {}

  static async open(filePath: string = STORE_PATH): Promise<RecipientRepositoryServer> {
    const db = await JSONFilePreset<RecipientStore>(filePath, defaultData);
    return new RecipientRepositoryServer(db);
  }

  async load(id: string): Promise<Recipient | null> {
    await this.db.read();
    const doc = this.db.data.recipients.find((row) => {
      const parsed = RecipientSchema.safeParse(row);
      return parsed.success && parsed.data.id === id;
    });
    if (!doc) return null;
    return Recipient.fromDto(RecipientSchema.parse(doc));
  }

  async create(input: CreateRecipientInput): Promise<Recipient> {
    const doc = {
      id: crypto.randomUUID(),
      name: input.name,
      status: 'Pending' as const,
      enterpriseId: input.enterpriseId,
      beneficiaryBank: input.beneficiaryBank,
      createdAt: new Date().toISOString(),
    };
    await this.db.update(({ recipients }) => {
      recipients.push(doc);
    });
    return Recipient.fromDto(RecipientSchema.parse(doc));
  }

  async search(query?: RecipientSearch): Promise<Recipient[]> {
    await this.db.read();
    let collection = new Recipients(
      this.db.data.recipients.map((row) => Recipient.fromDto(RecipientSchema.parse(row))),
    );
    if (query?.enterpriseId) {
      collection = new Recipients(
        collection.toArray().filter((r) => r.enterpriseId === query.enterpriseId),
      );
    }
    if (query?.status) {
      collection = collection.filterByStatus(query.status);
    }
    if (query?.name) {
      collection = collection.search(query.name);
    }
    return collection.toArray();
  }

  async update(root: Recipient): Promise<Recipient> {
    await this.db.update(({ recipients }) => {
      const index = recipients.findIndex((row) => {
        const parsed = RecipientSchema.safeParse(row);
        return parsed.success && parsed.data.id === root.id;
      });
      if (index >= 0) {
        recipients[index] = {
          id: root.id,
          name: root.name,
          status: root.status,
          enterpriseId: root.enterpriseId,
          beneficiaryBank: { name: root.bankName, routingNumber: '' },
          createdAt: new Date().toISOString(),
        };
      }
    });
    return root;
  }
}

export class RecipientsServer extends Recipients {
  static async loadByEnterprise(
    enterpriseId: string,
    repo: RecipientRepository,
    opts?: { activeOnly?: boolean },
  ): Promise<Recipient[]> {
    return repo.search({
      enterpriseId,
      status: opts?.activeOnly ? 'Active' : undefined,
    });
  }
}

export function createRecipientsRouter(repo: RecipientRepository): Router {
  const router = Router();

  router.get('/', async (req, res) => {
    const enterpriseId = (req as { user: { enterpriseId: string } }).user.enterpriseId;
    const activeOnly = req.query.activeOnly === 'true';
    const recipients = await RecipientsServer.loadByEnterprise(enterpriseId, repo, {
      activeOnly,
    });
    res.json({ recipients, total: recipients.length });
  });

  return router;
}
