import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';
import type { KnowledgeGraphDto, NodeDto, SourceRangeDto } from './knowledge-graph';
import {
  definitionsInFile,
  pythonBlockEnd,
  SKIP_DIR,
  type SourceDefinition,
  type WorkspaceFile,
} from './workspace';

const SKIP_FOLDER = new Set([
  ...SKIP_DIR,
  '.context',
  '.cursor',
  '.vscode',
  '.github',
  'htmlcov',
  'examples',
  '__pycache__',
  '.venv',
  'dist',
  'coverage',
]);

const definitionCatalogs = new Map<string, SourceDefinition[]>();

export function overlayWorkspaceTree(dto: KnowledgeGraphDto): KnowledgeGraphDto {
  const root = dto.folder;
  if (!root || !existsSync(root) || !statSync(root).isDirectory()) {
    return dto;
  }
  const folders = collectRelativeFolders(root);
  addFolderPackages(dto, folders);
  fillSourceBodies(dto, root);
  return dto;
}

function collectRelativeFolders(root: string): string[] {
  const folders: string[] = [];
  const walk = (relative: string) => {
    const current = relative ? join(root, relative) : root;
    let entries: string[] = [];
    try {
      entries = readdirSync(current);
    } catch {
      return;
    }
    for (const name of entries) {
      if (SKIP_FOLDER.has(name) || name.startsWith('.')) {
        continue;
      }
      const child = relative ? `${relative}/${name}` : name;
      try {
        if (!statSync(join(root, child)).isDirectory()) {
          continue;
        }
      } catch {
        continue;
      }
      folders.push(child.replaceAll('\\', '/'));
      walk(child);
    }
  };
  walk('');
  return folders;
}

function addFolderPackages(dto: KnowledgeGraphDto, folders: string[]) {
  const seen = new Set<string>();
  for (const graph of dto.practice_graphs) {
    for (const node of graph.nodes) {
      if (node.semantic_type !== 'Module' && node.semantic_type !== 'Package') {
        continue;
      }
      const folder = (node.properties?.folder || '').replaceAll('\\', '/');
      if (folder) {
        seen.add(folder);
      }
    }
  }
  const added: NodeDto[] = [];
  for (const path of folders) {
    if (seen.has(path)) {
      continue;
    }
    seen.add(path);
    added.push({
      node_id: `pkg:${path}`,
      name: path.split('/').pop() ?? path,
      practice: '',
      fidelity: null,
      semantic_type: 'Package',
      properties: { folder: path },
      applicable_rules: [],
      violations: [],
      source: null,
    });
  }
  if (added.length === 0) {
    return;
  }
  const workspace = dto.practice_graphs.find(
    (graph) => graph.id === 'practice:workspace',
  );
  if (workspace) {
    workspace.nodes.push(...added);
    return;
  }
  dto.practice_graphs.unshift({
    id: 'practice:workspace',
    name: 'workspace',
    nodes: added,
    relationships: [],
  });
}

function fillSourceBodies(dto: KnowledgeGraphDto, root: string) {
  const catalog = indexDefinitions(root);
  const owners = ownership(dto);
  for (const graph of dto.practice_graphs) {
    for (const node of graph.nodes) {
      if (node.semantic_type !== 'OoadClass') {
        continue;
      }
      node.source = resolveBody(root, node, catalog, owners, null);
    }
  }
  for (const graph of dto.practice_graphs) {
    for (const node of graph.nodes) {
      if (node.semantic_type !== 'Operation') {
        continue;
      }
      const ownerClass = owners.classOf.get(node.node_id);
      const classFile = ownerClass
        ? owners.nodeById.get(ownerClass)?.source?.file ?? null
        : null;
      node.source = resolveBody(
        root,
        node,
        catalog,
        owners,
        classFile || node.source?.file || null,
      );
    }
  }
}

function ownership(dto: KnowledgeGraphDto): {
  nodeById: Map<string, NodeDto>;
  moduleFolder: Map<string, string>;
  classOf: Map<string, string>;
} {
  const nodeById = new Map<string, NodeDto>();
  for (const graph of dto.practice_graphs) {
    for (const node of graph.nodes) {
      nodeById.set(node.node_id, node);
    }
  }
  const moduleFolder = new Map<string, string>();
  const classOf = new Map<string, string>();
  for (const graph of dto.practice_graphs) {
    for (const edge of graph.relationships) {
      const parentId = edge.kind === 'owns' ? edge.from_id : edge.to_id;
      const childId = edge.kind === 'owns' ? edge.to_id : edge.from_id;
      if (edge.kind !== 'owns' && edge.kind !== 'belongsTo') {
        continue;
      }
      const parent = nodeById.get(parentId);
      if (!parent) {
        continue;
      }
      if (parent.semantic_type === 'OoadClass') {
        classOf.set(childId, parentId);
      }
      const folder =
        parent.properties?.folder ||
        (parent.semantic_type === 'Module' || parent.semantic_type === 'Package'
          ? parent.name.replaceAll('.', '/')
          : '');
      if (folder) {
        moduleFolder.set(childId, folder.replaceAll('\\', '/'));
      }
    }
  }
  for (const [childId, classId] of classOf) {
    const classFolder = moduleFolder.get(classId);
    if (classFolder && !moduleFolder.has(childId)) {
      moduleFolder.set(childId, classFolder);
    }
  }
  return { nodeById, moduleFolder, classOf };
}

function indexDefinitions(root: string): SourceDefinition[] {
  const cached = definitionCatalogs.get(root);
  if (cached) {
    return cached;
  }
  const found: SourceDefinition[] = [];
  for (const file of collectSourceFiles(root, '')) {
    found.push(...definitionsInFile(file));
  }
  definitionCatalogs.set(root, found);
  return found;
}

function collectSourceFiles(root: string, relative: string): WorkspaceFile[] {
  const files: WorkspaceFile[] = [];
  const current = relative ? join(root, relative) : root;
  let entries: string[] = [];
  try {
    entries = readdirSync(current);
  } catch {
    return files;
  }
  for (const name of entries) {
    if (SKIP_FOLDER.has(name) || name.startsWith('.')) {
      continue;
    }
    const child = relative ? `${relative}/${name}` : name;
    const full = join(root, child);
    let info;
    try {
      info = statSync(full);
    } catch {
      continue;
    }
    if (info.isDirectory()) {
      files.push(...collectSourceFiles(root, child));
      continue;
    }
    if (!/\.(py|ts|tsx|js|jsx)$/.test(name) || name.endsWith('.d.ts')) {
      continue;
    }
    try {
      files.push({
        relativePath: child.replaceAll('\\', '/'),
        text: readFileSync(full, 'utf8'),
      });
    } catch {
      continue;
    }
  }
  return files;
}

function resolveBody(
  root: string,
  node: NodeDto,
  catalog: SourceDefinition[],
  owners: { moduleFolder: Map<string, string> },
  preferFile: string | null,
): SourceRangeDto | null {
  const kind = node.semantic_type === 'OoadClass' ? 'OoadClass' : 'Operation';
  const folder = owners.moduleFolder.get(node.node_id) ?? '';
  const hit = pickDefinition(
    catalog,
    kind,
    node.name,
    folder,
    preferFile,
    node.source?.start_line ?? 0,
  );
  if (hit) {
    return expandSource(root, hit.source, node.name);
  }
  if (node.source?.file && node.source.start_line >= 1) {
    return expandSource(root, node.source, node.name);
  }
  return node.source;
}

function pickDefinition(
  catalog: SourceDefinition[],
  kind: 'OoadClass' | 'Operation',
  name: string,
  folder: string,
  preferFile: string | null,
  hintLine = 0,
): SourceDefinition | null {
  const hits = catalog.filter(
    (entry) => entry.semantic_type === kind && entry.name === name,
  );
  if (hits.length === 0) {
    return null;
  }
  const scored = hits.map((entry) => {
    let score = 0;
    const file = entry.source.file.replaceAll('\\', '/');
    if (preferFile && file === preferFile.replaceAll('\\', '/')) {
      score += 100;
    }
    if (folder && (file === folder || file.startsWith(`${folder}/`))) {
      score += 50;
    }
    const base = file.split('/').pop() ?? '';
    if (base.toLowerCase().includes(name.toLowerCase())) {
      score += 10;
    }
    if (hintLine > 0) {
      const start = entry.source.start_line;
      const end = entry.source.end_line || start;
      if (start <= hintLine && hintLine <= end) {
        score += 200;
      } else {
        score += Math.max(0, 40 - Math.abs(start - hintLine));
      }
    }
    return { entry, score };
  });
  scored.sort((left, right) => right.score - left.score);
  return scored[0]?.entry ?? null;
}

function expandSource(
  root: string,
  source: SourceRangeDto,
  expectedName?: string,
): SourceRangeDto {
  const full = join(root, source.file);
  if (!existsSync(full)) {
    return source;
  }
  let text = '';
  try {
    text = readFileSync(full, 'utf8');
  } catch {
    return source;
  }
  const lines = text.split(/\r?\n/);
  let start = Math.max(source.start_line, 1);
  if (expectedName) {
    const named = defLineIndex(lines, expectedName, start);
    if (named >= 0) {
      start = named + 1;
    }
  }
  if (start > lines.length) {
    return source;
  }
  const header = lines[start - 1] ?? '';
  const onHeader = /(?:async\s+)?(?:class|def)\b/.test(header) || /\{/.test(header);
  let end = start;
  if (source.file.endsWith('.py')) {
    end = pythonBlockEnd(lines, start - 1) + 1;
  } else if (/\.(ts|tsx|js|jsx)$/.test(source.file)) {
    end = braceBlockEnd(lines, start - 1) + 1;
  } else {
    end = Math.max(source.end_line || start, start);
  }
  if (!onHeader && !expectedName) {
    end = Math.max(end, source.end_line || start);
  }
  end = Math.min(end, lines.length);
  return {
    ...source,
    start_line: start,
    end_line: end,
    text: lines.slice(start - 1, end).join('\n'),
  };
}

function defLineIndex(lines: string[], name: string, hintLine: number): number {
  const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const python = new RegExp(
    `^(?:\\s*)(?:async\\s+)?def\\s+${escaped}\\s*\\(`,
  );
  const klass = new RegExp(`^(?:\\s*)class\\s+${escaped}\\b`);
  const script = new RegExp(
    `(?:(?:export|public|private|protected|static|async)\\s+)*${escaped}\\s*\\(`,
  );
  const matches: number[] = [];
  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    if (python.test(line) || klass.test(line) || script.test(line)) {
      matches.push(index);
    }
  }
  if (matches.length === 0) {
    return -1;
  }
  const hint = Math.max(hintLine - 1, 0);
  return matches.reduce((best, index) =>
    Math.abs(index - hint) < Math.abs(best - hint) ? index : best,
  );
}

function braceBlockEnd(lines: string[], startIndex: number): number {
  let depth = 0;
  let seen = false;
  for (let index = startIndex; index < lines.length; index += 1) {
    for (const ch of lines[index]) {
      if (ch === '{') {
        depth += 1;
        seen = true;
      } else if (ch === '}') {
        depth -= 1;
        if (seen && depth === 0) {
          return index;
        }
      }
    }
  }
  return startIndex;
}
