/**
 * {{domainName}}-server.ts — server tier for the {{domainName}} aggregate.
 *
 * Repository (one lowdb JSON file for this aggregate root), {{DomainName}}sServer
 * (domain ops that call the repo), and the Express router. Routes only parse
 * the request and delegate (delegate-routes-to-domain-server).
 */
import { Router } from 'express';
import { Low } from 'lowdb';
import { JSONFilePreset } from 'lowdb/node';
import {
  {{DomainName}},
  {{DomainName}}s,
  {{DomainName}}Schema,
  Create{{DomainName}}InputSchema,
  type Create{{DomainName}}Input,
  type {{DomainName}}Search,
  type {{DomainName}}Repository,
  toDomainEntity,
} from './{{domainName}}';

type {{DomainName}}Store = {
  {{domainNames}}: unknown[];
};

const defaultData: {{DomainName}}Store = { {{domainNames}}: [] };
const STORE_PATH = 'data/{{domainNames}}.json';

function toDto(root: {{DomainName}}) {
  return {
    id: root.id,
    name: root.name,
    status: root.status.status,
    createdAt: root.createdAt,
  };
}

export class {{DomainName}}RepositoryServer implements {{DomainName}}Repository {
  constructor(private readonly db: Low<{{DomainName}}Store>) {}

  static async open(
    filePath: string = STORE_PATH,
  ): Promise<{{DomainName}}RepositoryServer> {
    const db = await JSONFilePreset<{{DomainName}}Store>(filePath, defaultData);
    return new {{DomainName}}RepositoryServer(db);
  }

  async load(id: string): Promise<{{DomainName}} | null> {
    await this.db.read();
    const doc = this.db.data.{{domainNames}}.find(
      (row) => {{DomainName}}Schema.parse(row).id === id,
    );
    if (!doc) return null;
    return toDomainEntity({{DomainName}}Schema.parse(doc));
  }

  async create(input: Create{{DomainName}}Input): Promise<{{DomainName}}> {
    const doc = {
      id: crypto.randomUUID(),
      name: input.name,
      status: 'Pending',
      createdAt: new Date().toISOString(),
    };
    await this.db.update(({ {{domainNames}} }) => {
      {{domainNames}}.push(doc);
    });
    return toDomainEntity({{DomainName}}Schema.parse(doc));
  }

  async search(query?: {{DomainName}}Search): Promise<{{DomainName}}[]> {
    await this.db.read();
    let collection = new {{DomainName}}s(
      this.db.data.{{domainNames}}.map((row) =>
        toDomainEntity({{DomainName}}Schema.parse(row)),
      ),
    );
    if (query?.status) {
      collection = collection.filterByStatus(query.status);
    }
    if (query?.name) {
      collection = collection.search(query.name);
    }
    return collection.toArray();
  }

  async update(root: {{DomainName}}): Promise<{{DomainName}}> {
    await this.db.update(({ {{domainNames}} }) => {
      const index = {{domainNames}}.findIndex(
        (row) => {{DomainName}}Schema.parse(row).id === root.id,
      );
      if (index >= 0) {
        {{domainNames}}[index] = toDto(root);
      }
    });
    return root;
  }
}

export class {{DomainName}}sServer extends {{DomainName}}s {
  static async loadAll(
    repo: {{DomainName}}Repository,
    opts?: { activeOnly?: boolean },
  ): Promise<{{DomainName}}[]> {
    const query = opts?.activeOnly ? { status: 'Active' as const } : undefined;
    return repo.search(query);
  }

  static async loadById(
    repo: {{DomainName}}Repository,
    id: string,
  ): Promise<{{DomainName}} | null> {
    return repo.load(id);
  }

  static async create(
    repo: {{DomainName}}Repository,
    input: Create{{DomainName}}Input,
  ): Promise<{{DomainName}}> {
    return repo.create(input);
  }

  static async update(
    repo: {{DomainName}}Repository,
    root: {{DomainName}},
  ): Promise<{{DomainName}}> {
    return repo.update(root);
  }
}

export function create{{DomainName}}sRouter(repo: {{DomainName}}Repository): Router {
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
