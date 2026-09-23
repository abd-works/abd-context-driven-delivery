/**
 * Build a KnowledgeGraph from a working folder's source text.
 * No filesystem — the server supplies file paths and contents.
 */
import {
  KEEP_OPERATIONS_SMALL_FOCUSED,
  KnowledgeGraph,
  type KnowledgeGraphDto,
  type NodeDto,
  type RelationshipDto,
} from './knowledge-graph';

export const MAX_OPERATION_LINES = 20;

export type WorkspaceFile = {
  relativePath: string;
  text: string;
};

export const SKIP_DIR = new Set([
  'node_modules',
  '.git',
  'dist',
  '__pycache__',
  '.venv',
  'coverage',
  '.codeql',
]);

const SOURCE_EXT = new Set(['.ts', '.tsx', '.js', '.jsx', '.py']);

export function scanSourceFiles(files: WorkspaceFile[]): WorkspaceFile[] {
  return files
    .filter((file) => isScanSourcePath(file.relativePath))
    .slice(0, 500);
}

export function isScanSourcePath(relativePath: string): boolean {
  const parts = relativePath.replaceAll('\\', '/').split('/');
  if (parts.some((part) => SKIP_DIR.has(part))) {
    return false;
  }
  const name = parts[parts.length - 1] ?? '';
  if (name.endsWith('.d.ts')) {
    return false;
  }
  const dot = name.lastIndexOf('.');
  return dot >= 0 && SOURCE_EXT.has(name.slice(dot));
}

export function pickerRelativePath(webkitRelativePath: string): {
  folder: string;
  relativePath: string;
} {
  const normalized = webkitRelativePath.replaceAll('\\', '/');
  const slash = normalized.indexOf('/');
  if (slash < 0) {
    return { folder: 'workspace', relativePath: normalized };
  }
  return {
    folder: normalized.slice(0, slash),
    relativePath: normalized.slice(slash + 1),
  };
}

const TS_SKIP = new Set([
  'if',
  'for',
  'while',
  'switch',
  'catch',
  'function',
  'else',
  'do',
  'return',
  'with',
  'constructor',
]);

export function knowledgeGraphFromWorkspace(
  folder: string,
  files: WorkspaceFile[],
  id: string,
): KnowledgeGraph {
  const nodes: NodeDto[] = [];
  const relationships: RelationshipDto[] = [];
  const folders = new Set<string>();

  for (const file of files) {
    const parent = _parentFolder(file.relativePath);
    if (parent) {
      folders.add(parent);
    }
    const fileNode = _fileNode(file);
    nodes.push(fileNode);
    if (parent) {
      relationships.push({
        kind: 'owns',
        from_id: _folderId(parent),
        to_id: fileNode.node_id,
      });
    }
    for (const operation of _operationsIn(file)) {
      nodes.push(operation);
      relationships.push({
        kind: 'owns',
        from_id: fileNode.node_id,
        to_id: operation.node_id,
      });
    }
  }

  for (const folderName of folders) {
    nodes.push(_folderNode(folderName));
  }

  const dto: KnowledgeGraphDto = {
    id,
    folder,
    practice_graphs: [
      {
        id: `practice:clean_engineering`,
        name: 'clean_engineering',
        nodes,
        relationships,
      },
    ],
  };
  return KnowledgeGraph.fromDto(dto);
}

function _folderId(relative: string): string {
  return `ce:Module:${relative.replaceAll('\\', '/')}`;
}

function _fileId(relative: string): string {
  return `ce:File:${relative.replaceAll('\\', '/')}`;
}

function _folderNode(relative: string): NodeDto {
  const name = relative.replaceAll('\\', '/').split('/').filter(Boolean).pop() ?? relative;
  return {
    node_id: _folderId(relative),
    name,
    practice: 'clean_engineering',
    semantic_type: 'Module',
    properties: { folder: relative.replaceAll('\\', '/') },
    applicable_rules: [],
    violations: [],
    source: null,
  };
}

function _fileNode(file: WorkspaceFile): NodeDto {
  const normalized = file.relativePath.replaceAll('\\', '/');
  const name = normalized.split('/').pop() ?? normalized;
  const lines = file.text.split('\n');
  return {
    node_id: _fileId(file.relativePath),
    name,
    practice: 'clean_engineering',
    semantic_type: 'Module',
    properties: { file: normalized },
    applicable_rules: [],
    violations: [],
    source: {
      file: normalized,
      start_line: 1,
      end_line: Math.max(1, lines.length),
      text: file.text,
    },
  };
}

function _parentFolder(relativePath: string): string | null {
  const normalized = relativePath.replaceAll('\\', '/');
  const cut = normalized.lastIndexOf('/');
  if (cut <= 0) {
    return null;
  }
  return normalized.slice(0, cut);
}

function _operationsIn(file: WorkspaceFile): NodeDto[] {
  if (file.relativePath.endsWith('.py')) {
    return _pythonOperations(file);
  }
  if (/\.(ts|tsx|js|jsx)$/.test(file.relativePath) && !file.relativePath.endsWith('.d.ts')) {
    return _scriptOperations(file);
  }
  return [];
}

function _scriptOperations(file: WorkspaceFile): NodeDto[] {
  const found: NodeDto[] = [];
  const pattern =
    /(?:(?:export|public|private|protected|static|async)\s+)*([A-Za-z_][A-Za-z0-9_]*)\s*\([^;{}]*\)\s*(?::[^{]+)?\{/g;
  let match: RegExpExecArray | null = pattern.exec(file.text);
  while (match) {
    const name = match[1];
    if (!TS_SKIP.has(name)) {
      const start = match.index;
      const end = _closingBrace(file.text, (match.index ?? 0) + match[0].length - 1);
      found.push(_operationNode(file, name, start, end));
    }
    match = pattern.exec(file.text);
  }
  return found;
}

function _pythonOperations(file: WorkspaceFile): NodeDto[] {
  const found: NodeDto[] = [];
  const lines = file.text.split('\n');
  for (let index = 0; index < lines.length; index += 1) {
    const matched = lines[index].match(/^(\s*)def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(/);
    if (!matched) {
      continue;
    }
    const indent = matched[1].length;
    let end = index;
    for (let next = index + 1; next < lines.length; next += 1) {
      const line = lines[next];
      if (line.trim() === '') {
        end = next;
        continue;
      }
      const nextIndent = line.match(/^\s*/)![0].length;
      if (nextIndent <= indent) {
        break;
      }
      end = next;
    }
    const startOffset = _offsetAtLine(file.text, index);
    const endOffset = _offsetAtLine(file.text, end) + lines[end].length;
    found.push(_operationNode(file, matched[2], startOffset, endOffset));
  }
  return found;
}

function _operationNode(
  file: WorkspaceFile,
  name: string,
  startOffset: number,
  endOffset: number,
): NodeDto {
  const startLine = _lineAt(file.text, startOffset);
  const endLine = _lineAt(file.text, endOffset);
  const lineCount = endLine - startLine + 1;
  const normalized = file.relativePath.replaceAll('\\', '/');
  const violating = lineCount > MAX_OPERATION_LINES;
  return {
    node_id: `ce:Operation:${normalized}:${name}`,
    name,
    practice: 'clean_engineering',
    semantic_type: 'Operation',
    properties: {},
    applicable_rules: [KEEP_OPERATIONS_SMALL_FOCUSED],
    violations: violating
      ? [
          {
            rule_slug: KEEP_OPERATIONS_SMALL_FOCUSED,
            message: `Operation '${name}' is ${lineCount} lines (max ${MAX_OPERATION_LINES}). Extract helpers.`,
            practice: 'clean_engineering',
            fidelity: 'code',
          },
        ]
      : [],
    source: {
      file: normalized,
      start_line: startLine,
      end_line: endLine,
      text: file.text.slice(startOffset, endOffset),
    },
  };
}

function _closingBrace(text: string, openIndex: number): number {
  let depth = 0;
  for (let index = openIndex; index < text.length; index += 1) {
    const ch = text[index];
    if (ch === '{') {
      depth += 1;
    } else if (ch === '}') {
      depth -= 1;
      if (depth === 0) {
        return index + 1;
      }
    }
  }
  return text.length;
}

function _lineAt(text: string, offset: number): number {
  return text.slice(0, Math.max(0, offset)).split('\n').length;
}

function _offsetAtLine(text: string, lineIndex: number): number {
  if (lineIndex <= 0) {
    return 0;
  }
  const parts = text.split('\n');
  let offset = 0;
  for (let index = 0; index < lineIndex && index < parts.length; index += 1) {
    offset += parts[index].length + 1;
  }
  return offset;
}
