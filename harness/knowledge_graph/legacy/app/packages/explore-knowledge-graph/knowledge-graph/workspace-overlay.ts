import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';
import {
  isAccessorSource,
  isClassKind,
  isComplexFieldType,
  KEEP_OPERATIONS_SMALL_FOCUSED,
  type KnowledgeGraphDto,
  type NodeDto,
  type SourceRangeDto,
} from './knowledge-graph';
import {
  definitionsInFile,
  isObjectLiteralKeyText,
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
  attachStepInvokes(dto, root);
  attachMemberInvokes(dto);
  attachComposition(dto, root);
  return dto;
}

function retagAccessors(dto: KnowledgeGraphDto) {
  for (const graph of dto.practice_graphs) {
    for (const node of graph.nodes) {
      if (node.semantic_type !== 'Operation' || !isAccessorSource(node.source?.text ?? '')) {
        continue;
      }
      node.semantic_type = 'Property';
      node.applicable_rules = (node.applicable_rules ?? []).filter(
        (slug) => slug !== KEEP_OPERATIONS_SMALL_FOCUSED,
      );
      node.violations = (node.violations ?? []).filter(
        (hit) => hit.rule_slug !== KEEP_OPERATIONS_SMALL_FOCUSED,
      );
    }
  }
}

function dropObjectLiteralKeyProperties(dto: KnowledgeGraphDto) {
  for (const graph of dto.practice_graphs) {
    const nodeById = new Map(graph.nodes.map((node) => [node.node_id, node]));
    const drop = new Set<string>();
    const owned = new Map<string, NodeDto[]>();
    for (const edge of graph.relationships) {
      if (edge.kind !== 'owns') {
        continue;
      }
      const child = nodeById.get(edge.to_id);
      if (child?.semantic_type !== 'Property') {
        continue;
      }
      const siblings = owned.get(edge.from_id) ?? [];
      siblings.push(child);
      owned.set(edge.from_id, siblings);
    }
    for (const siblings of owned.values()) {
      const keys = new Set<string>();
      for (const holder of siblings) {
        for (const name of objectFieldKeys(holder.source?.text ?? '')) {
          keys.add(name);
        }
      }
      for (const property of siblings) {
        if (keys.has(property.name) || isObjectLiteralKeyText(property.source?.text ?? '')) {
          drop.add(property.node_id);
        }
      }
    }
    if (drop.size === 0) {
      continue;
    }
    graph.nodes = graph.nodes.filter((node) => !drop.has(node.node_id));
    graph.relationships = graph.relationships.filter(
      (edge) => !drop.has(edge.from_id) && !drop.has(edge.to_id),
    );
  }
}

function objectFieldKeys(text: string): string[] {
  if (!/=\s*\{/.test(text)) {
    return [];
  }
  const keys: string[] = [];
  for (const match of text.matchAll(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:/gm)) {
    keys.push(match[1]);
  }
  return keys;
}

export function compositionByClass(markdown: string): Map<string, string[]> {
  const composed = new Map<string, string[]>();
  for (const part of markdown.split(/^### /m)) {
    const header = part.match(/^\*\*(.+?)\*\*/);
    if (!header) {
      continue;
    }
    const targets: string[] = [];
    for (const line of part.split('\n')) {
      if (!/<<\s*composition\s*>>/i.test(line)) {
        continue;
      }
      const typed = line.match(/:\s*([A-Za-z_][A-Za-z0-9_]*)/);
      if (typed) {
        targets.push(typed[1]);
      }
    }
    if (targets.length > 0) {
      composed.set(header[1].trim(), targets);
    }
  }
  return composed;
}

function attachRelatives(dto: KnowledgeGraphDto) {
  for (const graph of dto.practice_graphs) {
    const nodeById = new Map(graph.nodes.map((node) => [node.node_id, node]));
    const existing = new Set(graph.relationships.map((edge) => `${edge.kind}:${edge.from_id}:${edge.to_id}`));
    for (const edge of graph.relationships) {
      if (edge.kind !== 'owns') {
        continue;
      }
      const owner = nodeById.get(edge.from_id);
      const member = nodeById.get(edge.to_id);
      if (!owner || !member || !isClassKind(owner.semantic_type) || member.semantic_type !== 'Property') {
        continue;
      }
      if (!isComplexFieldType(member.source?.text ?? '')) {
        continue;
      }
      const key = `relative:${owner.node_id}:${member.node_id}`;
      if (existing.has(key)) {
        continue;
      }
      existing.add(key);
      graph.relationships.push({ kind: 'relative', from_id: owner.node_id, to_id: member.node_id });
    }
  }
}

function attachComposition(dto: KnowledgeGraphDto, root: string) {
  const model = join(root, 'domain', 'domain-model.md');
  let composed = new Map<string, string[]>();
  if (existsSync(model)) {
    try {
      composed = compositionByClass(readFileSync(model, 'utf8'));
    } catch {
      composed = new Map();
    }
  }
  for (const graph of dto.practice_graphs) {
    const classes = graph.nodes.filter((node) => isClassKind(node.semantic_type));
    const existing = new Set(graph.relationships.map((edge) => `${edge.kind}:${edge.from_id}:${edge.to_id}`));
    const link = (owner: NodeDto | undefined, targetName: string) => {
      if (!owner) {
        return;
      }
      const target = classNamed(classes, targetName, owner.source?.file);
      if (!target || target.node_id === owner.node_id) {
        return;
      }
      const key = `composition:${owner.node_id}:${target.node_id}`;
      if (existing.has(key)) {
        return;
      }
      existing.add(key);
      graph.relationships.push({ kind: 'composition', from_id: owner.node_id, to_id: target.node_id });
    };
    for (const [name, targets] of composed) {
      const owner = classNamed(classes, name);
      for (const targetName of targets) {
        link(owner, targetName);
      }
    }
    const nodeById = new Map(graph.nodes.map((node) => [node.node_id, node]));
    for (const edge of graph.relationships) {
      if (edge.kind !== 'owns') {
        continue;
      }
      const member = nodeById.get(edge.to_id);
      const owner = nodeById.get(edge.from_id);
      if (!member || member.semantic_type !== 'Property' || !owner || !isClassKind(owner.semantic_type)) {
        continue;
      }
      const text = member.source?.text ?? '';
      if (!/<<\s*composition\s*>>/i.test(text)) {
        continue;
      }
      const targetName = text.match(/:\s*([A-Za-z_][A-Za-z0-9_]*)/)?.[1];
      if (targetName) {
        link(owner, targetName);
      }
    }
  }
}

function classNamed(classes: NodeDto[], name: string, nearFile?: string): NodeDto | undefined {
  const matches = classes.filter((node) => node.name === name);
  if (nearFile) {
    const folder = nearFile.replaceAll('\\', '/').split('/').slice(0, -1).join('/');
    const nearby = matches.find((node) => (node.source?.file ?? '').replaceAll('\\', '/').startsWith(folder));
    if (nearby) {
      return nearby;
    }
  }
  return matches.find((node) => (node.source?.file ?? '').replaceAll('\\', '/').startsWith('domain/')) ?? matches[0];
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

const CALL_SKIP = new Set([
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

function attachStepInvokes(dto: KnowledgeGraphDto, root: string) {
  const operations = new Map<string, string>();
  for (const graph of dto.practice_graphs) {
    const classes = new Map(
      graph.nodes
        .filter((node) => node.semantic_type === 'OoadClass')
        .map((node) => [node.node_id, node]),
    );
    for (const edge of graph.relationships) {
      if (edge.kind !== 'owns') {
        continue;
      }
      const owner = classes.get(edge.from_id);
      const child = graph.nodes.find((node) => node.node_id === edge.to_id);
      if (!owner || !child || child.semantic_type !== 'Operation') {
        continue;
      }
      operations.set(`${owner.name.toLowerCase()}.${child.name}`, child.node_id);
    }
  }
  const call = /\b([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\s*\(/g;
  for (const graph of dto.practice_graphs) {
    for (const step of graph.nodes) {
      if (!isWhenStep(step)) {
        continue;
      }
      const seen = new Set<string>();
      for (const match of stepBody(root, step).matchAll(call)) {
        if (CALL_SKIP.has(match[1])) {
          continue;
        }
        const target = operations.get(`${match[1].toLowerCase()}.${match[2]}`);
        if (!target || seen.has(target)) {
          continue;
        }
        seen.add(target);
        const linked = graph.relationships.some(
          (edge) => edge.kind === 'invokes' && edge.from_id === step.node_id && edge.to_id === target,
        );
        if (linked) {
          continue;
        }
        graph.relationships.push({ kind: 'invokes', from_id: step.node_id, to_id: target });
      }
    }
  }
}

function attachMemberInvokes(dto: KnowledgeGraphDto) {
  const operations = new Map<string, string>();
  const properties = new Map<string, string>();
  const ownerName = new Map<string, string>();
  for (const graph of dto.practice_graphs) {
    const classes = new Map(
      graph.nodes
        .filter((node) => node.semantic_type === 'OoadClass')
        .map((node) => [node.node_id, node]),
    );
    for (const edge of graph.relationships) {
      if (edge.kind !== 'owns') {
        continue;
      }
      const owner = classes.get(edge.from_id);
      const child = graph.nodes.find((node) => node.node_id === edge.to_id);
      if (!owner || !child) {
        continue;
      }
      const key = `${owner.name.toLowerCase()}.${child.name}`;
      if (child.semantic_type === 'Operation') {
        operations.set(key, child.node_id);
      }
      if (child.semantic_type === 'Property') {
        properties.set(key, child.node_id);
      }
      ownerName.set(child.node_id, owner.name);
    }
  }
  const call = /\b([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\b/g;
  for (const graph of dto.practice_graphs) {
    for (const member of graph.nodes) {
      if (member.semantic_type !== 'Operation' && member.semantic_type !== 'Property') {
        continue;
      }
      const seen = new Set<string>();
      for (const match of (member.source?.text ?? '').matchAll(call)) {
        if (CALL_SKIP.has(match[1])) {
          continue;
        }
        const receiver =
          match[1] === 'this' || match[1] === 'self'
            ? (ownerName.get(member.node_id) ?? match[1])
            : match[1];
        const target =
          operations.get(`${receiver.toLowerCase()}.${match[2]}`) ??
          properties.get(`${receiver.toLowerCase()}.${match[2]}`);
        if (!target || target === member.node_id || seen.has(target)) {
          continue;
        }
        seen.add(target);
        const linked = graph.relationships.some(
          (edge) => edge.kind === 'invokes' && edge.from_id === member.node_id && edge.to_id === target,
        );
        if (linked) {
          continue;
        }
        graph.relationships.push({ kind: 'invokes', from_id: member.node_id, to_id: target });
      }
    }
  }
}

function isWhenStep(step: NodeDto): boolean {
  if (step.semantic_type !== 'Step') {
    return false;
  }
  const keyword = (step.keyword ?? '').toLowerCase();
  return keyword === 'when' || step.name.startsWith('When ');
}

function stepBody(root: string, step: NodeDto): string {
  const source = step.source;
  if (!source?.file) {
    return source?.text ?? '';
  }
  const full = join(root, source.file);
  if (!existsSync(full)) {
    return source.text ?? '';
  }
  let lines: string[];
  try {
    lines = readFileSync(full, 'utf8').split(/\r?\n/);
  } catch {
    return source.text ?? '';
  }
  const start = Math.max((source.start_line || 1) - 1, 0);
  let end = source.end_line || source.start_line || start + 1;
  if (end <= (source.start_line || 1)) {
    end = callbackEnd(lines, start);
  }
  return lines.slice(start, end).join('\n');
}

function callbackEnd(lines: string[], start: number): number {
  const text = lines.slice(start).join('\n');
  const openAt = text.indexOf('{');
  if (openAt < 0) {
    return start + 1;
  }
  let depth = 0;
  for (let index = openAt; index < text.length; index += 1) {
    const char = text[index];
    if (char === '{') {
      depth += 1;
    } else if (char === '}') {
      depth -= 1;
      if (depth === 0) {
        return start + text.slice(0, index + 1).split('\n').length;
      }
    }
  }
  return Math.min(start + 40, lines.length);
}

function attachClassMembers(dto: KnowledgeGraphDto, root: string) {
  const catalog = indexDefinitions(root).filter(
    (entry) => entry.semantic_type === 'Operation' || entry.semantic_type === 'Property',
  );
  for (const graph of dto.practice_graphs) {
    const classes = graph.nodes.filter(
      (node) =>
        isClassKind(node.semantic_type) &&
        node.source?.file &&
        node.source.start_line >= 1,
    );
    const owned = new Map<string, Set<string>>();
    for (const edge of graph.relationships) {
      if (edge.kind !== 'owns') {
        continue;
      }
      const child = graph.nodes.find((node) => node.node_id === edge.to_id);
      if (!child) {
        continue;
      }
      const names = owned.get(edge.from_id) ?? new Set<string>();
      names.add(`${child.semantic_type}:${child.name}`);
      owned.set(edge.from_id, names);
    }
    for (const member of catalog) {
      const file = member.source.file.replaceAll('\\', '/');
      const start = member.source.start_line;
      const end = member.source.end_line || start;
      if (
        member.semantic_type === 'Property' &&
        (isObjectLiteralKeyText(member.source.text ?? '') ||
          (insideOperation(catalog, file, start) &&
            !/^\s*(?:public|private|protected|readonly)\b/.test(member.source.text ?? '')))
      ) {
        continue;
      }
      const owner = smallestClass(classes, file, start, end);
      if (!owner) {
        continue;
      }
      const names = owned.get(owner.node_id) ?? new Set<string>();
      const key = `${member.semantic_type}:${member.name}`;
      if (names.has(key)) {
        continue;
      }
      const nodeId = `ce:${member.semantic_type}:${file}:${owner.name}:${member.name}`;
      if (graph.nodes.some((node) => node.node_id === nodeId)) {
        continue;
      }
      graph.nodes.push({
        node_id: nodeId,
        name: member.name,
        practice: 'clean_engineering',
        semantic_type: member.semantic_type,
        properties: {},
        applicable_rules: [],
        violations: [],
        source: member.source,
      });
      graph.relationships.push({ kind: 'owns', from_id: owner.node_id, to_id: nodeId });
      graph.relationships.push({ kind: 'belongsTo', from_id: nodeId, to_id: owner.node_id });
      names.add(key);
      owned.set(owner.node_id, names);
    }
  }
}

function insideOperation(catalog: SourceDefinition[], file: string, line: number): boolean {
  return catalog.some((entry) => {
    if (entry.semantic_type !== 'Operation') {
      return false;
    }
    const start = entry.source.start_line;
    const end = entry.source.end_line || start;
    return entry.source.file.replaceAll('\\', '/') === file && line >= start && line <= end;
  });
}

function smallestClass(classes: NodeDto[], file: string, start: number, end: number): NodeDto | null {
  let owner: NodeDto | null = null;
  let span = Number.POSITIVE_INFINITY;
  for (const cls of classes) {
    const clsFile = cls.source?.file.replaceAll('\\', '/') ?? '';
    const clsStart = cls.source?.start_line ?? 0;
    const clsEnd = cls.source?.end_line ?? clsStart;
    if (clsFile !== file || start < clsStart || end > clsEnd) {
      continue;
    }
    const size = clsEnd - clsStart;
    if (size < span) {
      span = size;
      owner = cls;
    }
  }
  return owner;
}

function fillSourceBodies(dto: KnowledgeGraphDto, root: string) {
  const catalog = indexDefinitions(root);
  const owners = ownership(dto);
  const files = new Map<string, string[] | null>();
  for (const graph of dto.practice_graphs) {
    for (const node of graph.nodes) {
      node.source = sourceForNode(root, node, catalog, owners, files);
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
      if (isClassKind(parent.semantic_type)) {
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

function sourceForNode(
  root: string,
  node: NodeDto,
  catalog: SourceDefinition[],
  owners: { moduleFolder: Map<string, string>; classOf: Map<string, string>; nodeById: Map<string, NodeDto> },
  files: Map<string, string[] | null>,
): SourceRangeDto | null {
  if (node.source?.file && node.source.start_line >= 1) {
    const span = readSpan(root, node.source, files);
    return node.semantic_type === 'Property' ? propertyExcerpt(node.name, span) : span;
  }
  if (
    node.semantic_type !== 'OoadClass' &&
    node.semantic_type !== 'Operation' &&
    node.semantic_type !== 'Property' &&
    !isClassKind(node.semantic_type)
  ) {
    return node.source;
  }
  const ownerClass = owners.classOf.get(node.node_id);
  const classFile = ownerClass
    ? owners.nodeById.get(ownerClass)?.source?.file ?? null
    : null;
  const hit = pickDefinition(
    catalog,
    node.semantic_type === 'Property' || node.semantic_type === 'Operation' || node.semantic_type === 'OoadClass'
      ? node.semantic_type
      : 'OoadClass',
    node.name,
    owners.moduleFolder.get(node.node_id) ?? '',
    classFile || node.source?.file || null,
    node.source?.start_line ?? 0,
  );
  if (hit) {
    const span = readSpan(root, hit.source, files);
    return node.semantic_type === 'Property' ? propertyExcerpt(node.name, span) : span;
  }
  return node.semantic_type === 'Property' && node.source
    ? propertyExcerpt(node.name, node.source)
    : node.source;
}

export function propertyExcerpt(name: string, source: SourceRangeDto): SourceRangeDto {
  const text = source.text ?? '';
  const lines = text.split('\n');
  if (lines.length <= 1 && !/constructor\s*\(/.test(text)) {
    return source;
  }
  const pattern = new RegExp(`\\b${name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`);
  const index = lines.findIndex(
    (row) =>
      pattern.test(row) &&
      !/^\s*(?:export\s+)?(?:abstract\s+)?class\b/.test(row) &&
      !/constructor\s*\(/.test(row),
  );
  if (index < 0) {
    return source;
  }
  const start = (source.start_line || 1) + index;
  return { ...source, start_line: start, end_line: start, text: lines[index] };
}

function pickDefinition(
  catalog: SourceDefinition[],
  kind: 'OoadClass' | 'Operation' | 'Property',
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

function readSpan(
  root: string,
  source: SourceRangeDto,
  files: Map<string, string[] | null>,
): SourceRangeDto {
  const file = source.file.replaceAll('\\', '/');
  let lines = files.get(file);
  if (lines === undefined) {
    const full = join(root, file);
    if (!existsSync(full)) {
      files.set(file, null);
      lines = null;
    } else {
      try {
        lines = readFileSync(full, 'utf8').split(/\r?\n/);
      } catch {
        lines = null;
      }
      files.set(file, lines);
    }
  }
  if (!lines) {
    return source;
  }
  const start = Math.max(source.start_line, 1);
  const end = Math.min(Math.max(source.end_line || start, start), lines.length);
  if (start > lines.length) {
    return source;
  }
  return {
    ...source,
    file,
    start_line: start,
    end_line: end,
    text: lines.slice(start - 1, end).join('\n'),
  };
}
