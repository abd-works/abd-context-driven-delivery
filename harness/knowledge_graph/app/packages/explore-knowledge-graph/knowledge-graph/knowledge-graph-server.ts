import { Router } from 'express';
import { Low } from 'lowdb';
import { Memory } from 'lowdb';
import { JSONFilePreset } from 'lowdb/node';
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { extname, join, relative } from 'node:path';
import {
  KnowledgeGraph,
  KnowledgeGraphSchema,
  type CreateKnowledgeGraphInput,
  type GraphFilter,
  type KnowledgeGraphRepository,
  type KnowledgeGraphSearch,
} from './knowledge-graph';
import { knowledgeGraphFromWorkspace, type WorkspaceFile } from './workspace';

type KnowledgeGraphStore = {
  knowledge_graphs: unknown[];
};

const defaultData: KnowledgeGraphStore = { knowledge_graphs: [] };
const STORE_PATH = 'data/knowledge-graphs.json';

export class KnowledgeGraphRepositoryServer implements KnowledgeGraphRepository {
  constructor(private readonly db: Low<KnowledgeGraphStore>) {}

  static async open(
    filePath: string = STORE_PATH,
  ): Promise<KnowledgeGraphRepositoryServer> {
    const db = await JSONFilePreset<KnowledgeGraphStore>(filePath, defaultData);
    return new KnowledgeGraphRepositoryServer(db);
  }

  static openMemory(
    graphs: unknown[] = [],
  ): KnowledgeGraphRepositoryServer {
    const db = new Low<KnowledgeGraphStore>(new Memory(), {
      knowledge_graphs: graphs,
    });
    return new KnowledgeGraphRepositoryServer(db);
  }

  async load(id: string): Promise<KnowledgeGraph | null> {
    await this.db.read();
    const doc = this.db.data.knowledge_graphs.find((row) => {
      const parsed = KnowledgeGraphSchema.safeParse(row);
      return parsed.success && parsed.data.id === id;
    });
    if (!doc) {
      return null;
    }
    return KnowledgeGraph.fromDto(KnowledgeGraphSchema.parse(doc));
  }

  async create(input: CreateKnowledgeGraphInput): Promise<KnowledgeGraph> {
    const doc = {
      id: crypto.randomUUID(),
      folder: input.folder ?? '',
      practice_graphs: input.practiceGraphs,
    };
    const parsed = KnowledgeGraphSchema.parse(doc);
    await this.db.update(({ knowledge_graphs }) => {
      knowledge_graphs.push(parsed);
    });
    return KnowledgeGraph.fromDto(parsed);
  }

  async search(query?: KnowledgeGraphSearch): Promise<KnowledgeGraph[]> {
    await this.db.read();
    const graphs = this.db.data.knowledge_graphs.map((row) =>
      KnowledgeGraph.fromDto(KnowledgeGraphSchema.parse(row)),
    );
    if (!query?.id) {
      return graphs;
    }
    return graphs.filter((graph) => graph.id === query.id);
  }

  async update(root: KnowledgeGraph): Promise<KnowledgeGraph> {
    const parsed = root.toDto();
    await this.db.update(({ knowledge_graphs }) => {
      const index = knowledge_graphs.findIndex((row) => {
        const candidate = KnowledgeGraphSchema.safeParse(row);
        return candidate.success && candidate.data.id === root.id;
      });
      if (index >= 0) {
        knowledge_graphs[index] = parsed;
      }
    });
    return KnowledgeGraph.fromDto(parsed);
  }
}

export class KnowledgeGraphsServer {
  static async loadGraph(
    id: string,
    repo: KnowledgeGraphRepository,
  ): Promise<KnowledgeGraph | null> {
    return repo.load(id);
  }

  static async search(
    repo: KnowledgeGraphRepository,
    query?: KnowledgeGraphSearch,
  ): Promise<KnowledgeGraph[]> {
    return repo.search(query);
  }

  static async create(
    input: CreateKnowledgeGraphInput,
    repo: KnowledgeGraphRepository,
  ): Promise<KnowledgeGraph> {
    return repo.create(input);
  }

  static async selectFolder(
    folder: string,
    repo: KnowledgeGraphRepository,
  ): Promise<KnowledgeGraph> {
    if (!existsSync(folder) || !statSync(folder).isDirectory()) {
      throw new FolderNotFound(folder);
    }
    const files = _readWorkspaceFiles(folder);
    const graph = knowledgeGraphFromWorkspace(
      folder,
      files,
      crypto.randomUUID(),
    );
    return repo.create({
      folder: graph.folder,
      practiceGraphs: graph.toDto().practice_graphs,
    });
  }

  static browse(graph: KnowledgeGraph) {
    return graph.present();
  }

  static selectNode(graph: KnowledgeGraph, nodeId: string) {
    return graph.selectNode(nodeId).present();
  }

  static followRelationship(graph: KnowledgeGraph, toId: string) {
    return graph.followRelationship(toId).present();
  }

  static filterGraph(graph: KnowledgeGraph, filter: GraphFilter) {
    return graph.filterGraph(filter).present();
  }
}

export class FolderNotFound extends Error {
  constructor(folder: string) {
    super(`Folder not found: ${folder}`);
    this.name = 'FolderNotFound';
  }
}

const SKIP_DIR = new Set([
  'node_modules',
  '.git',
  'dist',
  '__pycache__',
  '.venv',
  'coverage',
  '.codeql',
]);

const SOURCE_EXT = new Set(['.ts', '.tsx', '.js', '.jsx', '.py']);

function _readWorkspaceFiles(folder: string): WorkspaceFile[] {
  const files: WorkspaceFile[] = [];
  _walk(folder, folder, files);
  return files;
}

function _walk(root: string, current: string, files: WorkspaceFile[]): void {
  if (files.length >= 500) {
    return;
  }
  for (const entry of readdirSync(current)) {
    if (SKIP_DIR.has(entry)) {
      continue;
    }
    const full = join(current, entry);
    const info = statSync(full);
    if (info.isDirectory()) {
      _walk(root, full, files);
      continue;
    }
    if (!SOURCE_EXT.has(extname(entry)) || entry.endsWith('.d.ts')) {
      continue;
    }
    files.push({
      relativePath: relative(root, full).replaceAll('\\', '/'),
      text: readFileSync(full, 'utf8'),
    });
    if (files.length >= 500) {
      return;
    }
  }
}

export function createKnowledgeGraphsRouter(
  repo: KnowledgeGraphRepository,
): Router {
  const router = Router();

  router.post('/scan', async (req, res) => {
    try {
      const graph = await KnowledgeGraphsServer.selectFolder(
        String(req.body.folder ?? ''),
        repo,
      );
      res.status(201).json(graph.present());
    } catch (error) {
      if (error instanceof FolderNotFound) {
        res.status(400).json({ error: error.message });
        return;
      }
      throw error;
    }
  });

  router.get('/', async (_req, res) => {
    const graphs = await KnowledgeGraphsServer.search(repo);
    res.json({
      knowledge_graphs: graphs.map((graph) => graph.toDto()),
      total: graphs.length,
    });
  });

  router.get('/:id', async (req, res) => {
    const graph = await KnowledgeGraphsServer.loadGraph(req.params.id, repo);
    if (!graph) {
      res.status(404).json({ error: 'KnowledgeGraph not found' });
      return;
    }
    const filtered = KnowledgeGraphsServer.filterGraph(
      graph,
      _filterFromQuery(req.query as Record<string, unknown>),
    );
    res.json(filtered);
  });

  router.post('/', async (req, res) => {
    const created = await KnowledgeGraphsServer.create(
      { practiceGraphs: req.body.practice_graphs },
      repo,
    );
    res.status(201).json(created.present());
  });

  router.post('/:id/select-node', async (req, res) => {
    const graph = await KnowledgeGraphsServer.loadGraph(req.params.id, repo);
    if (!graph) {
      res.status(404).json({ error: 'KnowledgeGraph not found' });
      return;
    }
    res.json(KnowledgeGraphsServer.selectNode(graph, req.body.node_id));
  });

  router.post('/:id/follow-relationship', async (req, res) => {
    const graph = await KnowledgeGraphsServer.loadGraph(req.params.id, repo);
    if (!graph) {
      res.status(404).json({ error: 'KnowledgeGraph not found' });
      return;
    }
    res.json(KnowledgeGraphsServer.followRelationship(graph, req.body.to_id));
  });

  return router;
}

function _filterFromQuery(query: Record<string, unknown>): GraphFilter {
  return {
    practice: _stringQuery(query.practice),
    connectorKind: _stringQuery(query.connector_kind),
    node: _stringQuery(query.node),
    violations: query.violations === 'true',
    rule: _stringQuery(query.rule),
  };
}

function _stringQuery(value: unknown): string | undefined {
  return typeof value === 'string' && value.length > 0 ? value : undefined;
}
