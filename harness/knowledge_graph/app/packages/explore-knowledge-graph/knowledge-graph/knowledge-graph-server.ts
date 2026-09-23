import { Router } from 'express';
import { Low } from 'lowdb';
import { Memory } from 'lowdb';
import { JSONFilePreset } from 'lowdb/node';
import { spawnSync } from 'node:child_process';
import { existsSync, readdirSync, readFileSync, statSync, writeFileSync, mkdirSync } from 'node:fs';
import { basename, dirname, delimiter, join, relative } from 'node:path';
import {
  KnowledgeGraph,
  KnowledgeGraphSchema,
  type CreateKnowledgeGraphInput,
  type GraphFilter,
  type KnowledgeGraphDto,
  type KnowledgeGraphRepository,
  type KnowledgeGraphSearch,
} from './knowledge-graph';
import {
  isScanSourcePath,
  knowledgeGraphFromWorkspace,
  resolveScanRoot,
  scanSourceFiles,
  SKIP_DIR,
  type WorkspaceFile,
} from './workspace';
import { overlayWorkspaceTree } from './workspace-overlay';

type KnowledgeGraphStore = {
  knowledge_graphs: unknown[];
};

const defaultData: KnowledgeGraphStore = { knowledge_graphs: [] };
const STORE_PATH = 'data/knowledge-graphs.json';
const SCAN_ROOT_PATH = 'data/scan-root.json';

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
    return graphFromWorkspaceDto(KnowledgeGraphSchema.parse(doc));
  }

  async create(input: CreateKnowledgeGraphInput): Promise<KnowledgeGraph> {
    const doc = {
      id: crypto.randomUUID(),
      folder: input.folder ?? '',
      practice_graphs: input.practiceGraphs,
    };
    const parsed = KnowledgeGraphSchema.parse(doc);
    await this.db.update((data) => {
      data.knowledge_graphs = [parsed];
    });
    return graphFromWorkspaceDto(parsed);
  }

  async search(query?: KnowledgeGraphSearch): Promise<KnowledgeGraph[]> {
    await this.db.read();
    const graphs = this.db.data.knowledge_graphs.map((row) =>
      graphFromWorkspaceDto(KnowledgeGraphSchema.parse(row)),
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
    return graphFromWorkspaceDto(parsed);
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
    files?: WorkspaceFile[],
    force = false,
  ): Promise<KnowledgeGraph> {
    const uploaded = files ? scanSourceFiles(files) : [];
    const root =
      uploaded.length > 0 && !_isDir(folder)
        ? folder || _diskScanRoot('')
        : _resolvePickedFolder(folder);
    if (_isDir(root)) {
      _writeLastScanRoot(root);
    }
    const graph =
      uploaded.length > 0
        ? knowledgeGraphFromWorkspace(root, uploaded, crypto.randomUUID())
        : _fromPracticeHierarchyCli(root, Boolean(force));
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

const SKIP_DIRS = SKIP_DIR;

function _isDir(folder: string): boolean {
  return folder.length > 0 && existsSync(folder) && statSync(folder).isDirectory();
}

function _diskScanRoot(chosen: string): string {
  const last = _readLastScanRoot();
  const root = resolveScanRoot(
    _isDir(chosen) ? chosen : undefined,
    last && _isDir(last) ? last : undefined,
    _repoRoot(),
  );
  if (!_isDir(root)) {
    throw new FolderNotFound(root);
  }
  return root;
}

function _resolvePickedFolder(folder: string): string {
  const chosen = folder.trim();
  if (_isDir(chosen)) {
    return chosen;
  }
  const last = _readLastScanRoot();
  const repo = _repoRoot();
  const bases = [last, repo, last ? dirname(last) : '', dirname(repo)].filter(
    Boolean,
  );
  for (const base of bases) {
    if (basename(base) === chosen && _isDir(base)) {
      return base;
    }
    const nested = chosen ? join(base, chosen) : '';
    if (nested && _isDir(nested)) {
      return nested;
    }
  }
  return _diskScanRoot('');
}

function _repoRoot(): string {
  let dir = process.cwd();
  while (true) {
    if (existsSync(join(dir, '.git'))) {
      return dir;
    }
    const parent = dirname(dir);
    if (parent === dir) {
      return process.cwd();
    }
    dir = parent;
  }
}

function _python(): string {
  if (process.env.PYTHON) {
    return process.env.PYTHON;
  }
  const venvWin = join(_repoRoot(), '.venv', 'Scripts', 'python.exe');
  const venvUnix = join(_repoRoot(), '.venv', 'bin', 'python');
  if (existsSync(venvWin)) {
    return venvWin;
  }
  if (existsSync(venvUnix)) {
    return venvUnix;
  }
  return 'python';
}

function _readLastScanRoot(): string | undefined {
  if (!existsSync(SCAN_ROOT_PATH)) {
    return undefined;
  }
  try {
    const parsed = JSON.parse(readFileSync(SCAN_ROOT_PATH, 'utf8')) as {
      folder?: string;
    };
    return parsed.folder;
  } catch {
    return undefined;
  }
}

function _writeLastScanRoot(folder: string): void {
  mkdirSync(dirname(SCAN_ROOT_PATH), { recursive: true });
  writeFileSync(SCAN_ROOT_PATH, `${JSON.stringify({ folder }, null, 2)}\n`);
}

function _readWorkspaceFromDisk(folder: string): WorkspaceFile[] {
  if (!existsSync(folder) || !statSync(folder).isDirectory()) {
    throw new FolderNotFound(folder);
  }
  const files: WorkspaceFile[] = [];
  _walk(folder, folder, files);
  return scanSourceFiles(files);
}

function _walk(root: string, current: string, files: WorkspaceFile[]): void {
  if (files.length >= 500) {
    return;
  }
  for (const entry of readdirSync(current)) {
    if (SKIP_DIRS.has(entry)) {
      continue;
    }
    const full = join(current, entry);
    const info = statSync(full);
    if (info.isDirectory()) {
      _walk(root, full, files);
      continue;
    }
    if (!isScanSourcePath(relative(root, full))) {
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
      const files = Array.isArray(req.body.files) ? req.body.files : undefined;
      const graph = await KnowledgeGraphsServer.selectFolder(
        String(req.body.folder ?? ''),
        repo,
        files,
        Boolean(req.body.force),
      );
      res.status(201).json(graph.present());
    } catch (error) {
      if (error instanceof FolderNotFound) {
        res.status(400).json({ error: error.message });
        return;
      }
      res.status(500).json({
        error: error instanceof Error ? error.message : 'Scan failed',
      });
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

function _fromPracticeHierarchyCli(root: string, force = false): KnowledgeGraph {
  const cached = join(root, '.context', 'explorer-graph.json');
  if (!force && existsSync(cached)) {
    const dto = JSON.parse(readFileSync(cached, 'utf8'));
    dto.folder = dto.folder || root;
    return graphFromWorkspaceDto(dto);
  }
  const repo = _repoRoot();
  const script = join(
    repo,
    'harness',
    'knowledge_graph',
    'write_practice_hierarchy.py',
  );
  const pythonPath = [
    repo,
    join(repo, 'harness'),
    join(repo, 'tools'),
    join(repo, 'practices'),
    join(repo, 'actions'),
    process.env.PYTHONPATH ?? '',
  ]
    .filter(Boolean)
    .join(delimiter);
  const result = spawnSync(
    _python(),
    [script, '--json', '--no-populate', root],
    {
      cwd: repo,
      env: { ...process.env, PYTHONPATH: pythonPath },
      encoding: 'utf8',
      maxBuffer: 64 * 1024 * 1024,
    },
  );
  if (result.status !== 0) {
    if (existsSync(cached)) {
      const dto = JSON.parse(readFileSync(cached, 'utf8'));
      dto.folder = dto.folder || root;
      return graphFromWorkspaceDto(dto);
    }
    throw new Error(
      result.stderr || result.stdout || 'write_practice_hierarchy.py failed',
    );
  }
  const line = (result.stdout || '')
    .trim()
    .split('\n')
    .filter(Boolean)
    .at(-1);
  if (!line) {
    throw new Error('write_practice_hierarchy.py printed no JSON');
  }
  return graphFromWorkspaceDto(JSON.parse(line));
}

function graphFromWorkspaceDto(dto: KnowledgeGraphDto): KnowledgeGraph {
  return KnowledgeGraph.fromDto(overlayWorkspaceTree(dto));
}

function _filterFromQuery(query: Record<string, unknown>): GraphFilter {
  return {
    practices: _stringList(query.practice),
    stages: _stringList(query.stage ?? query.fidelity),
    nodeTypes: _stringList(query.node_type),
    relationshipTypes: _stringList(query.relationship_type),
    connectorKind: _stringQuery(query.connector_kind),
    node: _stringQuery(query.node),
    violations: query.violations === 'true',
    rules: _stringList(query.rule),
  };
}

function _stringQuery(value: unknown): string | undefined {
  return typeof value === 'string' && value.length > 0 ? value : undefined;
}

function _stringList(value: unknown): string[] | undefined {
  const raw = Array.isArray(value) ? value : value == null ? [] : [value];
  const items = raw.flatMap((entry) =>
    typeof entry === 'string' ? entry.split(',').map((part) => part.trim()) : [],
  ).filter(Boolean);
  return items.length > 0 ? items : undefined;
}
