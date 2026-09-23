import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';
import type { KnowledgeGraphDto, NodeDto, SourceRangeDto } from './knowledge-graph';
import { SKIP_DIR } from './workspace';

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

export function overlayWorkspaceTree(dto: KnowledgeGraphDto): KnowledgeGraphDto {
  const root = dto.folder;
  if (!root || !existsSync(root) || !statSync(root).isDirectory()) {
    return dto;
  }
  const folders = collectRelativeFolders(root);
  addFolderPackages(dto, folders);
  attachClassSources(dto, indexClassFiles(root));
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

function indexClassFiles(root: string): Map<string, SourceRangeDto[]> {
  const found = new Map<string, SourceRangeDto[]>();
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
      const full = join(root, child);
      let info;
      try {
        info = statSync(full);
      } catch {
        continue;
      }
      if (info.isDirectory()) {
        walk(child);
        continue;
      }
      if (!/\.(py|ts|tsx|js|jsx)$/.test(name) || name.endsWith('.d.ts')) {
        continue;
      }
      let text = '';
      try {
        text = readFileSync(full, 'utf8');
      } catch {
        continue;
      }
      const file = child.replaceAll('\\', '/');
      for (const [index, line] of text.split('\n').entries()) {
        const matched = /^(?:export\s+(?:default\s+)?)?class\s+([A-Za-z_]\w*)/.exec(
          line,
        );
        if (!matched) {
          continue;
        }
        const slug = matched[1];
        const hits = found.get(slug) ?? [];
        hits.push({ file, start_line: index + 1, end_line: index + 1, text: line });
        found.set(slug, hits);
      }
    }
  };
  walk('');
  return found;
}

function attachClassSources(
  dto: KnowledgeGraphDto,
  filesByClass: Map<string, SourceRangeDto[]>,
) {
  const nodes = dto.practice_graphs.flatMap((graph) => graph.nodes);
  const byId = new Map(nodes.map((node) => [node.node_id, node]));
  const edges = dto.practice_graphs.flatMap((graph) => graph.relationships);
  for (const node of nodes) {
    if (node.semantic_type !== 'OoadClass' || node.source?.file) {
      continue;
    }
    const hits = filesByClass.get(node.name);
    if (!hits || hits.length === 0) {
      continue;
    }
    const home = moduleFolder(node, byId, edges);
    node.source = pickClassFile(hits, home);
  }
}

function moduleFolder(
  node: NodeDto,
  byId: Map<string, NodeDto>,
  edges: Array<{ kind: string; from_id: string; to_id: string }>,
): string {
  for (const edge of edges) {
    const otherId =
      edge.from_id === node.node_id
        ? edge.to_id
        : edge.to_id === node.node_id
          ? edge.from_id
          : '';
    if (!otherId) {
      continue;
    }
    if (edge.kind !== 'owns' && edge.kind !== 'belongsTo') {
      continue;
    }
    const other = byId.get(otherId);
    if (other?.semantic_type !== 'Module' && other?.semantic_type !== 'Package') {
      continue;
    }
    return (other.properties?.folder || other.name.replaceAll('.', '/')).replaceAll(
      '\\',
      '/',
    );
  }
  return '';
}

function pickClassFile(hits: SourceRangeDto[], home: string): SourceRangeDto {
  const underHome = home
    ? hits.filter(
        (hit) => hit.file === home || hit.file.startsWith(`${home}/`),
      )
    : hits;
  const pool = underHome.length > 0 ? underHome : hits;
  return [...pool].sort((left, right) => right.file.length - left.file.length)[0];
}
