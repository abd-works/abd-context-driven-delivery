import {
  fieldTypeNames,
  isClassKind,
  isSimpleProperty,
  signatureTypeNames,
  SKIP_TYPES,
  type ListedTreeNode,
} from './knowledge-graph/knowledge-graph';

const CALL = /\b([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\b/g;
const MAX_DEPTH = 5;

export type ClassBody = {
  id: string;
  name: string;
  text: string;
};

export type CallBody = {
  id: string;
  member: string;
  label: string;
  text: string;
  types?: ClassBody[];
};

export type CallFold = {
  start: number;
  end: number;
  kind: 'call' | 'class';
};

export type CallLayout = {
  text: string;
  folds: CallFold[];
  lineNumbers: string[];
};

export function callBodiesIn(node: ListedTreeNode): Map<string, CallBody> {
  const bodies = new Map<string, CallBody>();
  const visit = (current: ListedTreeNode) => {
    for (const child of current.children) {
      const text = child.source?.text ?? '';
      const callable =
        child.semantic_type === 'Operation' ||
        (child.semantic_type === 'Property' && !isSimpleProperty(text));
      if (callable && text) {
        const member = memberName(child.name);
        if (!bodies.has(member)) {
          bodies.set(member, {
            id: child.node_id,
            member,
            label: child.name,
            text,
            types: classTypes(child, text),
          });
        }
      }
      visit(child);
    }
  };
  visit(node);
  return bodies;
}

export function classBodiesIn(node: ListedTreeNode): ClassBody[] {
  const found: ClassBody[] = [];
  const seen = new Set<string>();
  const visit = (current: ListedTreeNode) => {
    const text = current.source?.text ?? '';
    if (isClassKind(current.semantic_type) && text && !seen.has(current.node_id)) {
      seen.add(current.node_id);
      found.push({ id: current.node_id, name: current.name, text });
    }
    for (const child of current.children) {
      visit(child);
    }
  };
  visit(node);
  return found;
}

export function directCallsIn(node: ListedTreeNode): CallBody[] {
  const byId = new Map([...callBodiesIn(node).values()].map((body) => [body.id, body]));
  return node.children.flatMap((child) => {
    const body = byId.get(child.node_id);
    return body ? [body] : [];
  });
}

export function displayedCallSource(
  text: string,
  bodies: Map<string, CallBody>,
  depth = 1,
  stack: string[] = [],
  known: ClassBody[] = [],
  anchored: CallBody[] = [],
  listClasses = false,
): CallLayout {
  const folds: CallFold[] = [];
  const lineNumbers: string[] = [];
  const output: string[] = [];
  text.split('\n').forEach((line, index) => {
    output.push(line);
    lineNumbers.push(String(index + 1));
    if (depth >= MAX_DEPTH) {
      return;
    }
    const calls = callsOnLine(line, bodies, stack);
    if (index === 0) {
      for (const call of anchored) {
        if (!calls.some((listed) => listed.id === call.id)) {
          calls.push(call);
        }
      }
    }
    const fromCalls = typesOn(calls);
    const mentioned = known.filter(
      (type) =>
        !fromCalls.some((listed) => listed.id === type.id) && mentionsType(line, type.name),
    );
    const listedIds = new Set([...fromCalls, ...mentioned].map((type) => type.id));
    const extras =
      index === 0 && listClasses ? known.filter((type) => !listedIds.has(type.id)) : [];
    if (calls.length === 0 && mentioned.length === 0 && extras.length === 0) {
      return;
    }
    const pad = `${indentOf(line)}    `;
    const callLine = output.length;
    for (const call of calls) {
      appendOperation(output, lineNumbers, folds, call, bodies, depth, stack, pad, known);
    }
    for (const type of [...fromCalls, ...mentioned, ...extras]) {
      appendClass(output, lineNumbers, folds, type, pad);
    }
    if (output.length > callLine) {
      folds.push({ start: callLine, end: output.length, kind: 'call' });
    }
  });
  return { text: output.join('\n'), folds, lineNumbers };
}

export function visibleLineCount(layout: CallLayout, open: Set<number> = new Set()): number {
  const total = Math.max(layout.text.split('\n').length, 1);
  const hidden = new Set<number>();
  for (const fold of layout.folds) {
    if (open.has(fold.start)) {
      continue;
    }
    for (let line = fold.start + 1; line <= fold.end; line += 1) {
      hidden.add(line);
    }
  }
  return Math.max(total - hidden.size, 1);
}

function callsOnLine(
  line: string,
  bodies: Map<string, CallBody>,
  stack: string[],
): CallBody[] {
  const found: CallBody[] = [];
  const seen = new Set<string>();
  for (const match of line.matchAll(CALL)) {
    if (SKIP_TYPES.has(match[1])) {
      continue;
    }
    const body = bodies.get(match[2]);
    if (!body || stack.includes(body.id) || seen.has(body.id)) {
      continue;
    }
    seen.add(body.id);
    found.push(body);
  }
  return found;
}

function appendOperation(
  output: string[],
  lineNumbers: string[],
  folds: CallFold[],
  call: CallBody,
  bodies: Map<string, CallBody>,
  depth: number,
  stack: string[],
  pad: string,
  known: ClassBody[],
) {
  const nested = displayedCallSource(call.text, bodies, depth + 1, [...stack, call.id], known);
  const nestedLines = nested.text.split('\n');
  output.push(nestedLines[0].length > 0 ? `${pad}${nestedLines[0]}` : pad);
  lineNumbers.push('');
  const operationLine = output.length;
  for (const nestedLine of nestedLines.slice(1)) {
    output.push(nestedLine.length > 0 ? `${pad}${nestedLine}` : pad);
    lineNumbers.push('');
  }
  if (output.length > operationLine) {
    folds.push({ start: operationLine, end: output.length, kind: 'call' });
  }
  for (const fold of nested.folds) {
    if (fold.start === 1) {
      continue;
    }
    folds.push({
      start: operationLine + fold.start - 1,
      end: operationLine + fold.end - 1,
      kind: fold.kind,
    });
  }
}

function appendClass(
  output: string[],
  lineNumbers: string[],
  folds: CallFold[],
  type: ClassBody,
  pad: string,
) {
  output.push(`${pad}${type.name}`);
  lineNumbers.push('');
  const classLine = output.length;
  const classLines = type.text.split('\n');
  if (classLines.length === 0 || (classLines.length === 1 && classLines[0].trim() === type.name)) {
    return;
  }
  const classPad = `${pad}    `;
  for (const classLine of classLines) {
    output.push(classLine.length > 0 ? `${classPad}${classLine}` : classPad);
    lineNumbers.push('');
  }
  folds.push({ start: classLine, end: output.length, kind: 'class' });
}

function mentionsType(line: string, name: string): boolean {
  if (SKIP_TYPES.has(name)) {
    return false;
  }
  const names = new Set([...signatureTypeNames(line), ...fieldTypeNames(line)]);
  return names.has(name);
}

function typesOn(calls: CallBody[]): ClassBody[] {
  const types: ClassBody[] = [];
  const seen = new Set<string>();
  for (const call of calls) {
    for (const type of call.types ?? []) {
      if (seen.has(type.id)) {
        continue;
      }
      seen.add(type.id);
      types.push(type);
    }
  }
  return types;
}

function classTypes(node: ListedTreeNode, text: string): ClassBody[] {
  const wanted =
    node.semantic_type === 'Property' ? fieldTypeNames(text) : signatureTypeNames(text);
  const classes = new Map(
    node.children
      .filter((child) => isClassKind(child.semantic_type))
      .map((child) => [child.name, child]),
  );
  const types: ClassBody[] = [];
  const seen = new Set<string>();
  for (const name of wanted) {
    if (SKIP_TYPES.has(name) || seen.has(name)) {
      continue;
    }
    const match = classes.get(name);
    if (!match) {
      continue;
    }
    seen.add(name);
    types.push({
      id: match.node_id,
      name: match.name,
      text: match.source?.text ?? '',
    });
  }
  return types;
}

function memberName(name: string): string {
  const dot = name.lastIndexOf('.');
  return dot >= 0 ? name.slice(dot + 1) : name;
}

function indentOf(line: string): string {
  return line.match(/^\s*/)?.[0] ?? '';
}
