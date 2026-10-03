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
} from '../../../legacy/app/packages/explore-knowledge-graph/knowledge-graph/knowledge-graph';
import { KnowledgeGraphServer } from './knowledge-graph/knowledge-graph-server';
import { definitionsInFile,
  knowledgeGraphFromWorkspace,
  resolveNamedFolder,
  scanSourceFiles,
  type WorkspaceFile,
} from '../../../legacy/app/packages/explore-knowledge-graph/knowledge-graph/workspace';
import { taggedPractice, stepLinks, databaseBuildRequired } from './knowledge-graph/knowledge-graph';

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
    const root = _resolvePickedFolder(folder);
    if (_isDir(root)) {
      _writeLastScanRoot(root);
    }
    const graph =
      uploaded.length > 0
        ? knowledgeGraphFromWorkspace(root, uploaded, crypto.randomUUID())
        : _fromPracticeHierarchyCli(root, false);
    const nested = _nestDiskFolders(graph, root);
    const specified = _attachStorySpecification(nested, root);
    const coded = _attachClasses(specified, root);
    const linked = _linkStepMembers(coded, root);
    const tagged = _retagPractices(linked);
    return repo.create({
      folder: root,
      practiceGraphs: tagged.toDto().practice_graphs,
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
    const model = new KnowledgeGraphServer(null, null, null, null);
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
      const files = Array.isArray(req.body.files) ? req.body.files : undefined;
      const graph = await KnowledgeGraphsServer.selectFolder(
        String(req.body.folder ?? ''),
        repo,
        files,
        Boolean(req.body.force),
      );
      const presented = httpPresent(graph.present());
      if (presented.folder && _isDir(presented.folder)) {
        presented.listed_tree = _completeDirectory(
          presented.listed_tree ?? [],
          presented.folder,
        );
      }
      res.status(201).json(presented);
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
  const script = join(repo, 'harness', 'knowledge_graph', 'legacy', 'database_cli.py');
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
    'legacy',
    'write_practice_hierarchy.py',
  );
  const pythonPath = _pythonEnv();
  const args = [script, '--json'];
  if (!fromScratch) {
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
  _dropSourceText(dto);
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

function _fileRow(name: string, relative: string): DirectoryRow {
  return {
    node_id: `file:${relative}`,
    name,
    semantic_type: 'File',
    is_file: true,
    is_folder: false,
    children: [],
    rules: [],
    relationships: [],
    source: { file: relative, start_line: 1, end_line: 1, text: '' },
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

function _completeDirectory(listed: any[], root: string): any[] {
  return _mergeDirectory(listed, root, '');
}

function _mergeDirectory(listed: any[], root: string, parent: string): any[] {
  const dir = parent ? join(root, parent) : root;
  if (!_isDir(dir)) {
    return listed;
  }
  const rows = listed.map((row) => ({ ...row, children: row.children ?? [] }));
  const byName = new Map(rows.map((row) => [row.name, row]));
  let names: string[] = [];
  try {
    names = readdirSync(dir);
  } catch {
    return rows;
  }
  for (const name of names) {
    if (_skipDiskName(name)) {
      continue;
    }
    const relative = parent ? `${parent}/${name}` : name;
    const abs = join(root, relative);
    let isDir = false;
    try {
      isDir = statSync(abs).isDirectory();
    } catch {
      continue;
    }
    if (!isDir) {
      continue;
    }
    let row = byName.get(name);
    if (!row) {
      row = _folderRow(name, relative);
      rows.push(row);
      byName.set(name, row);
    }
    row.is_folder = true;
    row.children = _mergeDirectory(row.children ?? [], root, relative);
  }
  return rows;
}

function _linkStepMembers(graph: KnowledgeGraph, root: string): KnowledgeGraph {
  const dto = graph.toDto();
  const nodes = dto.practice_graphs.flatMap((practice) => practice.nodes);
  const classIds = new Map<string, string>();
  const operations: { id: string; name: string; owner: string }[] = [];
  for (const practice of dto.practice_graphs) {
    const classes = new Map(
      practice.nodes
        .filter((node) => node.semantic_type === 'OoadClass')
        .map((node) => [node.node_id, node.name]),
    );
    for (const [id, name] of classes) {
      if (!classIds.has(name)) {
        classIds.set(name, id);
      }
    }
    for (const edge of practice.relationships) {
      if (edge.kind !== 'owns') {
        continue;
      }
      const owner = classes.get(edge.from_id);
      const child = practice.nodes.find((node) => node.node_id === edge.to_id);
      if (!owner || child?.semantic_type !== 'Operation') {
        continue;
      }
      operations.push({ id: child.node_id, name: child.name, owner });
    }
  }
  const examples = _exampleExports(root);
  for (const practice of dto.practice_graphs) {
    for (const step of [...practice.nodes]) {
      if (step.semantic_type !== 'Step' || !step.source?.file) {
        continue;
      }
      const text = _sourceSlice(root, step.source.file, step.source.start_line, step.source.end_line);
      if (text) {
        step.source = { ...step.source, text };
      }
      const linked = stepLinks(text, operations, examples, [...classIds.keys()]);
      for (const target of linked.invokes) {
        _relate(practice, 'invokes', step.node_id, target);
      }
      for (const example of linked.examples) {
        const known = examples.find((item) => item.name === example.name);
        const exampleId = `stories:Example:${step.node_id}:${example.name}`;
        if (!practice.nodes.some((node) => node.node_id === exampleId)) {
          practice.nodes.push({
            node_id: exampleId,
            name: example.name,
            practice: 'stories',
            fidelity: 'scenarios',
            semantic_type: 'Example',
            properties: { folder: String(step.properties?.folder ?? '') },
            applicable_rules: [],
            violations: [],
            source: {
              file: known?.file ?? step.source.file,
              start_line: known?.line ?? step.source.start_line,
              end_line: known?.end ?? step.source.start_line,
              text: known?.text ?? example.name,
            },
          });
          practice.relationships.push({ kind: 'owns', from_id: step.node_id, to_id: exampleId });
        }
        for (const className of example.classes) {
          const classId = classIds.get(className);
          if (classId) {
            _relate(practice, 'demonstrates', exampleId, classId);
          }
        }
      }
      for (const className of linked.expected) {
        const classId = classIds.get(className);
        if (classId) {
          _relate(practice, 'expected', step.node_id, classId);
        }
      }
    }
  }
  return KnowledgeGraph.fromDto({ ...dto, folder: graph.folder });
}

function _relate(
  practice: KnowledgeGraphDto['practice_graphs'][number],
  kind: string,
  fromId: string,
  toId: string,
): void {
  if (
    practice.relationships.some(
      (edge) => edge.kind === kind && edge.from_id === fromId && edge.to_id === toId,
    )
  ) {
    return;
  }
  practice.relationships.push({ kind, from_id: fromId, to_id: toId });
}

function _exampleExports(root: string): { name: string; classes: string[]; file: string; line: number; end: number; text: string }[] {
  const found: { name: string; classes: string[]; file: string; line: number; end: number; text: string }[] = [];
  const tests = join(root, 'tests');
  if (!_isDir(tests)) {
    return found;
  }
  const visit = (dir: string) => {
    for (const name of readdirSync(dir)) {
      if (name === 'node_modules' || name.startsWith('.')) {
        continue;
      }
      const abs = join(dir, name);
      if (statSync(abs).isDirectory()) {
        visit(abs);
        continue;
      }
      if (!name.endsWith('.examples.ts')) {
        continue;
      }
      const text = readFileSync(abs, 'utf8');
      const file = relative(root, abs).replaceAll('\\', '/');
      const matches = [...text.matchAll(/export\s+function\s+([A-Za-z_][A-Za-z0-9_]*)/g)];
      matches.forEach((match, index) => {
        const next = matches[index + 1]?.index ?? text.length;
        const local = text.slice(match.index ?? 0, next);
        const brace = local.indexOf('{');
        if (brace < 0) {
          return;
        }
        const openAt = (match.index ?? 0) + brace;
        const line = text.slice(0, match.index ?? 0).split(/\r?\n/).length;
        const end = _balancedEnd(text, openAt, '{', '}');
        const body = _lineSlice(text, line, end);
        const returned = body.match(/\)\s*:\s*([A-Za-z_][A-Za-z0-9_]*)/)?.[1] ?? '';
        const constructed = [...body.matchAll(/\bnew\s+([A-Z][A-Za-z0-9_]*)/g)].map((item) => item[1]);
        const classes = [...new Set([returned, ...constructed].filter((item) => /^[A-Z]/.test(item)))];
        found.push({ name: match[1], classes, file, line, end, text: body });
      });
    }
  };
  visit(tests);
  return found;
}

function _sourceSlice(root: string, file: string, start: number, end: number): string {
  const full = join(root, file);
  if (!existsSync(full)) {
    return '';
  }
  const lines = readFileSync(full, 'utf8').split(/\r?\n/);
  const from = Math.max(0, start - 1);
  const to = Math.max(from, end);
  return lines.slice(from, to).join('\n');
}

function _retagPractices(graph: KnowledgeGraph): KnowledgeGraph {
  const dto = graph.toDto();
  for (const practice of dto.practice_graphs) {
    for (const node of practice.nodes) {
      node.practice = taggedPractice(node.semantic_type, node.practice);
      const folder = String(node.properties?.folder ?? '').replaceAll('\\', '/');
      if (
        (node.semantic_type === 'Module' || node.semantic_type === 'Package') &&
        (folder === 'tests' || folder.startsWith('tests/'))
      ) {
        node.practice = 'stories';
      }
    }
  }
  return KnowledgeGraph.fromDto({ ...dto, folder: graph.folder });
}

function _nestDiskFolders(graph: KnowledgeGraph, root: string): KnowledgeGraph {
  if (!root || !existsSync(root)) {
    return graph;
  }
  const dto = graph.toDto();
  const workspace =
    dto.practice_graphs.find((item) => item.id === 'practice:workspace') ??
    dto.practice_graphs[0];
  if (!workspace) {
    return graph;
  }
  const byPath = new Map<string, string>();
  for (const practice of dto.practice_graphs) {
    for (const node of practice.nodes) {
      if (node.semantic_type !== 'Package' && node.semantic_type !== 'Module') {
        continue;
      }
      const folder = String(node.properties?.folder ?? '').replaceAll('\\', '/');
      if (folder) {
        byPath.set(folder, node.node_id);
      }
    }
  }
  const seeds = new Set(byPath.keys());
  _addTopLevelFolders(root, byPath, workspace.nodes);
  for (const seed of seeds) {
    _addDiskFolders(root, seed, byPath, workspace.nodes);
  }
  for (const path of [...byPath.keys()]) {
    if (!path.includes('/')) {
      _addDiskFolders(root, path, byPath, workspace.nodes);
    }
  }
  const seen = new Set(
    dto.practice_graphs.flatMap((practice) =>
      practice.relationships.map((edge) => `${edge.from_id}\0${edge.to_id}`),
    ),
  );
  for (const [path, nodeId] of byPath) {
    const split = path.lastIndexOf('/');
    if (split <= 0) {
      continue;
    }
    const parentId = byPath.get(path.slice(0, split));
    if (!parentId) {
      continue;
    }
    const key = `${parentId}\0${nodeId}`;
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    workspace.relationships.push({ kind: 'owns', from_id: parentId, to_id: nodeId });
  }
  return KnowledgeGraph.fromDto(dto);
}

function _addTopLevelFolders(
  root: string,
  byPath: Map<string, string>,
  nodes: KnowledgeGraphDto['practice_graphs'][number]['nodes'],
): void {
  let names: string[] = [];
  try {
    names = readdirSync(root);
  } catch {
    return;
  }
  for (const name of names) {
    if (!name || name.startsWith('.') || DISK_SKIP.has(name)) {
      continue;
    }
    let info;
    try {
      info = statSync(join(root, name));
    } catch {
      continue;
    }
    if (!info.isDirectory() || byPath.has(name)) {
      continue;
    }
    const nodeId = `pkg:${name}`;
    byPath.set(name, nodeId);
    nodes.push({
      node_id: nodeId,
      name,
      practice: '',
      fidelity: null,
      semantic_type: 'Package',
      properties: { folder: name },
      applicable_rules: [],
      violations: [],
      source: null,
    });
  }
}

function _addDiskFolders(
  root: string,
  folder: string,
  byPath: Map<string, string>,
  nodes: KnowledgeGraphDto['practice_graphs'][number]['nodes'],
): void {
  let names: string[] = [];
  try {
    names = readdirSync(join(root, folder));
  } catch {
    return;
  }
  for (const name of names) {
    if (!name || name.startsWith('.') || DISK_SKIP.has(name)) {
      continue;
    }
    const child = `${folder}/${name}`.replaceAll('\\', '/');
    let info;
    try {
      info = statSync(join(root, child));
    } catch {
      continue;
    }
    if (!info.isDirectory()) {
      continue;
    }
    if (!byPath.has(child)) {
      const nodeId = `pkg:${child}`;
      byPath.set(child, nodeId);
      nodes.push({
        node_id: nodeId,
        name,
        practice: '',
        fidelity: null,
        semantic_type: 'Package',
        properties: { folder: child },
        applicable_rules: [],
        violations: [],
        source: null,
      });
    }
    _addDiskFolders(root, child, byPath, nodes);
  }
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
  _dropSourceText(dto);
  const graph = graphFromWorkspaceDto(dto);
  if (_graphIsEmpty(graph)) {
    throw new Error(`Knowledge graph has no nodes: ${cached}`);
  }
  return graph;
}

function _dropSourceText(dto: KnowledgeGraphDto): void {
  for (const practice of dto.practice_graphs) {
    for (const node of practice.nodes) {
      if (node.source?.text) {
        node.source = { ...node.source, text: '' };
      }
    }
  }
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

function _attachStorySpecification(graph: KnowledgeGraph, root: string): KnowledgeGraph {
  const dto = graph.toDto();
  const tests = join(root, 'tests');
  if (!_isDir(tests)) {
    return graph;
  }
  const stories = _ensurePractice(dto, 'stories');
  for (const file of _storyFiles(tests)) {
    for (const parsed of _parseStoryFile(root, file)) {
      const matches = stories.nodes.filter(
        (node) => node.semantic_type === 'Story' && node.name === parsed.name,
      );
      const storyId = matches[0]?.node_id ?? _addStory(stories, parsed);
      const story = stories.nodes.find((node) => node.node_id === storyId);
      if (story) {
        const shared = parsed.file.endsWith('.story.shared.ts');
        if (shared || !story.source?.file) {
          story.source = {
            file: parsed.file,
            start_line: parsed.line,
            end_line: parsed.endLine,
            text: '',
          };
        }
        story.properties = { ...(story.properties ?? {}), folder: parsed.folder };
      }
      if (!storyId) {
        continue;
      }
      for (const background of parsed.backgrounds) {
        _own(stories, storyId, 'Background', 'Background', parsed.file, background.line, background.endLine, background.steps, parsed.folder);
      }
      for (const scenario of parsed.scenarios) {
        _own(stories, storyId, 'Scenario', scenario.name, parsed.file, scenario.line, scenario.endLine, scenario.steps, parsed.folder);
      }
      for (const example of parsed.examples) {
        _own(stories, storyId, 'Example', example.name, example.file, example.line, example.line, [], parsed.folder);
      }
    }
  }
  _fillEpicSource(stories, root);
  return graphFromWorkspaceDto({ ...dto, folder: root });
}

function _ensurePractice(
  dto: KnowledgeGraphDto,
  name: string,
): KnowledgeGraphDto['practice_graphs'][number] {
  const existing = dto.practice_graphs.find((item) => item.name === name);
  if (existing) {
    return existing;
  }
  const created = {
    id: `practice:${name}`,
    name,
    nodes: [],
    relationships: [],
  };
  dto.practice_graphs.push(created);
  return created;
}

function _addStory(
  stories: KnowledgeGraphDto['practice_graphs'][number],
  parsed: { name: string; file: string; line: number; endLine: number; folder: string },
): string {
  const nodeId = `stories:Story:${parsed.file}:${parsed.name}`;
  stories.nodes.push({
    node_id: nodeId,
    name: parsed.name,
    practice: 'stories',
    fidelity: 'scenarios',
    semantic_type: 'Story',
    properties: { folder: parsed.folder },
    applicable_rules: [],
    violations: [],
    source: {
      file: parsed.file,
      start_line: parsed.line,
      end_line: parsed.endLine,
      text: '',
    },
  });
  return nodeId;
}

function _own(
  stories: KnowledgeGraphDto['practice_graphs'][number],
  parentId: string,
  type: string,
  name: string,
  file: string,
  line: number,
  endLine: number,
  steps: { keyword: string; name: string; line: number; endLine: number }[],
  folder = '',
): string | null {
  const existing = stories.relationships.find(
    (edge) => edge.kind === 'owns' && edge.from_id === parentId && stories.nodes.some((node) => node.node_id === edge.to_id && node.name === name && node.semantic_type === type),
  );
  if (existing) {
    const current = stories.nodes.find((node) => node.node_id === existing.to_id);
    if (
      current?.source &&
      (file.endsWith('.story.shared.ts') || current.source.end_line <= current.source.start_line)
    ) {
      current.source = {
        ...current.source,
        file,
        start_line: line,
        end_line: Math.max(line, endLine),
        text: '',
      };
    }
    _ownSteps(stories, existing.to_id, steps, file, folder);
    return existing.to_id;
  }
  const nodeId = `stories:${type}:${parentId}:${line}:${name}`;
  stories.nodes.push({
    node_id: nodeId,
    name,
    practice: 'stories',
    fidelity: 'scenarios',
    semantic_type: type,
    properties: folder ? { folder } : {},
    applicable_rules: [],
    violations: [],
    source: { file, start_line: line, end_line: Math.max(line, endLine), text: '' },
  });
  stories.relationships.push({ kind: 'owns', from_id: parentId, to_id: nodeId });
  _ownSteps(stories, nodeId, steps, file, folder);
  return nodeId;
}

function _ownSteps(
  stories: KnowledgeGraphDto['practice_graphs'][number],
  nodeId: string,
  steps: { keyword: string; name: string; line: number; endLine: number }[],
  file: string,
  folder: string,
): void {
  let previous = 'given';
  for (const step of steps) {
    const keyword = step.keyword === 'and' ? previous : step.keyword;
    previous = keyword;
    const label = `${keyword[0].toUpperCase()}${keyword.slice(1)} ${step.name}`;
    _own(stories, nodeId, 'Step', label, file, step.line, step.endLine, [], folder);
  }
}

function _storyFiles(dir: string): string[] {
  const found: string[] = [];
  for (const name of readdirSync(dir)) {
    if (name === 'node_modules' || name.startsWith('.')) {
      continue;
    }
    const abs = join(dir, name);
    if (statSync(abs).isDirectory()) {
      found.push(..._storyFiles(abs));
    } else if (
      name.endsWith('.e2e.ts') ||
      name.endsWith('.story.playwright.ts') ||
      name.endsWith('.story.shared.ts')
    ) {
      found.push(abs);
    }
  }
  return found;
}

function _parseStoryFile(root: string, abs: string): {
  name: string;
  file: string;
  line: number;
  endLine: number;
  backgrounds: { line: number; endLine: number; steps: { keyword: string; name: string; line: number; endLine: number }[] }[];
  scenarios: { name: string; line: number; endLine: number; steps: { keyword: string; name: string; line: number; endLine: number }[] }[];
  examples: { name: string; file: string; line: number }[];
  epic: string;
  subEpic: string;
  epicFolder: string;
  folder: string;
}[] {
  const text = readFileSync(abs, 'utf8');
  const stories = [...text.matchAll(/(?:withStory|shareStory|story)\(\s*['"]([^'"]+)['"]/g)];
  if (stories.length === 0) {
    return [];
  }
  const file = relative(root, abs).replaceAll('\\', '/');
  const lines = text.split(/\r?\n/);
  const examples = _importedExamples(root, abs, text);
  const parts = file.split('/');
  const epic = parts.length > 2 ? parts[1] : 'tests';
  const subEpic = parts.length > 3 ? parts[2] : '';
  const folder = subEpic ? parts.slice(0, 3).join('/') : parts.slice(0, 2).join('/');
  return stories.map((story, storyIndex) => {
    const storyLine = text.slice(0, story.index ?? 0).split(/\r?\n/).length;
    const nextStart = stories[storyIndex + 1]?.index;
    const nextLine = nextStart == null ? lines.length + 1 : text.slice(0, nextStart).split(/\r?\n/).length;
    const backgrounds: { line: number; endLine: number; steps: { keyword: string; name: string; line: number; endLine: number }[] }[] = [];
    const scenarios: { name: string; line: number; endLine: number; steps: { keyword: string; name: string; line: number; endLine: number }[] }[] = [];
    let current: { steps: { keyword: string; name: string; line: number; endLine: number }[] } | null = null;
    for (let index = storyLine - 1; index < nextLine - 1 && index < lines.length; index += 1) {
      const line = lines[index];
      const background = line.match(/(?:withBackground|background)\s*\(/);
      const scenario = line.match(/(?:withScenario|scenario)\(\s*['"]([^'"]+)['"]/);
      const step = line.match(/(?:^|[^\w])(given|when|then|and)\(\s*['"]([^'"]+)['"]/i);
      if (background) {
        current = { steps: [] };
        backgrounds.push({ line: index + 1, endLine: index + 1, steps: current.steps });
        continue;
      }
      if (scenario) {
        current = { steps: [] };
        scenarios.push({ name: scenario[1], line: index + 1, endLine: index + 1, steps: current.steps });
        continue;
      }
      if (step && current) {
        current.steps.push({ keyword: step[1].toLowerCase(), name: step[2], line: index + 1, endLine: index + 1 });
      }
    }
    for (const background of backgrounds) {
      background.endLine = _blockEndLine(text, background.line);
      for (const step of background.steps) {
        step.endLine = _blockEndLine(text, step.line);
      }
    }
    for (const scenario of scenarios) {
      scenario.endLine = _blockEndLine(text, scenario.line);
      for (const step of scenario.steps) {
        step.endLine = _blockEndLine(text, step.line);
      }
    }
    return {
      name: story[1],
      file,
      line: storyLine,
      endLine: _blockEndLine(text, storyLine),
      epic,
      subEpic,
      epicFolder: parts.slice(0, 2).join('/'),
      folder,
      backgrounds,
      scenarios,
      examples: storyIndex === 0 ? examples : [],
    };
  });
}

function _blockEndLine(text: string, line: number): number {
  let offset = 0;
  let current = 1;
  while (current < line && offset < text.length) {
    if (text[offset] === '\n') {
      current += 1;
    }
    offset += 1;
  }
  let endAt = _openerEnd(text, offset);
  endAt = _chainEnd(text, endAt);
  return text.slice(0, Math.max(offset + 1, endAt)).split(/\r?\n/).length;
}

function _openerEnd(text: string, offset: number): number {
  const rest = text.slice(offset);
  const openParen = rest.indexOf('(');
  const openBrace = rest.indexOf('{');
  if (openParen >= 0 && (openBrace < 0 || openParen < openBrace)) {
    return _balancedEndIndex(text, offset + openParen, '(', ')');
  }
  if (openBrace >= 0) {
    return _balancedEndIndex(text, offset + openBrace, '{', '}');
  }
  return offset;
}

function _chainEnd(text: string, endAt: number): number {
  let cursor = endAt;
  while (cursor < text.length) {
    let look = cursor;
    while (look < text.length && /\s/.test(text[look])) {
      look += 1;
    }
    const call = /^\.[ \t]*[A-Za-z_][A-Za-z0-9_]*[ \t]*\(/.exec(text.slice(look));
    if (!call) {
      break;
    }
    const parenAt = look + call[0].lastIndexOf('(');
    cursor = _balancedEndIndex(text, parenAt, '(', ')');
  }
  return cursor;
}

function _balancedEnd(text: string, openAt: number, open: string, close: string): number {
  return text.slice(0, _balancedEndIndex(text, openAt, open, close)).split(/\r?\n/).length;
}

function _balancedEndIndex(text: string, openAt: number, open: string, close: string): number {
  let depth = 0;
  let quote = '';
  for (let index = openAt; index < text.length; index += 1) {
    const char = text[index];
    if (quote) {
      if (char === '\\') {
        index += 1;
        continue;
      }
      if (char === quote) {
        quote = '';
      }
      continue;
    }
    if (char === '"' || char === "'" || char === '`') {
      quote = char;
      continue;
    }
    if (char === open) {
      depth += 1;
    } else if (char === close) {
      depth -= 1;
      if (depth === 0) {
        return index + 1;
      }
    }
  }
  return text.length;
}

function _fillEpicSource(
  stories: KnowledgeGraphDto['practice_graphs'][number],
  root: string,
): void {
  const byId = new Map(stories.nodes.map((node) => [node.node_id, node]));
  const children = new Map<string, string[]>();
  for (const edge of stories.relationships) {
    if (edge.kind !== 'owns') {
      continue;
    }
    const list = children.get(edge.from_id) ?? [];
    list.push(edge.to_id);
    children.set(edge.from_id, list);
  }
  for (const epic of stories.nodes) {
    if (epic.semantic_type !== 'Epic') {
      continue;
    }
    const blocks: string[] = [];
    let file = '';
    const seen = new Set<string>();
    const walk = (id: string) => {
      for (const childId of children.get(id) ?? []) {
        if (seen.has(childId)) {
          continue;
        }
        seen.add(childId);
        const child = byId.get(childId);
        if (!child) {
          continue;
        }
        if (child.semantic_type === 'Story' && child.source?.file) {
          if (!file) {
            file = child.source.file;
          }
          const text = _readSourceText(
            root,
            child.source.file,
            child.source.start_line,
            child.source.end_line,
          );
          if (text.trim()) {
            blocks.push(text);
          }
        }
        if (child.semantic_type === 'Epic' || child.semantic_type === 'SubEpic') {
          walk(childId);
        }
      }
    };
    walk(epic.node_id);
    if (!blocks.length || !file) {
      continue;
    }
    const text = blocks.join('\n\n');
    epic.source = {
      file,
      start_line: 1,
      end_line: text.split(/\r?\n/).length,
      text,
    };
  }
}

function _attachClasses(graph: KnowledgeGraph, root: string): KnowledgeGraph {
  const dto = graph.toDto();
  if (!_isDir(root)) {
    return graph;
  }
  const engineering = _ensurePractice(dto, 'clean_engineering');
  const seen = new Set(engineering.nodes.map((node) => node.node_id));
  for (const abs of _codeFiles(root)) {
    const file = relative(root, abs).replaceAll('\\', '/');
    const text = readFileSync(abs, 'utf8');
    const workspace: WorkspaceFile = { relativePath: file, text };
    const classes: { id: string; start: number; end: number }[] = [];
    for (const found of definitionsInFile(workspace)) {
      if (found.semantic_type !== 'OoadClass') {
        continue;
      }
      const id = _addType(
        engineering,
        seen,
        file,
        'OoadClass',
        found.name,
        found.source.start_line,
        found.source.end_line,
        null,
        found.source.text ?? '',
      );
      if (id) {
        classes.push({ id, start: found.source.start_line, end: found.source.end_line });
      }
    }
    for (const match of text.matchAll(/export\s+interface\s+([A-Za-z_][A-Za-z0-9_]*)[^{]*\{/g)) {
      const at = match.index ?? 0;
      const start = text.slice(0, at).split(/\r?\n/).length;
      const end = _blockEndLine(text, start);
      const id = _addType(engineering, seen, file, 'OoadClass', match[1], start, end, null, _lineSlice(text, start, end));
      if (id) {
        classes.push({ id, start, end });
      }
    }
    for (const found of definitionsInFile(workspace)) {
      if (found.semantic_type === 'OoadClass') {
        continue;
      }
      const line = found.source.start_line;
      const owner = classes.find((item) => item.start <= line && line <= item.end);
      const body =
        found.semantic_type === 'Operation' || found.semantic_type === 'Property'
          ? _lineSlice(text, line, found.source.end_line)
          : '';
      _addType(
        engineering,
        seen,
        file,
        found.semantic_type,
        found.name,
        line,
        found.source.end_line,
        owner?.id ?? null,
        body,
      );
    }
  }
  _linkOperationCalls(dto);
  return graphFromWorkspaceDto({ ...dto, folder: root });
}

const CALL_RECEIVER_SKIP = new Set([
  'expect',
  'vi',
  'console',
  'Math',
  'JSON',
  'Object',
  'Promise',
  'Array',
  'describe',
  'it',
  'test',
  'beforeEach',
  'afterEach',
]);

function _lineSlice(text: string, start: number, end: number): string {
  const lines = text.split(/\r?\n/);
  const from = Math.max(0, start - 1);
  const to = Math.max(from, end);
  return lines.slice(from, to).join('\n');
}

function _linkOperationCalls(dto: KnowledgeGraphDto): void {
  const operations = new Map<string, string>();
  const ownerName = new Map<string, string>();
  for (const practice of dto.practice_graphs) {
    const classes = new Map(
      practice.nodes
        .filter((node) => node.semantic_type === 'OoadClass')
        .map((node) => [node.node_id, node.name]),
    );
    const nodes = new Map(practice.nodes.map((node) => [node.node_id, node]));
    for (const edge of practice.relationships) {
      if (edge.kind !== 'owns') {
        continue;
      }
      const className = classes.get(edge.from_id);
      const child = nodes.get(edge.to_id);
      if (!className || !child) {
        continue;
      }
      if (child.semantic_type !== 'Operation' && child.semantic_type !== 'Property') {
        continue;
      }
      operations.set(`${className.toLowerCase()}.${child.name}`, child.node_id);
      ownerName.set(child.node_id, className);
    }
  }
  const call = /\b([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\s*\(/g;
  for (const practice of dto.practice_graphs) {
    const nodes = new Map(practice.nodes.map((node) => [node.node_id, node]));
    for (const member of practice.nodes) {
      if (member.semantic_type !== 'Operation' && member.semantic_type !== 'Property') {
        continue;
      }
      const text = member.source?.text ?? '';
      if (!text) {
        continue;
      }
      const seen = new Set<string>();
      for (const match of text.matchAll(call)) {
        if (CALL_RECEIVER_SKIP.has(match[1])) {
          continue;
        }
        const receiver =
          match[1] === 'this' || match[1] === 'self'
            ? (ownerName.get(member.node_id) ?? '')
            : match[1];
        const target = operations.get(`${receiver.toLowerCase()}.${match[2]}`);
        if (!target || target === member.node_id || seen.has(target) || !nodes.has(target)) {
          continue;
        }
        seen.add(target);
        const linked = practice.relationships.some(
          (edge) => edge.kind === 'invokes' && edge.from_id === member.node_id && edge.to_id === target,
        );
        if (!linked) {
          practice.relationships.push({ kind: 'invokes', from_id: member.node_id, to_id: target });
        }
      }
    }
  }
}

function _addType(
  engineering: KnowledgeGraphDto['practice_graphs'][number],
  seen: Set<string>,
  file: string,
  type: string,
  name: string,
  start: number,
  end: number,
  ownerId: string | null,
  body = '',
): string | null {
  const nodeId = `ce:${type}:${file}:${name}:${start}`;
  if (seen.has(nodeId)) {
    return nodeId;
  }
  seen.add(nodeId);
  const folder = file.includes('/') ? file.slice(0, file.lastIndexOf('/')) : '';
  engineering.nodes.push({
    node_id: nodeId,
    name,
    practice: 'clean_engineering',
    fidelity: 'code',
    semantic_type: type,
    properties: folder ? { folder } : {},
    applicable_rules: [],
    violations: [],
    source: { file, start_line: start, end_line: Math.max(start, end), text: body },
  });
  const owner =
    ownerId ??
    engineering.nodes.find(
      (node) =>
        (node.semantic_type === 'Module' || node.semantic_type === 'Package') &&
        String(node.properties?.folder ?? '').replaceAll('\\', '/') === folder,
    )?.node_id;
  if (owner) {
    engineering.relationships.push({ kind: 'owns', from_id: owner, to_id: nodeId });
  }
  return nodeId;
}

function _codeFiles(dir: string, root = dir): string[] {
  const found: string[] = [];
  for (const name of readdirSync(dir)) {
    if (name === 'node_modules' || name === 'tests' || name === 'dist' || name === 'coverage' || name.startsWith('.')) {
      continue;
    }
    const abs = join(dir, name);
    if (statSync(abs).isDirectory()) {
      found.push(..._codeFiles(abs, root));
    } else if (/\.(ts|tsx)$/.test(name) && !name.endsWith('.d.ts')) {
      found.push(abs);
    }
  }
  return found;
}

function _importedExamples(
  root: string,
  storyFile: string,
  text: string,
): { name: string; file: string; line: number }[] {
  const found: { name: string; file: string; line: number }[] = [];
  const seen = new Set<string>();
  for (const match of text.matchAll(/from\s+['"]([^'"]+)['"]/g)) {
    const spec = match[1];
    if (!spec.includes('examples')) {
      continue;
    }
    const abs = join(dirname(storyFile), spec.endsWith('.ts') ? spec : `${spec}.ts`);
    if (!existsSync(abs) || seen.has(abs)) {
      continue;
    }
    seen.add(abs);
    const body = readFileSync(abs, 'utf8');
    const file = relative(root, abs).replaceAll('\\', '/');
    for (const exported of body.matchAll(/export (?:const|function) (\w+)/g)) {
      const at = exported.index ?? 0;
      found.push({
        name: exported[1],
        file,
        line: body.slice(0, at).split(/\r?\n/).length,
      });
    }
  }
  return found;
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
