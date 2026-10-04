import { Router } from 'express';
import { Low } from 'lowdb';
import { Memory } from 'lowdb';
import { JSONFilePreset } from 'lowdb/node';
import { spawnSync } from 'node:child_process';
import { existsSync, readdirSync, readFileSync, statSync, writeFileSync, mkdirSync } from 'node:fs';
import { basename, dirname, delimiter, isAbsolute, join, relative, resolve } from 'node:path';
import {
  KnowledgeGraph,
  KnowledgeGraphSchema,
  type CreateKnowledgeGraphInput,
  type GraphFilter,
  type KnowledgeGraphDto,
  type KnowledgeGraphRepository,
  type KnowledgeGraphSearch,
} from './knowledge-graph/graph';
import { KnowledgeGraphNode } from './knowledge-graph/knowledge-graph-node';
import { resolveNamedFolder } from './knowledge-graph/workspace';
import { databaseBuildRequired } from './knowledge-graph/knowledge-graph';

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
    force = false,
  ): Promise<KnowledgeGraph> {
    const root = _resolvePickedFolder(folder);
    if (_isDir(root)) {
      _writeLastScanRoot(root);
    }
    const graph = _fromPracticeHierarchyCli(root, force);
    return repo.create({
      folder: root,
      practiceGraphs: graph.toDto().practice_graphs,
    });
  }

  static browse(graph: KnowledgeGraph) {
    return httpPresent(graph.present());
  }

  static selectNode(graph: KnowledgeGraph, nodeId: string) {
    return httpPresent(graph.selectNode(nodeId).present());
  }

  static followRelationship(graph: KnowledgeGraph, toId: string) {
    return httpPresent(graph.followRelationship(toId).present());
  }

  static filterGraph(graph: KnowledgeGraph, filter: GraphFilter) {
    return httpPresent(graph.filterGraph(filter).present());
  }

  static readSource(
    folder: string,
    ranges: { file: string; start_line: number; end_line: number }[],
  ): { file: string; start_line: number; end_line: number; text: string }[] {
    const root = _resolvePickedFolder(folder);
    return ranges.map((range) => ({
      file: range.file,
      start_line: range.start_line,
      end_line: range.end_line,
      text: _readSourceText(root, range.file, range.start_line, range.end_line),
    }));
  }

  static async createDatabase(
    folder: string,
    repo: KnowledgeGraphRepository,
  ): Promise<KnowledgeGraph> {
    const model = new KnowledgeGraphNode(null, null, null, null);
    model.folder = folder;
    model.createDatabase();
    return _runDatabaseOperation('create-database', folder, repo);
  }

  static async refreshMaster(
    folder: string,
    repo: KnowledgeGraphRepository,
  ): Promise<KnowledgeGraph> {
    return _runDatabaseOperation('refresh-master', folder, repo);
  }

  static async reloadWorkingCopy(
    folder: string,
    repo: KnowledgeGraphRepository,
  ): Promise<KnowledgeGraph> {
    return _runDatabaseOperation('reload-working-copy', folder, repo);
  }
}

export class FolderNotFound extends Error {
  constructor(folder: string) {
    super(`Folder not found: ${folder}`);
    this.name = 'FolderNotFound';
  }
}

function _isDir(folder: string): boolean {
  return folder.length > 0 && existsSync(folder) && statSync(folder).isDirectory();
}

function _resolvePickedFolder(folder: string): string {
  const chosen = folder.trim();
  const repo = _repoRoot();
  const last = _readLastScanRoot();
  if (!chosen || chosen === 'workspace') {
    if (last && _isDir(last)) {
      return last;
    }
    return repo;
  }
  const bases = [
    repo,
    last,
    last ? dirname(last) : '',
    dirname(repo),
    ..._knownFolderBases(),
  ].filter(Boolean);
  const found = resolveNamedFolder(
    chosen,
    bases,
    _isDir,
    (base) => {
      try {
        return readdirSync(base);
      } catch {
        return [];
      }
    },
    join,
    basename,
  );
  if (found) {
    return found;
  }
  throw new FolderNotFound(chosen);
}

function _knownFolderBases(): string[] {
  const found: string[] = [];
  const dev = 'C:\\dev\\paradise-mobile';
  if (_isDir(dev)) {
    found.push(dev);
  }
  const home = process.env.USERPROFILE || process.env.HOME || '';
  if (!home || !_isDir(home)) {
    return found;
  }
  try {
    for (const name of readdirSync(home)) {
      if (!name.toLowerCase().startsWith('onedrive')) {
        continue;
      }
      const mobile = join(home, name, 'personal', 'paradise-mobile');
      if (_isDir(mobile)) {
        found.push(mobile);
      }
    }
  } catch {
    return found;
  }
  return found;
}

function _databaseRoot(folder: string): string {
  return _resolvePickedFolder(folder);
}

function _codeqlReady(root: string): boolean {
  return (
    _isDir(join(root, '.codeql', 'javascript-master')) &&
    _isDir(join(root, '.codeql', 'javascript-working-copy'))
  );
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

function _pythonEnv(): NodeJS.ProcessEnv {
  const repo = _repoRoot();
  const harness = join(repo, 'harness').toLowerCase();
  const parts = [
    repo,
    join(repo, 'tools'),
    join(repo, 'practices'),
    join(repo, 'actions'),
    ...(process.env.PYTHONPATH ?? '').split(delimiter),
  ].filter(
    (item) =>
      Boolean(item) && item.replaceAll('/', '\\').toLowerCase() !== harness,
  );
  return { ...process.env, PYTHONPATH: parts.join(delimiter) };
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

export function createKnowledgeGraphsRouter(
  repo: KnowledgeGraphRepository,
): Router {
  const router = Router();

  router.post('/create-database', async (req, res) => {
    await _databaseRoute(req, res, repo, KnowledgeGraphsServer.createDatabase);
  });

  router.post('/refresh-master', async (req, res) => {
    await _databaseRoute(req, res, repo, KnowledgeGraphsServer.refreshMaster);
  });

  router.post('/reload-working-copy', async (req, res) => {
    await _databaseRoute(req, res, repo, KnowledgeGraphsServer.reloadWorkingCopy);
  });

  router.post('/scan', async (req, res) => {
    try {
      const graph = await KnowledgeGraphsServer.selectFolder(
        String(req.body.folder ?? ''),
        repo,
        Boolean(req.body.force),
      );
      res.status(201).json(httpPresent(graph.present()));
    } catch (error) {
      if (error instanceof FolderNotFound) {
        const paths = _relativePaths(req.body.paths);
        if (paths.length > 0) {
          res.status(201).json({
            folder: String(req.body.folder ?? ''),
            listed_tree: _treeFromPaths(paths),
            knowledge_graph: { practice_graphs: [] },
            filter_options: {
              practices: [],
              stages: [],
              node_types: [],
              relationship_types: [],
              rules: [],
            },
          });
          return;
        }
        res.status(400).json({ error: error.message });
        return;
      }
      res.status(500).json({
        error: error instanceof Error ? error.message : 'Scan failed',
      });
    }
  });

  router.post('/source', (req, res) => {
    try {
      const ranges = Array.isArray(req.body.ranges) ? req.body.ranges : [];
      res.json({
        ranges: KnowledgeGraphsServer.readSource(
          String(req.body.folder ?? ''),
          ranges.map((range: { file?: string; start_line?: number; end_line?: number }) => ({
            file: String(range.file ?? ''),
            start_line: Number(range.start_line),
            end_line: Number(range.end_line),
          })),
        ),
      });
    } catch (error) {
      res.status(400).json({
        error: error instanceof Error ? error.message : 'Could not read source',
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
    res.status(201).json(httpPresent(created.present()));
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

async function _databaseRoute(
  req: { body: { folder?: string } },
  res: {
    status: (code: number) => { json: (body: unknown) => void };
    json: (body: unknown) => void;
  },
  repo: KnowledgeGraphRepository,
  run: (
    folder: string,
    repo: KnowledgeGraphRepository,
  ) => Promise<KnowledgeGraph>,
) {
  try {
    const graph = await run(String(req.body.folder ?? ''), repo);
    res.status(201).json(httpPresent(graph.present()));
  } catch (error) {
    if (error instanceof FolderNotFound) {
      res.status(400).json({ error: error.message });
      return;
    }
    res.status(500).json({
      error: error instanceof Error ? error.message : 'Database operation failed',
    });
  }
}

async function _runDatabaseOperation(
  operation: 'create-database' | 'refresh-master' | 'reload-working-copy',
  folder: string,
  repo: KnowledgeGraphRepository,
): Promise<KnowledgeGraph> {
  const root = _databaseRoot(folder);
  if (_isDir(root)) {
    _writeLastScanRoot(root);
  }
  if (databaseBuildRequired(operation, _codeqlReady(root))) {
    console.log(`${operation} ${root}`);
    _spawnDatabaseCli(operation, root);
  }
  return KnowledgeGraphsServer.selectFolder(root, repo);
}

function _spawnDatabaseCli(
  operation: 'create-database' | 'refresh-master' | 'reload-working-copy',
  root: string,
): void {
  const repo = _repoRoot();
  const script = join(repo, 'harness', 'knowledge_graph', 'database_cli.py');
  const result = spawnSync(_python(), [script, operation, root], {
    cwd: repo,
    env: _pythonEnv(),
    encoding: 'utf8',
    maxBuffer: 64 * 1024 * 1024,
    timeout: 2 * 60 * 60 * 1000,
  });
  if (result.status !== 0) {
    throw new Error(
      [result.stderr, result.stdout, result.error?.message]
        .filter(Boolean)
        .join('\n') || `${operation} failed`,
    );
  }
}

function _fromPracticeHierarchyCli(
  root: string,
  force = false,
  fromScratch = false,
): KnowledgeGraph {
  const cached = join(root, '.context', 'explorer-graph.json');
  if (!force) {
    return _graphFromCache(cached, root);
  }
  const repo = _repoRoot();
  const script = join(
    repo,
    'harness',
    'knowledge_graph',
    'write_practice_hierarchy.py',
  );
  const pythonPath = _pythonEnv();
  const args = [script, '--json'];
  if (!force && !fromScratch) {
    args.push('--no-populate');
  }
  args.push(root);
  const result = spawnSync(_python(), args, {
    cwd: repo,
    env: pythonPath,
    encoding: 'utf8',
    maxBuffer: 64 * 1024 * 1024,
  });
  if (result.status !== 0) {
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
  const dto = JSON.parse(line) as KnowledgeGraphDto;
  dto.folder = root;
  const graph = graphFromWorkspaceDto(dto);
  if (_graphIsEmpty(graph)) {
    throw new Error('Knowledge graph has no nodes');
  }
  return graph;
}

function _graphIsEmpty(graph: KnowledgeGraph): boolean {
  return graph.toDto().practice_graphs.every((item) => item.nodes.length === 0);
}

const DISK_SKIP = new Set([
  'node_modules',
  '.git',
  'dist',
  'build',
  '__pycache__',
  '.venv',
  'venv',
  'coverage',
  '.codeql',
  '.codeql-db',
  '.context',
  '.cursor',
  '.vscode',
  '.github',
  'htmlcov',
]);

type DirectoryRow = {
  node_id: string;
  name: string;
  semantic_type: string;
  is_file: boolean;
  is_folder: boolean;
  children: DirectoryRow[];
  rules: [];
  relationships: [];
  source?: { file: string; start_line: number; end_line: number; text: string };
};

function _relativePaths(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value
    .map((entry) => String(entry ?? '').replaceAll('\\', '/'))
    .filter((entry) => entry.length > 0 && !entry.split('/').some((part) => _skipDiskName(part)));
}

function _skipDiskName(name: string): boolean {
  return !name || name.startsWith('.') || DISK_SKIP.has(name);
}

function _folderRow(name: string, relative: string): DirectoryRow {
  return {
    node_id: `pkg:${relative}`,
    name,
    semantic_type: 'Package',
    is_file: false,
    is_folder: true,
    children: [],
    rules: [],
    relationships: [],
  };
}

function _treeFromPaths(paths: string[]): DirectoryRow[] {
  const roots: DirectoryRow[] = [];
  for (const path of paths) {
    const parts = path.split('/').filter(Boolean);
    let level = roots;
    let relative = '';
    for (let index = 0; index < parts.length; index += 1) {
      const name = parts[index];
      relative = relative ? `${relative}/${name}` : name;
      if (index === parts.length - 1) {
        continue;
      }
      let node = level.find((item) => item.name === name);
      if (!node) {
        node = _folderRow(name, relative);
        level.push(node);
      }
      level = node.children;
    }
  }
  return roots;
}

function _graphFromCache(cached: string, root: string): KnowledgeGraph {
  if (!existsSync(cached)) {
    throw new Error(`Knowledge graph is missing: ${cached}`);
  }
  let dto: KnowledgeGraphDto;
  try {
    dto = JSON.parse(readFileSync(cached, 'utf8')) as KnowledgeGraphDto;
  } catch (error) {
    const message = error instanceof Error ? error.message : 'invalid JSON';
    throw new Error(`Knowledge graph could not be read: ${cached}: ${message}`);
  }
  if (!Array.isArray(dto.practice_graphs)) {
    throw new Error(`Knowledge graph has no practice graphs: ${cached}`);
  }
  dto.folder = root;
  const graph = graphFromWorkspaceDto(dto);
  if (_graphIsEmpty(graph)) {
    throw new Error(`Knowledge graph has no nodes: ${cached}`);
  }
  return graph;
}

function _readSourceText(
  root: string,
  file: string,
  startLine: number,
  endLine: number,
): string {
  const rootPath = resolve(root);
  const target = resolve(rootPath, file);
  const fromRoot = relative(rootPath, target);
  if (!file || fromRoot.startsWith('..') || isAbsolute(fromRoot)) {
    throw new Error(`Source is outside the graph folder: ${file}`);
  }
  if (!existsSync(target) || !statSync(target).isFile()) {
    return '';
  }
  const lines = readFileSync(target, 'utf8').split(/\r?\n/);
  const start = Math.max(1, startLine);
  const end = Math.max(start, endLine);
  return lines.slice(start - 1, end).join('\n');
}

function graphFromWorkspaceDto(dto: KnowledgeGraphDto): KnowledgeGraph {
  return KnowledgeGraph.fromDto(dto);
}

function httpPresent(presented: ReturnType<KnowledgeGraph['present']>) {
  const folder = typeof presented.folder === 'string' ? presented.folder : '';
  return { ...presented, listed_nodes: [], rule_catalog: _rulesFromGuidance(folder) };
}

const guidanceRules = new Map<string, { slug: string; practice: string; fidelity: string; applies_to: string[] }[]>();

function _rulesFromGuidance(folder: string) {
  const key = folder || '*';
  const cached = guidanceRules.get(key);
  if (cached) {
    return cached;
  }
  const repo = _repoRoot();
  const result = spawnSync(
    _python(),
    [
      '-c',
      'import json,sys; from harness.knowledge_graph.model.knowledge_graph_node import rules_from_guidance; print(json.dumps(rules_from_guidance(sys.argv[1] or None)))',
      folder,
    ],
    {
      cwd: repo,
      env: _pythonEnv(),
      encoding: 'utf8',
      maxBuffer: 16 * 1024 * 1024,
    },
  );
  if (result.status !== 0) {
    console.error(result.stderr || result.stdout || 'guidance rules failed');
    return [];
  }
  const line = (result.stdout || '').trim().split('\n').filter(Boolean).at(-1) || '[]';
  const rules = JSON.parse(line) as { slug: string; practice: string; fidelity: string; applies_to: string[] }[];
  guidanceRules.set(key, rules);
  return rules;
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
    ruleSources: _stringList(query.rule_source),
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
