const MAX_DEPTH = 5;

const SKIP_TYPES = new Set([
  "string",
  "number",
  "boolean",
  "unknown",
  "void",
  "any",
  "null",
  "undefined",
  "object",
  "never",
  "bigint",
  "symbol",
  "str",
  "int",
  "float",
  "bool",
  "None",
  "list",
  "dict",
  "self",
  "Promise",
  "Array",
  "Readonly",
  "Partial",
  "Record",
  "Map",
  "Set",
  "Date",
  "console",
  "Math",
  "JSON",
  "Object",
  "expect",
]);

const CLASS_KINDS = new Set([
  "OoadClass",
  "Entity",
  "EntityRoot",
  "ValueObject",
  "Aggregate",
]);

export type FoldNode = {
  nodeId: string;
  name: string;
  nodeType?: { name?: string } | null;
  source?: { text?: string; file?: string; startLine?: number; endLine?: number } | null;
  children?: FoldNode[];
};

export type FoldMember = {
  id: string;
  name: string;
  kind: string;
  owner: string;
  text: string;
  file: string;
  start: number;
  end: number;
  classes?: string[];
};

type ClassBody = { id: string; name: string; text: string };
type CallBody = { id: string; member: string; label: string; text: string; types: ClassBody[] };
type CallFold = { start: number; end: number; kind: "call" | "class" };

export type InlineFold = { start: number; end: number; kind: "call" | "class"; glyph: number };

export type InlineLayout = { text: string; folds: InlineFold[]; lineNumbers: string[] };

export function collectFoldMembers(nodes: FoldNode[]): FoldMember[] {
  const seen = new Map<string, FoldMember>();
  const visit = (node: FoldNode, owner: string, parentIsClass: boolean) => {
    const kind = node.nodeType?.name ?? "";
    const isClass = CLASS_KINDS.has(kind);
    if ((kind === "Operation" || kind === "Property" || isClass) && node.nodeId) {
      const existing = seen.get(node.nodeId);
      const realOwner = isClass ? "" : parentIsClass ? owner : (existing?.owner ?? "");
      if (!existing) {
        seen.set(node.nodeId, {
          id: node.nodeId,
          name: node.name,
          kind,
          owner: realOwner,
          text: node.source?.text ?? "",
          file: node.source?.file ?? "",
          start: Number(node.source?.startLine) || 0,
          end: Number(node.source?.endLine) || 0,
        });
      } else {
        if (parentIsClass && !isClass) {
          existing.owner = owner;
        }
        if (!existing.text && node.source?.text) {
          existing.text = node.source.text;
        }
        if (!existing.file && node.source?.file) {
          existing.file = node.source.file;
          existing.start = Number(node.source.startLine) || existing.start;
          existing.end = Number(node.source.endLine) || existing.end;
        }
      }
    }
    const nextOwner = isClass ? node.name : owner;
    for (const child of node.children ?? []) {
      visit(child, nextOwner, isClass);
    }
  };
  for (const node of nodes) {
    visit(node, "", false);
  }
  return [...seen.values()];
}

export function inlineCallLayout(
  text: string,
  members: FoldMember[],
  owner: string,
  options: { anchored?: FoldMember[]; listClasses?: boolean; named?: FoldMember[]; openedClass?: string } = {},
): InlineLayout {
  const classes = classCatalog(members);
  const bodies = callCatalog(members, classes, owner);
  const known = [...classes.values()];
  const anchored = (options.anchored ?? [])
    .map((member) => bodies.get(memberKey(member.owner || owner, member.name)) ?? bodiesByMember(bodies).get(member.name))
    .filter((body): body is CallBody => Boolean(body));
  const namedCalls: CallBody[] = [];
  const namedClasses: ClassBody[] = [];
  for (const member of options.named ?? []) {
    if (CLASS_KINDS.has(member.kind)) {
      const listed = classes.get(member.name);
      if (listed && !namedClasses.some((item) => item.id === listed.id)) {
        namedClasses.push(listed);
      }
      continue;
    }
    namedCalls.push({
      id: member.id,
      member: member.name,
      label: member.name,
      text: member.text || member.name,
      types: (member.classes ?? [])
        .map((name) => classes.get(name))
        .filter((item): item is ClassBody => Boolean(item)),
    });
  }
  const opened = options.openedClass ?? "";
  const layout = displayedCallSource(
    text,
    bodies,
    1,
    opened ? known.filter((type) => type.name === opened).map((type) => type.id) : [],
    known,
    anchored,
    options.listClasses ?? false,
    namedCalls,
    namedClasses,
  );
  return {
    text: layout.text,
    lineNumbers: layout.lineNumbers,
    folds: layout.folds
      .filter((fold) => fold.end > fold.start)
      .map((fold) => ({
        glyph: fold.start,
        start: fold.start + 1,
        end: fold.end,
        kind: fold.kind,
      })),
  };
}

export function signatureTypeNames(text: string): string[] {
  const head = text.split("{")[0] ?? "";
  const params = head.match(/\(([^)]*)\)/)?.[1] ?? "";
  const names: string[] = [];
  for (const part of params.split(",")) {
    if (!part.includes(":")) {
      continue;
    }
    names.push(...typeIdentifiers(part.slice(part.indexOf(":") + 1)));
  }
  names.push(...returnTypeNames(head));
  return names;
}

function returnTypeNames(text: string): string[] {
  const returned = text.match(/\)\s*(?::|->)\s*([\s\S]*)$/)?.[1] ?? "";
  return typeIdentifiers(returned);
}

function fieldTypeNames(text: string): string[] {
  return typeIdentifiers(text.split(":").slice(1).join(":"));
}

function typeIdentifiers(text: string): string[] {
  return text.match(/[A-Za-z_][A-Za-z0-9_]*/g) ?? [];
}

function classCatalog(members: FoldMember[]): Map<string, ClassBody> {
  const classes = new Map<string, ClassBody>();
  for (const member of members) {
    if (!CLASS_KINDS.has(member.kind) || !member.text || classes.has(member.name)) {
      continue;
    }
    classes.set(member.name, { id: member.id, name: member.name, text: member.text });
  }
  return classes;
}

function callCatalog(members: FoldMember[], classes: Map<string, ClassBody>, owner: string): Map<string, CallBody> {
  const bodies = new Map<string, CallBody>();
  const ordered = [...members].sort((left, right) => {
    const leftOwner = left.owner === owner ? 0 : 1;
    const rightOwner = right.owner === owner ? 0 : 1;
    return leftOwner - rightOwner;
  });
  for (const member of ordered) {
    if (member.kind !== "Operation" && member.kind !== "Property") {
      continue;
    }
    if (!member.text) {
      continue;
    }
    const key = memberKey(member.owner, member.name);
    const body: CallBody = {
      id: member.id,
      member: member.name,
      label: member.owner ? `${member.owner}.${member.name}` : member.name,
      text: member.text,
      types: typesIn(member.kind, member.text, classes),
    };
    if (!bodies.has(key)) {
      bodies.set(key, body);
    }
    if (!bodies.has(member.name)) {
      bodies.set(member.name, body);
    }
  }
  return bodies;
}

function bodiesByMember(bodies: Map<string, CallBody>): Map<string, CallBody> {
  const byName = new Map<string, CallBody>();
  for (const body of bodies.values()) {
    if (!byName.has(body.member)) {
      byName.set(body.member, body);
    }
  }
  return byName;
}

function memberKey(owner: string, name: string): string {
  return owner ? `${owner}.${name}` : name;
}

function typesIn(kind: string, text: string, classes: Map<string, ClassBody>): ClassBody[] {
  const wanted = kind === "Property" ? fieldTypeNames(text) : signatureTypeNames(text);
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
    types.push(match);
  }
  return types;
}

function displayedCallSource(
  text: string,
  bodies: Map<string, CallBody>,
  depth: number,
  stack: string[],
  known: ClassBody[],
  anchored: CallBody[],
  listClasses: boolean,
  namedCalls: CallBody[] = [],
  namedClasses: ClassBody[] = [],
): { text: string; folds: CallFold[]; lineNumbers: string[] } {
  const folds: CallFold[] = [];
  const lineNumbers: string[] = [];
  const output: string[] = [];
  text.split("\n").forEach((line, index) => {
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
    for (const call of namedCalls) {
      if (wordHas(line, call.member) && !calls.some((listed) => listed.id === call.id) && !stack.includes(call.id)) {
        calls.push(call);
      }
    }
    const fromCalls = typesOn(calls);
    const mentioned = known.filter(
      (type) =>
        !stack.includes(type.id) &&
        !fromCalls.some((listed) => listed.id === type.id) &&
        mentionsType(line, type.name),
    );
    for (const type of namedClasses) {
      if (wordHas(line, type.name) && !fromCalls.some((listed) => listed.id === type.id) && !mentioned.some((listed) => listed.id === type.id)) {
        mentioned.push(type);
      }
    }
    const listedIds = new Set([...fromCalls, ...mentioned].map((type) => type.id));
    const extras = index === 0 && listClasses ? known.filter((type) => !listedIds.has(type.id)) : [];
    if (calls.length === 0 && mentioned.length === 0 && extras.length === 0) {
      return;
    }
    const pad = `${indentOf(line)}    `;
    const callLine = output.length;
    for (const call of calls) {
      appendOperation(output, lineNumbers, folds, call, bodies, depth, stack, pad, known);
    }
    for (const type of [...fromCalls, ...mentioned, ...extras]) {
      appendClass(output, lineNumbers, folds, type, pad, stack);
    }
    if (output.length > callLine) {
      folds.push({ start: callLine, end: output.length, kind: calls.length > 0 ? "call" : "class" });
    }
  });
  return { text: output.join("\n"), folds, lineNumbers };
}

function wordHas(line: string, name: string): boolean {
  return new RegExp(`\\b${name}\\b`).test(line);
}

function callsOnLine(line: string, bodies: Map<string, CallBody>, stack: string[]): CallBody[] {
  const found: CallBody[] = [];
  const seen = new Set<string>();
  const add = (body: CallBody | undefined) => {
    if (!body || stack.includes(body.id) || seen.has(body.id)) {
      return;
    }
    seen.add(body.id);
    found.push(body);
  };
  const pattern = /\b([A-Za-z_][A-Za-z0-9_]*)\??\.([A-Za-z_][A-Za-z0-9_]*)\b/g;
  let match: RegExpExecArray | null;
  while ((match = pattern.exec(line))) {
    if (!SKIP_TYPES.has(match[1])) {
      add(resolveCall(bodies, match[1], match[2]));
    }
    const next = match.index + match[1].length + (match[0].includes("?.") ? 2 : 1);
    if (pattern.lastIndex > next) {
      pattern.lastIndex = next;
    }
  }
  return found;
}

function resolveCall(bodies: Map<string, CallBody>, receiver: string, method: string): CallBody | undefined {
  if (receiver !== "this") {
    const exact = bodies.get(`${receiver}.${method}`);
    if (exact) {
      return exact;
    }
    const wanted = receiver.toLowerCase();
    for (const [key, body] of bodies) {
      const dot = key.lastIndexOf(".");
      if (dot < 0 || key.slice(dot + 1) !== method) {
        continue;
      }
      if (key.slice(0, dot).toLowerCase() === wanted) {
        return body;
      }
    }
  }
  return bodies.get(method);
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
  const nested = displayedCallSource(call.text, bodies, depth + 1, [...stack, call.id], known, [], false);
  const nestedLines = nested.text.split("\n");
  output.push(nestedLines[0].length > 0 ? `${pad}${nestedLines[0]}` : pad);
  lineNumbers.push("");
  const operationLine = output.length;
  for (const nestedLine of nestedLines.slice(1)) {
    output.push(nestedLine.length > 0 ? `${pad}${nestedLine}` : pad);
    lineNumbers.push("");
  }
  if (output.length > operationLine) {
    folds.push({ start: operationLine, end: output.length, kind: "call" });
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
  stack: string[],
) {
  if (stack.includes(type.id)) {
    return;
  }
  output.push(`${pad}${type.name}`);
  lineNumbers.push("");
  const classLine = output.length;
  const classLines = type.text.split("\n");
  if (classLines.length === 0 || (classLines.length === 1 && classLines[0].trim() === type.name)) {
    return;
  }
  const classPad = `${pad}    `;
  for (const classLineText of classLines) {
    output.push(classLineText.length > 0 ? `${classPad}${classLineText}` : classPad);
    lineNumbers.push("");
  }
  folds.push({ start: classLine, end: output.length, kind: "class" });
}

function mentionsType(line: string, name: string): boolean {
  if (SKIP_TYPES.has(name)) {
    return false;
  }
  const code = line.replace(/'(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*"|`(?:\\.|[^`\\])*`/g, " ");
  return new RegExp(`\\b${name}\\b`).test(code);
}

function typesOn(calls: CallBody[]): ClassBody[] {
  const types: ClassBody[] = [];
  const seen = new Set<string>();
  for (const call of calls) {
    for (const type of call.types) {
      if (seen.has(type.id)) {
        continue;
      }
      seen.add(type.id);
      types.push(type);
    }
  }
  return types;
}

function indentOf(line: string): string {
  return line.match(/^\s*/)?.[0] ?? "";
}
