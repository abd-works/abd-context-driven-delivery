/**
 * {{domainName}}-server.ts — server tier for the {{domainName}} domain.
 *
 * Repository (Mongo I/O), {{DomainName}}sServer (domain ops that call the repo),
 * and the Express router. Routes only parse the request and delegate
 * (delegate-routes-to-domain-server).
 */
import { Router } from 'express';
import { Collection, Db } from 'mongodb';
import {
  {{DomainName}},
  {{DomainName}}s,
  {{DomainName}}Schema,
  Create{{DomainName}}InputSchema,
  type Create{{DomainName}}Input,
  type {{DomainName}}Repository,
  toDomainEntity,
} from './{{domainName}}';

export class {{DomainName}}RepositoryServer implements {{DomainName}}Repository {
  private collection: Collection;

  constructor(db: Db) {
    this.collection = db.collection('{{domainNames}}');
  }

  async findAll(): Promise<{{DomainName}}[]> {
    const docs = await this.collection.find().toArray();
    return docs.map(doc => toDomainEntity({{DomainName}}Schema.parse(doc)));
  }

  async findById(id: string): Promise<{{DomainName}} | null> {
    const doc = await this.collection.findOne({ id });
    if (!doc) return null;
    return toDomainEntity({{DomainName}}Schema.parse(doc));
  }

  async save(input: Create{{DomainName}}Input): Promise<{{DomainName}}> {
    const doc = {
      id: crypto.randomUUID(),
      name: input.name,
      status: 'Pending',
      createdAt: new Date(),
    };
    await this.collection.insertOne(doc);
    return toDomainEntity({{DomainName}}Schema.parse(doc));
  }
}

export class {{DomainName}}sServer extends {{DomainName}}s {
  static async loadAll(
    repo: {{DomainName}}Repository,
    opts?: { activeOnly?: boolean },
  ): Promise<{{DomainName}}[]> {
    const all = await repo.findAll();
    let collection: {{DomainName}}s = new {{DomainName}}s(all);
    if (opts?.activeOnly) {
      collection = collection.filterByStatus('Active');
    }
    return collection.toArray();
  }

  static async loadById(
    repo: {{DomainName}}Repository,
    id: string,
  ): Promise<{{DomainName}} | null> {
    return repo.findById(id);
  }

  static async create(
    repo: {{DomainName}}Repository,
    input: Create{{DomainName}}Input,
  ): Promise<{{DomainName}}> {
    return repo.save(input);
  }
}

export function create{{DomainName}}sRouter(repo: {{DomainName}}RepositoryServer): Router {
  const router = Router();

  router.get('/', async (req, res) => {
    const activeOnly = req.query.active_only === 'true';
    const items = await {{DomainName}}sServer.loadAll(repo, { activeOnly });
    res.json(items);
  });

  router.get('/:id', async (req, res) => {
    const item = await {{DomainName}}sServer.loadById(repo, req.params.id);
    if (!item) {
      res.status(404).json({ error: 'Not found' });
      return;
    }
    res.json(item);
  });

  router.post('/', async (req, res) => {
    const validation = Create{{DomainName}}InputSchema.safeParse(req.body);
    if (!validation.success) {
      res.status(400).json({ error: validation.error.issues[0].message });
      return;
    }
    const created = await {{DomainName}}sServer.create(repo, validation.data);
    res.status(201).json(created);
  });

  return router;
}
